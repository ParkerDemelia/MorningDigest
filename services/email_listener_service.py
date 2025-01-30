import imaplib
import email
import time
import os
from email.header import decode_header
import threading
from datetime import datetime, timedelta
import re
from dateutil import parser
from services.calendar_service import GoogleCalendarService
from services.gemini_service import GeminiService

class EmailListenerService:
    def __init__(self, email_address, password, database_service):
        self.email_address = email_address
        self.password = password
        self.db = database_service
        self.imap_server = "imap.gmail.com"
        self.is_running = False
        self.thread = None
        self.calendar_service = GoogleCalendarService()
        self.gemini = GeminiService()

    def start(self):
        """Start the email listener in a separate thread."""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._listen_for_emails)
            self.thread.daemon = True
            self.thread.start()
            print("Email listener started successfully")

    def stop(self):
        """Stop the email listener."""
        self.is_running = False
        if self.thread:
            self.thread.join()
            print("Email listener stopped")

    def _listen_for_emails(self):
        """Continuously check for new emails."""
        while self.is_running:
            try:
                # Connect to IMAP server
                mail = imaplib.IMAP4_SSL(self.imap_server)
                mail.login(self.email_address, self.password)
                
                while self.is_running:
                    # Select inbox
                    mail.select("INBOX")
                    
                    # Search for unread emails
                    _, messages = mail.search(None, "UNSEEN")
                    
                    for num in messages[0].split():
                        # Fetch email message
                        _, msg_data = mail.fetch(num, "(RFC822)")
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)
                        
                        # Process the email
                        self._process_email(email_message)
                        
                    # Wait before checking again
                    time.sleep(60)
                    
            except Exception as e:
                print(f"Error in email listener: {str(e)}")
                time.sleep(300)  # Wait 5 minutes before retrying
                
            finally:
                try:
                    mail.logout()
                except:
                    pass

    def _process_email(self, email_message):
        """Process an incoming email message."""
        # Get sender
        self.current_sender = email.utils.parseaddr(email_message["From"])[1]
        
        # Get subject and decode if necessary
        subject = decode_header(email_message["Subject"])[0]
        if isinstance(subject[0], bytes):
            subject = subject[0].decode(subject[1] or "utf-8")
        else:
            subject = subject[0]
            
        # Get body
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = email_message.get_payload(decode=True).decode()
            
        # Process the query and generate response
        response = self._generate_response(subject, body)
        
        # Store the interaction in the database
        self._store_interaction(self.current_sender, body, response)
        
        # Send response
        self._send_response(self.current_sender, response, subject)

    def _generate_response(self, subject, body):
        """Generate a response based on the email content."""
        subject_lower = subject.lower()
        
        # Check for different types of requests
        if subject_lower.startswith('add event') or subject_lower.startswith('new event'):
            return self._process_calendar_request(body)
        elif any(keyword in subject_lower for keyword in ['show events', 'list events', 'upcoming events', 'my events']):
            return self._get_upcoming_events()
        elif subject_lower.startswith('analyze events') or subject_lower.startswith('event insights'):
            return self._analyze_upcoming_events()
        
        # Handle other types of queries
        return f"Thank you for your message. I received your query: {body[:100]}...\n\nYou can:\n- Add events (Subject: 'Add Event')\n- View upcoming events (Subject: 'Show Events')\n- Get event insights (Subject: 'Analyze Events')"

    def _process_calendar_request(self, body):
        """Process an email containing calendar event details."""
        try:
            # Extract event details using regex patterns
            title_match = re.search(r'Title:\s*(.+?)(?:\n|$)', body)
            date_match = re.search(r'Date:\s*(.+?)(?:\n|$)', body)
            time_match = re.search(r'Time:\s*(.+?)(?:\n|$)', body)
            duration_match = re.search(r'Duration:\s*(.+?)(?:\n|$)', body)
            description_match = re.search(r'Description:\s*(.+?)(?:\n|$)', body)

            if not (title_match and date_match and time_match):
                return """Invalid event format. Please use the following format:
Title: Event Name
Date: YYYY-MM-DD
Time: HH:MM
Duration: X hours (optional, defaults to 1 hour)
Description: Event description (optional)"""

            title = title_match.group(1).strip()
            date_str = date_match.group(1).strip()
            time_str = time_match.group(1).strip()
            
            # Parse start time
            start_time = parser.parse(f"{date_str} {time_str}")
            
            # Calculate end time
            duration_hours = 1  # default duration
            if duration_match:
                duration_str = duration_match.group(1).strip()
                duration_hours = float(re.search(r'(\d+(?:\.\d+)?)', duration_str).group(1))
            
            end_time = start_time + timedelta(hours=duration_hours)
            
            # Get description if available
            description = description_match.group(1).strip() if description_match else ""

            # Store in database
            event_id = self.db.store_calendar_event(
                email_from=self.current_sender,
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time
            )

            # Add to Google Calendar
            try:
                self.calendar_service.add_event(
                    title=title,
                    description=description,
                    start_time=start_time,
                    end_time=end_time
                )
                self.db.update_calendar_event_status(event_id, 'added')
                return f"Successfully added event '{title}' to your calendar for {start_time.strftime('%B %d, %Y at %I:%M %p')}"
            except Exception as e:
                self.db.update_calendar_event_status(event_id, 'failed')
                return f"Failed to add event to calendar: {str(e)}"

        except Exception as e:
            return f"Error processing calendar request: {str(e)}\n\nPlease use the following format:\nTitle: Event Name\nDate: YYYY-MM-DD\nTime: HH:MM\nDuration: X hours (optional)\nDescription: Event description (optional)"

    def _get_upcoming_events(self, days=7):
        """Get upcoming calendar events."""
        try:
            # Get events from Google Calendar
            today = datetime.now()
            end_date = today + timedelta(days=days)
            events = self.calendar_service.get_events(today, end_date)
            
            if not events:
                return "You have no upcoming events in the next 7 days."
            
            # Format events nicely
            response = "Your upcoming events:\n\n"
            for event in events:
                response += f"📅 {event}\n\n"
            
            response += "\nTo add new events, send an email with subject 'Add Event' and follow the format:\nTitle: Event Name\nDate: YYYY-MM-DD\nTime: HH:MM\nDuration: X hours (optional)\nDescription: Event description (optional)"
            
            return response

        except Exception as e:
            return f"Error retrieving events: {str(e)}"

    def _analyze_upcoming_events(self, days=7):
        """Get upcoming events and generate insights using Gemini."""
        try:
            # Get events from Google Calendar
            today = datetime.now()
            end_date = today + timedelta(days=days)
            events = self.calendar_service.get_events(today, end_date)
            
            if not events:
                return "You have no upcoming events to analyze in the next 7 days."
            
            # Format events for Gemini
            events_text = "Upcoming events:\n"
            for event in events:
                events_text += f"- {event}\n"
            
            # Generate insights using Gemini
            prompt = f"""Here are the user's upcoming calendar events for the next 7 days:

{events_text}

Please provide:
1. A brief overview of their schedule
2. Any potential scheduling conflicts or tight timings
3. Suggestions for better time management
4. Tips for preparation or things to keep in mind
5. Any patterns or insights about their schedule

Keep the response concise but informative."""

            insights = self.gemini.generate_text(prompt)
            
            if not insights:
                insights = "Unable to generate insights at the moment. Here are your upcoming events:\n\n" + events_text
            
            return insights

        except Exception as e:
            return f"Error analyzing events: {str(e)}"

    def _store_interaction(self, sender, query, response):
        """Store the interaction in the database."""
        self.db.store_query(sender, query, response)

    def _send_response(self, to_address, response, subject):
        """Send a response email."""
        from services.email_service import EmailService
        email_service = EmailService(self.email_address, self.password)
        reply_subject = f"Re: {subject}" if not subject.startswith("Re:") else subject
        email_service.send_email(to_address, reply_subject, response) 