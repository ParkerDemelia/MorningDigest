from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle

class GoogleCalendarService:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.creds = None
        self.is_configured = False
        
        # Only try to authenticate if credentials file is provided
        if os.getenv('GOOGLE_CALENDAR_CREDENTIALS'):
            try:
                self._authenticate()
                self.is_configured = True
            except Exception as e:
                print(f"Calendar setup failed: {str(e)}")

    def _authenticate(self):
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                creds_path = os.getenv('GOOGLE_CALENDAR_CREDENTIALS')
                if not os.path.exists(creds_path):
                    raise FileNotFoundError(f"Credentials file not found at: {creds_path}")
                    
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_path,
                    self.SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

    def get_events(self, start_date, end_date):
        if not self.is_configured:
            return """
                <li>⚠️ Calendar not configured. To see your events:</li>
                <li>1. Enable Google Calendar API in Google Cloud Console</li>
                <li>2. Download credentials.json</li>
                <li>3. Set GOOGLE_CALENDAR_CREDENTIALS in .env file</li>
            """
            
        try:
            service = build('calendar', 'v3', credentials=self.creds)
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                maxResults=10,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                return "<li>No upcoming events</li>"
                
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                time_str = start.split('T')[1][:5] if 'T' in start else 'All day'
                formatted_events.append(
                    f"<li>{time_str} - {event['summary']}</li>"
                )
                
            return "\n".join(formatted_events)
            
        except Exception as e:
            return f"<li>Unable to fetch calendar events: {str(e)}</li>" 