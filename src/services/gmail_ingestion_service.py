import asyncio
import base64
import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from email.utils import parseaddr
from pathlib import Path
from typing import Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2 import credentials as oauth_credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from controllers.InterviewController import InterviewController
from models.ProcessedEmailModel import ProcessedEmailModel
from models.db_schemes import ProcessedEmail

logger = logging.getLogger(__name__)


@dataclass
class GmailMessage:
    message_id: str
    subject: str
    body: str
    from_email: str


class GmailIngestionService:
    """Poll Gmail for unread interview invitation emails and trigger workflows."""

    SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
    TOKEN_FILE = "gmail_ingestion_token.json"
    INVITATION_KEYWORDS = (
        "interview",
        "technical interview",
        "hr interview",
        "screening",
        "candidate",
        "hiring",
        "recruiter",
        "schedule",
        "meeting",
    )

    def __init__(self, db_client: object, settings):
        self.db_client = db_client
        self.settings = settings
        self.poll_interval_seconds = max(5, int(settings.GMAIL_POLL_INTERVAL_SECONDS or 30))
        self.label_filter = settings.GMAIL_LABEL_FILTER or "INBOX"
        self.query = settings.GMAIL_QUERY or "is:unread"
        self.service = None
        self.credentials = None
        self.last_poll_at: Optional[datetime] = None
        self.last_error: Optional[str] = None
        self.total_processed = 0
        self.total_triggered = 0
        self.enabled = bool(settings.GMAIL_INGESTION_ENABLED)

        if self.enabled:
            self._authenticate()

    def _client_secrets_file(self) -> Path:
        configured = self.settings.GMAIL_CLIENT_SECRETS_FILE or self.settings.GOOGLE_CALENDAR_CLIENT_SECRETS_FILE
        if not configured:
            raise ValueError("GMAIL_CLIENT_SECRETS_FILE or GOOGLE_CALENDAR_CLIENT_SECRETS_FILE must be configured")
        path = Path(configured)
        if not path.exists():
            raise FileNotFoundError(f"Gmail client secrets file not found: {path}")
        return path

    def _token_path(self) -> Path:
        configured = self.settings.GMAIL_TOKEN_STORAGE_PATH
        if configured:
            path = Path(configured)
            if path.suffix.lower() == ".json":
                return path
            return path / self.TOKEN_FILE
        return Path(__file__).resolve().parents[2] / self.TOKEN_FILE

    def _authenticate(self) -> None:
        token_path = self._token_path()
        token_path.parent.mkdir(parents=True, exist_ok=True)

        if token_path.exists():
            logger.info("Loading cached Gmail OAuth token from %s", token_path)
            self.credentials = oauth_credentials.Credentials.from_authorized_user_file(
                str(token_path),
                scopes=self.SCOPES,
            )
        else:
            logger.info("No cached Gmail token found, initiating OAuth flow")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self._client_secrets_file()),
                scopes=self.SCOPES,
            )
            self.credentials = flow.run_local_server(
                port=0,
                open_browser=False,
                authorization_prompt_message=(
                    "Please visit this URL in your browser to authorize Gmail ingestion:\n{url}\n"
                ),
            )
            self._save_token(token_path)

        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            logger.info("Refreshing expired Gmail OAuth token")
            self.credentials.refresh(Request())
            self._save_token(token_path)

        self.service = build("gmail", "v1", credentials=self.credentials)
        logger.info("GmailIngestionService authenticated successfully")

    def _save_token(self, token_path: Path) -> None:
        if not self.credentials:
            return
        token_data = {
            "token": self.credentials.token,
            "refresh_token": self.credentials.refresh_token,
            "token_uri": self.credentials.token_uri,
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret,
            "scopes": self.credentials.scopes,
        }
        with open(token_path, "w") as token_file:
            json.dump(token_data, token_file, indent=2)
        logger.info("Gmail OAuth token saved to %s", token_path)

    async def poll_forever(self) -> None:
        logger.info("Gmail inbox polling started with interval=%s seconds", self.poll_interval_seconds)
        while True:
            try:
                await self.poll_once()
            except asyncio.CancelledError:
                logger.info("Gmail inbox polling stopped")
                raise
            except Exception as exc:
                self.last_error = str(exc)
                logger.error("Gmail inbox polling failed: %s", exc)

            await asyncio.sleep(self.poll_interval_seconds)

    async def poll_once(self) -> Dict[str, int]:
        if not self.enabled:
            return {"unread": 0, "detected": 0, "triggered": 0, "processed": 0}
        if self.service is None:
            self._authenticate()

        logger.info("Checking inbox...")
        self.last_poll_at = datetime.utcnow()

        processed_model = await ProcessedEmailModel.create_instance(db_client=self.db_client)
        messages = self._list_unread_messages()
        stats = {"unread": len(messages), "detected": 0, "triggered": 0, "processed": 0}

        for message_ref in messages:
            message_id = message_ref.get("id")
            if not message_id:
                continue

            logger.info("Found unread email: message_id=%s", message_id)
            if await processed_model.is_processed(message_id):
                self._mark_as_read(message_id)
                continue

            gmail_message = self._get_message(message_id)
            if not self._is_interview_invitation(gmail_message):
                continue

            stats["detected"] += 1
            logger.info("Interview invitation detected: message_id=%s subject=%s", message_id, gmail_message.subject)

            controller = InterviewController(db_client=self.db_client, settings=self.settings)
            state = await controller.trigger_interview(
                subject=gmail_message.subject,
                body=gmail_message.body,
                from_email=gmail_message.from_email,
                candidate_email=gmail_message.from_email,
            )

            stats["triggered"] += 1
            self.total_triggered += 1
            logger.info("Workflow triggered: message_id=%s interview_id=%s", message_id, state.interview_id)

            await processed_model.mark_processed(
                ProcessedEmail(
                    message_id=message_id,
                    interview_id=state.interview_id,
                    from_email=gmail_message.from_email,
                    subject=gmail_message.subject,
                )
            )
            stats["processed"] += 1
            self.total_processed += 1
            logger.info("Email marked as processed: message_id=%s", message_id)

            self._mark_as_read(message_id)

        return stats

    def _list_unread_messages(self) -> List[Dict]:
        try:
            result = (
                self.service.users()
                .messages()
                .list(
                    userId="me",
                    labelIds=[self.label_filter, "UNREAD"],
                    q=self.query,
                    maxResults=10,
                )
                .execute()
            )
            return result.get("messages", [])
        except HttpError as exc:
            logger.error("Failed to list Gmail messages: %s", exc)
            raise

    def _get_message(self, message_id: str) -> GmailMessage:
        raw_message = (
            self.service.users()
            .messages()
            .get(userId="me", id=message_id, format="full")
            .execute()
        )
        payload = raw_message.get("payload", {})
        headers = {header.get("name", "").lower(): header.get("value", "") for header in payload.get("headers", [])}
        subject = headers.get("subject", "(no subject)")
        _, from_email = parseaddr(headers.get("from", ""))
        body = self._extract_body(payload)

        return GmailMessage(
            message_id=message_id,
            subject=subject,
            body=body,
            from_email=from_email,
        )

    def _extract_body(self, payload: Dict) -> str:
        plain_parts: List[str] = []
        html_parts: List[str] = []

        def walk(part: Dict) -> None:
            mime_type = part.get("mimeType", "")
            data = part.get("body", {}).get("data")
            if data:
                decoded = self._decode_body(data)
                if mime_type == "text/plain":
                    plain_parts.append(decoded)
                elif mime_type == "text/html":
                    html_parts.append(decoded)

            for child in part.get("parts", []) or []:
                walk(child)

        walk(payload)

        if plain_parts:
            return "\n".join(part.strip() for part in plain_parts if part.strip())
        return self._strip_html("\n".join(part.strip() for part in html_parts if part.strip()))

    def _decode_body(self, data: str) -> str:
        padded = data + "=" * (-len(data) % 4)
        return base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8", errors="replace")

    def _strip_html(self, html: str) -> str:
        text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
        text = re.sub(r"</p\s*>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def _is_interview_invitation(self, message: GmailMessage) -> bool:
        text = f"{message.subject}\n{message.body}".lower()
        return "interview" in text and any(keyword in text for keyword in self.INVITATION_KEYWORDS)

    def _mark_as_read(self, message_id: str) -> None:
        self.service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"removeLabelIds": ["UNREAD"]},
        ).execute()

    async def status(self) -> Dict:
        processed_model = await ProcessedEmailModel.create_instance(db_client=self.db_client)
        return {
            "enabled": self.enabled,
            "poll_interval_seconds": self.poll_interval_seconds,
            "label_filter": self.label_filter,
            "query": self.query,
            "last_poll_at": self.last_poll_at,
            "last_error": self.last_error,
            "total_processed": self.total_processed,
            "total_triggered": self.total_triggered,
            "processed_messages_in_db": await processed_model.count_processed(),
        }
