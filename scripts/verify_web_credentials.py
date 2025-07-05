#!/usr/bin/env python3
"""
Verify Web Application Credentials

This script checks if your credentials.json is properly formatted for web application OAuth.
"""

import os
import json

def verify_web_credentials():
    """Verify web application credentials format"""
    
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        return False
    
    try:
        with open('credentials.json', 'r') as f:
            creds_data = json.load(f)
        
        print("✅ credentials.json found")
        
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
            
            # Check redirect URIs
            if 'redirect_uris' in web_config:
                print(f"📋 Redirect URIs in file: {web_config['redirect_uris']}")
            else:
                print("⚠️  No redirect_uris in credentials file (this is normal for downloaded files)")
            
            return True
            
        elif 'installed' in creds_data:
            print("⚠️  Desktop application format detected")
            print("This is a desktop application credential, not web application")
            print("You may want to create a web application credential instead")
            return False
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

def main():
    """Main verification function"""
    print("🔍 Web Application Credentials Verification")
    print("=" * 50)
    
    if verify_web_credentials():
        print("\n✅ Your credentials look good for web application!")
        print("\n📝 Next steps:")
        print("1. Make sure redirect URIs are set in Google Cloud Console")
        print("2. Run: python scripts/setup_gmail.py")
    else:
        print("\n❌ Please fix the credentials issues first")

if __name__ == "__main__":
    main() 