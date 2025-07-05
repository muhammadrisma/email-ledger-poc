#!/usr/bin/env python3
"""
Gmail API Setup Script

This script helps you set up Gmail API credentials for the email ledger POC.
"""

import os
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

# OAuth configuration
OAUTH_PORT = 8080
OAUTH_REDIRECT_URI = f'http://localhost:{OAUTH_PORT}/'

def setup_gmail_credentials():
    """Set up Gmail API credentials"""
    
    creds = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("❌ credentials.json not found!")
                print("\nTo get credentials.json:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project or select existing one")
                print("3. Enable Gmail API")
                print("4. Go to Credentials")
                print("5. Create OAuth 2.0 Client ID")
                print("6. Download the JSON file as 'credentials.json'")
                print("7. Place it in this directory")
                return False
            
            # Verify credentials format
            try:
                with open('credentials.json', 'r') as f:
                    creds_data = json.load(f)
                
                if 'web' in creds_data:
                    print("✅ Web application credentials detected")
                elif 'installed' in creds_data:
                    print("✅ Desktop application credentials detected")
                else:
                    print("❌ Invalid credentials format")
                    print("Expected 'web' or 'installed' section in credentials.json")
                    return False
                    
            except Exception as e:
                print(f"❌ Error reading credentials.json: {e}")
                return False
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                print(f"🌐 Starting OAuth flow on port {OAUTH_PORT}")
                print(f"📋 Redirect URI: {OAUTH_REDIRECT_URI}")
                print("\n⚠️  Make sure this redirect URI is added to your Google Cloud Console OAuth client!")
                creds = flow.run_local_server(port=OAUTH_PORT)
            except Exception as e:
                if "redirect_uri_mismatch" in str(e):
                    print("\n❌ Redirect URI mismatch error!")
                    print(f"Please add this redirect URI to your Google Cloud Console:")
                    print(f"   {OAUTH_REDIRECT_URI}")
                    print("\nSteps:")
                    print("1. Go to https://console.cloud.google.com/")
                    print("2. Navigate to APIs & Services → Credentials")
                    print("3. Edit your OAuth 2.0 Client ID")
                    print("4. Add the redirect URI above to 'Authorized redirect URIs'")
                    print("5. Save and try again")
                    return False
                else:
                    print(f"❌ OAuth error: {e}")
                    return False
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    print("Gmail API credentials configured successfully!")
    return True

def test_gmail_connection():
    """Test the Gmail API connection"""
    try:
        from simplegmail import Gmail
        gmail = Gmail()
        
        messages = gmail.get_messages(limit=1)
        print("Gmail API connection successful!")
        print(f"Found {len(messages)} messages in inbox")
        return True
        
    except Exception as e:
        print(f"Gmail API connection failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Gmail API Setup for Email Ledger POC")
    print("=" * 50)
    
    if not os.path.exists('credentials.json'):
        print("credentials.json not found!")
        print("\nPlease download your Gmail API credentials:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials")
        print("5. Download as 'credentials.json'")
        print("6. Place in this directory")
        return
    
    if setup_gmail_credentials():
        test_gmail_connection()
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Set your OpenAI API key in .env file")
    print("2. Configure your database connection")
    print("3. Run: python -m src.cli.main process")

if __name__ == "__main__":
    main() 