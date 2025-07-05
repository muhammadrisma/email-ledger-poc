#!/usr/bin/env python3
"""
Test Email Processing Script

This script tests the email processing functionality with direct Gmail API usage.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.services.email_processor import EmailProcessor
from app.services.ai_extractor import AIExtractor
from app.config import Config

def test_email_processor():
    """Test the email processor"""
    print("🔍 Testing Email Processor...")
    
    try:
        # Test Gmail service connection
        processor = EmailProcessor()
        print("✅ Gmail service connected successfully")
        
        # Test getting recent financial emails
        print("\n📧 Fetching recent financial emails...")
        emails = processor.get_recent_financial_emails(days_back=7)
        
        print(f"✅ Found {len(emails)} financial emails")
        
        if emails:
            print("\n📋 Sample emails:")
            for i, email in enumerate(emails[:3], 1):
                print(f"  {i}. {email['subject']} - {email['sender']}")
        
        return emails
        
    except Exception as e:
        print(f"❌ Error in email processor: {e}")
        return []

def test_ai_extractor():
    """Test the AI extractor"""
    print("\n🤖 Testing AI Extractor...")
    
    if not Config.OPENAI_API_KEY:
        print("❌ OpenAI API key not set")
        return False
    
    try:
        extractor = AIExtractor()
        print("✅ AI Extractor initialized successfully")
        
        # Test with sample data
        sample_email = {
            'subject': 'Payment Confirmation - $99.99',
            'sender': 'service@stripe.com',
            'date': '2024-01-15',
            'body': 'Your payment of $99.99 has been processed successfully.',
            'html_body': '<p>Your payment of $99.99 has been processed successfully.</p>',
            'attachments': []
        }
        
        print("\n📊 Testing AI extraction...")
        result = extractor.extract_financial_data(sample_email)
        
        print(f"✅ AI extraction result:")
        print(f"  Amount: {result.get('amount')}")
        print(f"  Currency: {result.get('currency')}")
        print(f"  Vendor: {result.get('vendor')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in AI extractor: {e}")
        return False

def test_full_pipeline():
    """Test the full email processing pipeline"""
    print("\n🚀 Testing Full Pipeline...")
    
    try:
        # Get emails
        processor = EmailProcessor()
        emails = processor.get_recent_financial_emails(days_back=7)
        
        if not emails:
            print("No financial emails found to test with")
            return
        
        # Test AI extraction on first email
        extractor = AIExtractor()
        test_email = emails[0]
        
        print(f"\n📧 Testing extraction on: {test_email['subject']}")
        
        result = extractor.extract_financial_data(test_email)
        
        print(f"✅ Extraction result:")
        print(f"  Amount: {result.get('amount')}")
        print(f"  Currency: {result.get('currency')}")
        print(f"  Vendor: {result.get('vendor')}")
        print(f"  Type: {result.get('transaction_type')}")
        
        if result.get('amount'):
            # Test classification
            classification = extractor.classify_expense(test_email, result)
            print(f"  Category: {classification.get('category')}")
        
    except Exception as e:
        print(f"❌ Error in full pipeline: {e}")

def main():
    """Main test function"""
    print("🧪 Email Processing Test Suite")
    print("=" * 50)
    
    # Test email processor
    emails = test_email_processor()
    
    # Test AI extractor
    ai_ok = test_ai_extractor()
    
    # Test full pipeline if we have emails and AI is working
    if emails and ai_ok:
        test_full_pipeline()
    
    print("\n✅ Test suite completed!")

if __name__ == "__main__":
    main() 