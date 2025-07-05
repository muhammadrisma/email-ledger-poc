#!/usr/bin/env python3
"""
Test Gmail Credentials Script

This script helps verify your credentials.json file and debug OAuth issues.
"""

import os
import json
import sys
from pathlib import Path

def test_credentials_file():
    """Test if credentials.json exists and is valid"""
    
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        print("Please download your OAuth 2.0 credentials from Google Cloud Console")
        return False
    
    try:
        with open('credentials.json', 'r') as f:
            creds_data = json.load(f)
        
        print("✅ credentials.json found and is valid JSON")
        
        # Check if it's web application format
        if 'web' in creds_data:
            print("✅ Web application format detected")
            web_config = creds_data['web']
            
            # Check required fields for web application
            required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
            missing_fields = []
            
            for field in required_fields:
                if field not in web_config:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            print("✅ All required web application fields are present")
            print(f"📋 Client ID: {web_config['client_id'][:20]}...")
            
            return True
            
        # Check if it's desktop application format
        elif 'installed' in creds_data:
            print("✅ Desktop application format detected")
            installed_config = creds_data['installed']
            
            # Check required fields for desktop application
            required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
            missing_fields = []
            
            for field in required_fields:
                if field not in installed_config:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            print("✅ All required desktop application fields are present")
            print(f"📋 Client ID: {installed_config['client_id'][:20]}...")
            
            return True
            
        else:
            print("❌ Unknown credentials format")
            print("Expected 'web' or 'installed' section")
            return False
        
    except json.JSONDecodeError:
        print("❌ credentials.json is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials.json: {e}")
        return False

def check_oauth_consent():
    """Check OAuth consent screen configuration"""
    print("\n📋 OAuth Consent Screen Checklist:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Navigate to APIs & Services → OAuth consent screen")
    print("3. Verify these settings:")
    print("   - App name is set")
    print("   - User support email is set")
    print("   - Developer contact information is set")
    print("   - If in 'Testing' mode, add your email to 'Test users'")
    print("   - Or publish the app to 'Production'")

def check_gmail_api():
    """Check Gmail API configuration"""
    print("\n📧 Gmail API Checklist:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Navigate to APIs & Services → Library")
    print("3. Search for 'Gmail API'")
    print("4. Make sure it shows as 'Enabled'")
    print("5. If not enabled, click on it and press 'Enable'")

def check_oauth_credentials():
    """Check OAuth credentials configuration"""
    print("\n🔑 OAuth Credentials Checklist:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Navigate to APIs & Services → Credentials")
    print("3. Check your OAuth 2.0 Client ID:")
    print("   - Application type should be 'Web application'")
    print("   - Authorized redirect URIs should include:")
    print("     * http://localhost:8080/")
    print("     * http://127.0.0.1:8080/")

def main():
    """Main test function"""
    print("🔍 Gmail Credentials Test")
    print("=" * 40)
    
    # Test credentials file
    if test_credentials_file():
        print("\n✅ Credentials file is valid!")
        
        # Show checklists
        check_oauth_consent()
        check_gmail_api()
        check_oauth_credentials()
        
        print("\n📝 Next steps:")
        print("1. Fix any issues identified above")
        print("2. Run: python scripts/setup_gmail.py")
    else:
        print("\n❌ Please fix the credentials file issues first")

if __name__ == "__main__":
    main() 