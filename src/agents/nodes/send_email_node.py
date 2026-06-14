import logging
from datetime import datetime
from html import escape

from models.enums.InterviewStatusEnum import InterviewStatusEnum
from services.email_service import EmailService
from ..interview_state import InterviewState

logger = logging.getLogger(__name__)


class SendEmailNode:
    """Send the interview report to the candidate via Gmail SMTP."""

    name = "send_email"

    def __init__(self, settings):
        self.settings = settings
        self.email_service = None

        smtp_user = self.settings.EMAIL_SMTP_USERNAME
        smtp_pass = self.settings.EMAIL_SMTP_PASSWORD

        logger.info(
            "[SendEmailNode] init: SMTP_USERNAME=%s, SMTP_PASSWORD=%s, SMTP_HOST=%s, SMTP_PORT=%s",
            smtp_user or "(NOT SET)",
            "***SET***" if smtp_pass else "(NOT SET)",
            self.settings.EMAIL_SMTP_HOST or "(default)",
            self.settings.EMAIL_SMTP_PORT,
        )

        if smtp_user and smtp_pass:
            try:
                self.email_service = EmailService(
                    smtp_host=self.settings.EMAIL_SMTP_HOST or EmailService.GMAIL_SMTP_HOST,
                    smtp_port=self.settings.EMAIL_SMTP_PORT,
                    smtp_username=smtp_user,
                    smtp_password=smtp_pass,
                    from_address=self.settings.EMAIL_FROM_ADDRESS or smtp_user,
                )
                logger.info("[SendEmailNode] EmailService initialized successfully.")
            except Exception as exc:
                logger.error("[SendEmailNode] FAILED to initialize EmailService: %s", exc, exc_info=True)
                self.email_service = None
        else:
            logger.warning(
                "[SendEmailNode] SMTP credentials missing. EMAIL_SMTP_USERNAME=%s, EMAIL_SMTP_PASSWORD=%s",
                "set" if smtp_user else "MISSING",
                "set" if smtp_pass else "MISSING",
            )

    def execute(self, state: InterviewState) -> InterviewState:
        """Send interview report to the candidate."""
        state.status = InterviewStatusEnum.SEND_EMAIL_REPORT.value

        logger.info(
            "[SendEmailNode] execute called: interview_id=%s, candidate_email=%s, from_email=%s, email_service=%s",
            state.interview_id,
            state.candidate_email,
            state.from_email,
            "AVAILABLE" if self.email_service else "NOT AVAILABLE",
        )

        try:
            recipient = state.candidate_email or state.from_email

            if not recipient:
                logger.error("[SendEmailNode] No recipient email found! candidate_email=%s, from_email=%s",
                             state.candidate_email, state.from_email)
                state.email_sent = False
                state.email_sent_at = None
                state.status = InterviewStatusEnum.FAILED.value
                state.last_error = "send_email failed: No recipient email address available."
                return state

            if not self.email_service:
                logger.error(
                    "[SendEmailNode] EmailService is NOT available! Cannot send email for interview_id=%s. "
                    "Check SMTP credentials in .env (EMAIL_SMTP_USERNAME, EMAIL_SMTP_PASSWORD).",
                    state.interview_id,
                )
                state.email_sent = False
                state.email_sent_at = None
                state.status = InterviewStatusEnum.FAILED.value
                state.last_error = (
                    "send_email failed: EmailService is not configured. "
                    "Set EMAIL_SMTP_USERNAME and EMAIL_SMTP_PASSWORD in .env."
                )
                return state

            subject = self._build_subject(state)
            body = self._build_body(state)
            html_body = self._build_html_body(state)

            logger.info(
                "[SendEmailNode] Attempting to send email: interview_id=%s, recipient=%s, subject=%s",
                state.interview_id,
                recipient,
                subject,
            )

            success = self.email_service.send(
                to_address=str(recipient),
                subject=subject,
                body=body,
                html_body=html_body,
            )

            if success:
                state.email_sent = True
                state.email_sent_at = datetime.utcnow()
                state.status = InterviewStatusEnum.COMPLETED.value
                logger.info(
                    "[SendEmailNode] ✅ Email sent SUCCESSFULLY: interview_id=%s, recipient=%s",
                    state.interview_id,
                    recipient,
                )
            else:
                state.email_sent = False
                state.email_sent_at = None
                state.status = InterviewStatusEnum.FAILED.value
                state.last_error = f"send_email failed: EmailService.send() returned False for recipient={recipient}"
                logger.error(
                    "[SendEmailNode] ❌ Email send FAILED (returned False): interview_id=%s, recipient=%s",
                    state.interview_id,
                    recipient,
                )

        except Exception as exc:
            state.status = InterviewStatusEnum.FAILED.value
            state.last_error = f"{self.name} failed: {exc}"
            state.email_sent = False
            state.email_sent_at = None
            logger.error(
                "[SendEmailNode] ❌ EXCEPTION during email send: interview_id=%s, error=%s",
                state.interview_id,
                exc,
                exc_info=True,
            )

        return state

    def _build_subject(self, state: InterviewState) -> str:
        return f"Interview Report: {state.decision} - {state.candidate_name or 'Candidate'}"

    def _build_body(self, state: InterviewState) -> str:
        report = state.report or {}

        lines = [
            f"Interview Report for {state.candidate_name or 'Candidate'}",
            "=" * 60,
            "",
            f"Interview ID: {state.interview_id}",
            f"Interview Date: {state.interview_datetime.strftime('%Y-%m-%d %H:%M') if state.interview_datetime else 'N/A'}",
            "",
            "RESULTS",
            "-" * 60,
            f"Overall Score: {report.get('overall_score', 'N/A')}/10",
            f"Decision: {state.decision}",
            "",
            "STRENGTHS",
            "-" * 60,
        ]

        for strength in report.get("strengths", []):
            lines.append(f"- {strength}")

        lines.extend([
            "",
            "AREAS FOR IMPROVEMENT",
            "-" * 60,
        ])

        for weakness in report.get("weaknesses", []):
            lines.append(f"- {weakness}")

        lines.extend([
            "",
            "SUMMARY",
            "-" * 60,
            report.get("summary", "Interview completed."),
            "",
            "Best regards,",
            "The Interview Team",
        ])

        return "\n".join(lines)

    def _build_html_body(self, state: InterviewState) -> str:
        report = state.report or {}
        decision_colors = {"Strong Hire": "#2e7d32", "Hire": "#388e3c", "Hold": "#f57c00", "Reject": "#c62828"}
        decision_color = decision_colors.get(state.decision, "#757575")

        strengths_html = "".join(f"<li>{escape(str(strength))}</li>" for strength in report.get("strengths", []))
        weaknesses_html = "".join(f"<li>{escape(str(weakness))}</li>" for weakness in report.get("weaknesses", []))
        candidate_name = escape(state.candidate_name or "Candidate")
        decision = escape(state.decision or "N/A")
        score = escape(str(report.get("overall_score", "N/A")))
        summary = escape(str(report.get("summary", "Interview completed.")))

        return f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Interview Report</h2>
                <p>Dear {candidate_name},</p>

                <p>Thank you for participating in our interview process. Here is your interview report:</p>

                <h3>Results</h3>
                <ul>
                    <li><strong>Overall Score:</strong> {score}/10</li>
                    <li><strong>Decision:</strong> <span style="color: {decision_color}; font-weight: bold;">{decision}</span></li>
                </ul>

                <h3>Strengths</h3>
                <ul>
                    {strengths_html}
                </ul>

                <h3>Areas for Improvement</h3>
                <ul>
                    {weaknesses_html}
                </ul>

                <h3>Summary</h3>
                <p>{summary}</p>

                <hr>
                <p>Best regards,<br>The Interview Team</p>
            </body>
        </html>
        """
