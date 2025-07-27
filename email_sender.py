import os
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gmail API configuration
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDENTIALS_FILE = 'credentials.json'  # Changed from credentials.b64
TOKEN_FILE = 'token.json'  # Changed from token.b64

def authenticate_gmail() -> Optional[object]:
    """
    Authenticate with Gmail API using OAuth2.
    Returns Gmail service object or None if authentication fails.
    """
    creds = None
    
    try:
        print("🔐 Attempting Gmail authentication...")
        
        # Check if we have stored credentials
        if os.path.exists(TOKEN_FILE):
            print("📄 Found existing token file...")
            try:
                creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
                print("✅ Loaded existing credentials")
            except Exception as token_error:
                print(f"⚠️  Error loading token: {token_error}")
                # Remove invalid token
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
                creds = None
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Refreshing expired token...")
                try:
                    creds.refresh(Request())
                    print("✅ Token refreshed successfully")
                except Exception as refresh_error:
                    print(f"⚠️  Token refresh failed: {refresh_error}")
                    # Remove the invalid token file
                    if os.path.exists(TOKEN_FILE):
                        os.remove(TOKEN_FILE)
                    creds = None
            
            if not creds:
                print("🔑 Starting new authentication flow...")
                # Load credentials from file
                if os.path.exists(CREDENTIALS_FILE):
                    try:
                        print("📋 Loading client configuration...")
                        flow = InstalledAppFlow.from_client_secrets_file(
                            CREDENTIALS_FILE, SCOPES
                        )
                        print("🌐 Opening browser for authentication...")
                        creds = flow.run_local_server(port=0)
                        print("✅ Authentication completed")
                    except Exception as creds_error:
                        print(f"❌ Error loading credentials: {creds_error}")
                        return None
                else:
                    print("❌ Credentials file not found. Please ensure credentials.json exists.")
                    return None
            
            # Save the credentials for the next run
            if creds:
                print("💾 Saving credentials for future use...")
                with open(TOKEN_FILE, 'w') as token_file:
                    token_file.write(creds.to_json())
        
        # Build the Gmail service
        if creds:
            print("🔧 Building Gmail service...")
            service = build('gmail', 'v1', credentials=creds)
            print("✅ Gmail authentication successful!")
            return service
        else:
            print("❌ No valid credentials available")
            return None
        
    except Exception as e:
        print(f"❌ Gmail authentication failed: {e}")
        print("💡 This might be because:")
        print("   1. Gmail API is not enabled in your Google Cloud project")
        print("   2. Your credentials don't have the correct scopes")
        print("   3. The project doesn't have Gmail API access")
        return None

def create_email_message(html_content: str, recipient_email: str, sender_email: str = None) -> dict:
    """
    Create a MIME email message with HTML content.
    Returns the message dict for Gmail API.
    """
    # Get sender email from environment or use default
    if not sender_email:
        sender_email = os.getenv('EMAIL_SENDER')
        if not sender_email:
            print("⚠️  EMAIL_SENDER not set in environment. Using authenticated user's email.")
    
    # Create message
    message = MIMEMultipart('alternative')
    message['to'] = recipient_email
    message['from'] = sender_email
    message['subject'] = f"📰 Daily News Digest — {datetime.now().strftime('%B %d, %Y')}"
    
    # Add HTML content
    html_part = MIMEText(html_content, 'html')
    message.attach(html_part)
    
    # Encode the message for Gmail API
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    return {
        'raw': raw_message
    }

def send_daily_digest(html_content: str, recipient_email: str) -> bool:
    """Send the daily news digest email"""
    try:
        print("📧 Sending daily news digest email...")
        
        # Authenticate with Gmail
        service = authenticate_gmail()
        if not service:
            print("❌ Gmail authentication failed - cannot send email")
            return False
        
        # Create email message
        sender_email = os.getenv('EMAIL_SENDER')
        message = create_email_message(html_content, recipient_email, sender_email)
        
        # Send the email
        sent_message = service.users().messages().send(userId='me', body=message).execute()
        
        # Print success details
        message_id = sent_message.get('id', 'Unknown')
        print("✅ Email sent successfully!")
        print(f"📧 Message ID: {message_id}")
        print(f"📬 Recipient: {recipient_email}")
        print(f"📅 Date: {datetime.now().strftime('%B %d, %Y')}")
        
        return True
        
    except HttpError as e:
        print(f"❌ Gmail API error: {e}")
        if e.resp.status == 401:
            print("🔑 Authentication failed - check your Gmail API credentials")
        elif e.resp.status == 403:
            print("🚫 Permission denied - check Gmail API scopes")
        elif e.resp.status == 429:
            print("⏰ Rate limit exceeded - try again later")
        return False
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

def test_email_sending(recipient_email: str = None) -> bool:
    """
    Test email sending functionality with a simple HTML email.
    """
    if not recipient_email:
        recipient_email = os.getenv('EMAIL_RECIPIENTS')
        if not recipient_email:
            print("❌ EMAIL_RECIPIENTS not set in environment variables")
            return False
    
    # Create a simple test email
    test_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Email</title>
    </head>
    <body>
        <h1>📧 Test Email</h1>
        <p>This is a test email from the Daily News Digest system.</p>
        <p>Sent on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        <p>If you receive this email, the Gmail API integration is working correctly!</p>
    </body>
    </html>
    """
    
    return send_daily_digest(test_html, recipient_email)

if __name__ == "__main__":
    # Test email sending
    print("🧪 Testing email sending functionality...")
    
    recipient = os.getenv('EMAIL_RECIPIENTS')
    if not recipient:
        print("❌ Please set EMAIL_RECIPIENTS in your environment variables")
    else:
        success = test_email_sending(recipient)
        if success:
            print("✅ Test email sent successfully!")
        else:
            print("❌ Test email failed to send") 