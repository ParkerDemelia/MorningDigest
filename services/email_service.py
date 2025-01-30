import yagmail
import os
from datetime import datetime

class EmailService:
    def __init__(self, email_address, app_password):
        self.email = email_address
        self.is_configured = False
        
        # Add more detailed debugging for environment variable
        print("\nEmail Service Debug:")
        print(f"Environment variables loaded from: {os.path.abspath('.env')}")
        test_mode_value = os.getenv('EMAIL_TEST_MODE')
        print(f"Raw EMAIL_TEST_MODE value: '{test_mode_value}'")
        
        if test_mode_value is None:
            print("Warning: EMAIL_TEST_MODE not found in environment, defaulting to 'true'")
            test_mode_value = 'true'
            
        self.test_mode = test_mode_value.lower().strip() not in ('false', '0')
        print(f"Parsed test_mode value: {self.test_mode}")
        print(f"Email Address: {email_address}")
        print(f"Password Length: {len(app_password) if app_password else 0}")
        print(f"Test Mode Enabled: {self.test_mode}")
        
        if self.test_mode:
            print("Email Service running in test mode (printing to console)")
            self.is_configured = True
            return
            
        if not email_address or not app_password:
            print("Email credentials not configured in .env file")
            return
            
        try:
            print("Attempting to connect to Gmail...")
            self.yag = yagmail.SMTP(email_address, app_password)
            self.is_configured = True
            print("Gmail connection successful!")
        except Exception as e:
            print(f"Email setup failed with error: {str(e)}")
            print("Make sure you're using an App Password from Google Account settings")

    def send_digest(self, content):
        # Format today's date for the subject
        today = datetime.now()
        subject = f"Today's Plan - {today.strftime('%A, %B %d')}"

        if self.test_mode:
            print("\n========== DIGEST EMAIL PREVIEW ==========")
            print(f"Subject: {subject}")
            print(content)
            print("========== END EMAIL PREVIEW ==========\n")
            return True
            
        if not self.is_configured:
            print("""
Email not configured. To set up email:
1. Create an app password in your Google Account settings:
   - Go to Google Account → Security
   - Enable 2-Step Verification if not enabled
   - Go to App Passwords
   - Select 'Mail' and 'Other (Custom name)'
   - Enter 'Morning Digest'
   - Copy the 16-character password
2. Add to .env file:
   EMAIL_ADDRESS=your.email@gmail.com
   EMAIL_PASSWORD=your16charapppassword (no spaces)
3. Set EMAIL_TEST_MODE=false to enable sending
""")
            return False
            
        try:
            print(f"Attempting to send email to {self.email}...")
            self.yag.send(
                to=self.email,
                subject=subject,
                contents=content
            )
            print("Email sent successfully!")
            return True
        except Exception as e:
            print(f"Failed to send email with error: {str(e)}")
            print("Check that your App Password is correct and has no spaces")
            return False 