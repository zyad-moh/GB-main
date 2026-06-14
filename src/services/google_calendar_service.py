"""
Google Calendar Service with OAuth 2.0 Authentication
Handles authentication, token management, and calendar operations
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.oauth2 import credentials as oauth_credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    """
    Service for managing Google Calendar operations with OAuth 2.0
    Supports token caching for repeated authentication
    """

    # Google Calendar API scope
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    TOKEN_FILE = "google_calendar_token.json"
    
    def __init__(self, client_secrets_file: str, calendar_id: str = "primary", token_storage_path: Optional[str] = None):
        """
        Initialize GoogleCalendarService
        
        Args:
            client_secrets_file: Path to downloaded OAuth 2.0 client secret JSON file
            calendar_id: Google Calendar ID (default: "primary" for main calendar)
            token_storage_path: Path to store OAuth tokens (default: project root)
        
        Raises:
            ValueError: If client_secrets_file is not provided or invalid
            FileNotFoundError: If client_secrets_file doesn't exist
        """
        if not client_secrets_file or not isinstance(client_secrets_file, str):
            raise ValueError("GOOGLE_CALENDAR_CLIENT_SECRETS_FILE must be configured and point to a valid file path.")

        self.client_secrets_file = Path(client_secrets_file)
        self.calendar_id = calendar_id
        
        # Determine token storage path
        if token_storage_path is None:
            self.token_storage_path = Path(__file__).resolve().parents[2] / self.TOKEN_FILE
        else:
            self.token_storage_path = Path(token_storage_path) / self.TOKEN_FILE
        
        # Validate client secrets file
        if not self.client_secrets_file.exists():
            raise FileNotFoundError(f"Client secrets file not found: {self.client_secrets_file}")
        
        try:
            with open(self.client_secrets_file, 'r') as f:
                secrets = json.load(f)
                if 'installed' not in secrets and 'web' not in secrets:
                    raise ValueError("Invalid OAuth 2.0 credentials file")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in client secrets file: {self.client_secrets_file}")
        
        self.service = None
        self.credentials = None
        self._authenticate()
        
        logger.info(f"GoogleCalendarService initialized with calendar_id: {calendar_id}")

    def _authenticate(self) -> None:
        """
        Authenticate with Google Calendar API
        Uses cached token if available, otherwise initiates OAuth flow
        """
        try:
            # Try to load cached token
            if os.path.exists(self.token_storage_path):
                logger.info(f"Loading cached OAuth token from {self.token_storage_path}")
                self.credentials = oauth_credentials.Credentials.from_authorized_user_file(
                    str(self.token_storage_path),
                    scopes=self.SCOPES
                )
            else:
                logger.info("No cached token found, initiating OAuth flow")
                self.credentials = self._run_oauth_flow()
            
            # Refresh if needed
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                logger.info("Refreshing expired OAuth token")
                self.credentials.refresh(Request())
                self._save_token()
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=self.credentials)
            logger.info("Successfully authenticated with Google Calendar API")
        
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise

    def _run_oauth_flow(self) -> oauth_credentials.Credentials:
        """
        Run OAuth 2.0 authorization flow
        User must authorize access through browser
        
        Returns:
            Credentials object with access token
        """
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.client_secrets_file,
                scopes=self.SCOPES
            )
            
            # Use browserless flow if the environment cannot open a GUI browser.
            # The user will need to open the printed URL manually.
            credentials = flow.run_local_server(
                port=0,
                open_browser=False,
                authorization_prompt_message=(
                    "Please visit this URL in your browser to authorize the application:\n{url}\n"
                )
            )
            
            # Save token for future use
            self._save_token(credentials)
            logger.info("OAuth flow completed successfully")
            return credentials
        
        except Exception as e:
            logger.error(f"OAuth flow failed: {str(e)}")
            raise

    def _save_token(self, credentials: Optional[oauth_credentials.Credentials] = None) -> None:
        """Save OAuth credentials to file"""
        try:
            creds = credentials or self.credentials
            if creds:
                token_data = {
                    'token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'token_uri': creds.token_uri,
                    'client_id': creds.client_id,
                    'client_secret': creds.client_secret,
                    'scopes': creds.scopes
                }
                with open(self.token_storage_path, 'w') as f:
                    json.dump(token_data, f, indent=2)
                logger.info(f"Token saved to {self.token_storage_path}")
        except Exception as e:
            logger.error(f"Failed to save token: {str(e)}")

    def create_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: str = "",
        attendees: Optional[List[str]] = None,
        location: str = "",
        meeting_link: Optional[str] = None
    ) -> Dict:
        """
        Create a calendar event
        
        Args:
            title: Event title
            start_time: Event start datetime
            end_time: Event end datetime
            description: Event description
            attendees: List of attendee email addresses
            location: Event location
            meeting_link: Optional external meeting link
        
        Returns:
            Dictionary with event details (id, htmlLink, start, end)
        
        Raises:
            ValueError: If start_time is after end_time
            HttpError: If Google Calendar API request fails
        """
        if start_time >= end_time:
            raise ValueError("start_time must be before end_time")
        
        try:
            # Build event body
            event_body = {
                'summary': title,
                'description': description or '',
                'start': {
                    'dateTime': start_time.isoformat() + 'Z' if start_time.tzinfo else start_time.isoformat(),
                    'timeZone': 'UTC'
                },
                'end': {
                    'dateTime': end_time.isoformat() + 'Z' if end_time.tzinfo else end_time.isoformat(),
                    'timeZone': 'UTC'
                }
            }
            
            # Add location if provided
            if location:
                event_body['location'] = location
            
            # Add attendees if provided
            if attendees:
                event_body['attendees'] = [
                    {'email': email, 'responseStatus': 'needsAction'}
                    for email in attendees
                ]
            
            # Add meeting link to description if provided
            if meeting_link:
                event_body['description'] = f"{event_body['description']}\n\nMeeting: {meeting_link}".strip()
            
            # Add custom reminders
            event_body['reminders'] = {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 15}         # 15 min before
                ]
            }
            
            # Create event
            logger.info(f"Creating calendar event: {title}")
            event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event_body,
                sendNotifications=True
            ).execute()
            
            logger.info(f"Event created successfully: {event['id']}")
            
            return {
                'success': True,
                'event_id': event['id'],
                'event_link': event.get('htmlLink', ''),
                'start_time': event['start'].get('dateTime', event['start'].get('date')),
                'end_time': event['end'].get('dateTime', event['end'].get('date')),
                'summary': event['summary'],
                'status': event.get('status', 'confirmed')
            }
        
        except HttpError as e:
            logger.error(f"Google Calendar API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating event: {str(e)}")
            raise

    def update_event(
        self,
        event_id: str,
        **kwargs
    ) -> Dict:
        """
        Update an existing calendar event
        
        Args:
            event_id: The ID of the event to update
            **kwargs: Fields to update (title, description, start_time, end_time, etc.)
        
        Returns:
            Updated event details
        """
        try:
            # Get current event
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Update fields
            if 'title' in kwargs:
                event['summary'] = kwargs['title']
            if 'description' in kwargs:
                event['description'] = kwargs['description']
            if 'start_time' in kwargs:
                start = kwargs['start_time']
                event['start'] = {
                    'dateTime': start.isoformat() + 'Z' if start.tzinfo else start.isoformat(),
                    'timeZone': 'UTC'
                }
            if 'end_time' in kwargs:
                end = kwargs['end_time']
                event['end'] = {
                    'dateTime': end.isoformat() + 'Z' if end.tzinfo else end.isoformat(),
                    'timeZone': 'UTC'
                }
            
            # Update event
            logger.info(f"Updating calendar event: {event_id}")
            updated = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event,
                sendNotifications=True
            ).execute()
            
            logger.info(f"Event updated successfully: {event_id}")
            
            return {
                'success': True,
                'event_id': updated['id'],
                'event_link': updated.get('htmlLink', ''),
                'start_time': updated['start'].get('dateTime', updated['start'].get('date')),
                'end_time': updated['end'].get('dateTime', updated['end'].get('date'))
            }
        
        except HttpError as e:
            logger.error(f"Failed to update event {event_id}: {str(e)}")
            raise

    def delete_event(self, event_id: str) -> bool:
        """
        Delete a calendar event
        
        Args:
            event_id: The ID of the event to delete
        
        Returns:
            True if deletion successful
        """
        try:
            logger.info(f"Deleting calendar event: {event_id}")
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"Event deleted successfully: {event_id}")
            return True
        
        except HttpError as e:
            logger.error(f"Failed to delete event {event_id}: {str(e)}")
            raise

    def get_event(self, event_id: str) -> Dict:
        """
        Retrieve event details
        
        Args:
            event_id: The ID of the event
        
        Returns:
            Event details
        """
        try:
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            return {
                'event_id': event['id'],
                'summary': event.get('summary', ''),
                'description': event.get('description', ''),
                'start_time': event['start'].get('dateTime', event['start'].get('date')),
                'end_time': event['end'].get('dateTime', event['end'].get('date')),
                'status': event.get('status', '')
            }
        
        except HttpError as e:
            logger.error(f"Failed to get event {event_id}: {str(e)}")
            raise

    def list_events(self, max_results: int = 10) -> List[Dict]:
        """
        List upcoming events
        
        Args:
            max_results: Maximum number of events to return
        
        Returns:
            List of event details
        """
        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=datetime.utcnow().isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return [
                {
                    'event_id': event['id'],
                    'summary': event.get('summary', ''),
                    'start_time': event['start'].get('dateTime', event['start'].get('date')),
                    'end_time': event['end'].get('dateTime', event['end'].get('date'))
                }
                for event in events
            ]
        
        except HttpError as e:
            logger.error(f"Failed to list events: {str(e)}")
            raise

    def clear_cached_token(self) -> bool:
        """
        Clear cached OAuth token (for re-authentication)
        
        Returns:
            True if token file was deleted
        """
        try:
            if os.path.exists(self.token_storage_path):
                os.remove(self.token_storage_path)
                logger.info(f"Cached token cleared: {self.token_storage_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to clear cached token: {str(e)}")
            return False
