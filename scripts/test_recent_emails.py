#!/usr/bin/env python3
"""
Test script for the new recent emails processing endpoint.
"""

import requests
import json
from typing import Dict

def test_process_recent_emails(email_count: int = 5) -> Dict:
    """
    Test the new process-recent-emails endpoint.
    
    Args:
        email_count: Number of recent emails to process
        
    Returns:
        Processing result
    """
    print(f"🔄 Testing process-recent-emails endpoint with {email_count} emails...")
    
    try:
        # Make request to the new endpoint
        response = requests.post(
            "http://localhost:8000/process-recent-emails",
            params={"email_count": email_count}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"📊 Processing Results:")
            print(f"  - Processed: {result.get('processed_count', 0)} emails")
            print(f"  - Successful extractions: {result.get('successful_extractions', 0)}")
            print(f"  - Timestamp: {result.get('timestamp', 'unknown')}")
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return {}
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server")
        print("Make sure the server is running on http://localhost:8000")
        return {}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

def test_different_counts():
    """Test the endpoint with different email counts."""
    print("🧪 Testing different email counts...")
    
    test_counts = [1, 3, 5, 10]
    
    for count in test_counts:
        print(f"\n📧 Testing with {count} emails:")
        result = test_process_recent_emails(count)
        if result:
            success_rate = (result.get('successful_extractions', 0) / result.get('processed_count', 1)) * 100
            print(f"  Success rate: {success_rate:.1f}%")

if __name__ == "__main__":
    print("🚀 Email Ledger - Recent Emails Processing Test")
    print("=" * 50)
    
    test_process_recent_emails() 
    test_different_counts()
    
    print("\n✅ Test completed!") 