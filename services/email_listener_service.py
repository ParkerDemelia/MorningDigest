import imaplib
import email
import time
import os
from email.header import decode_header
import threading
from datetime import datetime

class EmailListenerService:
    def __init__(self, email_address, password, database_service):
        self.email_address = email_address
        self.password = password
        self.db = database_service
        self.imap_server = "imap.gmail.com"
        self.is_running = False
        self.thread = None

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
        sender = email.utils.parseaddr(email_message["From"])[1]
        
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
        self._store_interaction(sender, body, response)
        
        # Send response
        self._send_response(sender, response, subject)

    def _generate_response(self, subject, body):
        """Generate a response based on the email content."""
        # TODO: Implement more sophisticated query processing
        # For now, just return a simple response
        return f"Thank you for your message. I received your query: {body[:100]}..."

    def _store_interaction(self, sender, query, response):
        """Store the interaction in the database."""
        self.db.store_query(sender, query, response)

    def _send_response(self, to_address, response, subject):
        """Send a response email."""
        from services.email_service import EmailService
        email_service = EmailService(self.email_address, self.password)
        reply_subject = f"Re: {subject}" if not subject.startswith("Re:") else subject
        email_service.send_email(to_address, reply_subject, response) 