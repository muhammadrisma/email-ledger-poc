#!/usr/bin/env python3
"""
Test script for PDF processing capabilities.
Tests the email processor's ability to extract text from PDF attachments.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.services.email_processor import EmailProcessor
import tempfile
import base64

def test_pdf_text_extraction():
    """Test PDF text extraction functionality"""
    print("=== Testing PDF Text Extraction ===")
    
    processor = EmailProcessor()
    
    # Create a simple test PDF content (this would normally come from an email attachment)
    # For testing, we'll create a mock PDF-like structure
    test_pdf_data = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF"
    
    print(f"Test PDF data size: {len(test_pdf_data)} bytes")
    
    try:
        # Test PDF text extraction
        extracted_text = processor.extract_pdf_text(test_pdf_data)
        print(f"Extracted text length: {len(extracted_text)}")
        print(f"Extracted text: {extracted_text[:200]}...")
        
        if extracted_text:
            print("✅ PDF text extraction working")
        else:
            print("⚠️  No text extracted from PDF")
            
    except Exception as e:
        print(f"❌ Error in PDF text extraction: {e}")

def test_attachment_processing():
    """Test attachment processing with PDF"""
    print("\n=== Testing Attachment Processing ===")
    
    processor = EmailProcessor()
    
    # Create mock attachment data with proper Gmail API structure
    # In Gmail API, attachment data comes base64-encoded
    pdf_data = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Invoice Amount: $150.00) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF"
    
    # Encode as base64 to simulate Gmail API
    import base64
    encoded_data = base64.urlsafe_b64encode(pdf_data).decode('utf-8')
    
    attachment_data = {
        'filename': 'test_invoice.pdf',
        'mimeType': 'application/pdf',  # Gmail API uses mimeType
        'data': encoded_data,  # Base64 encoded data
        'size': len(pdf_data)
    }
    
    try:
        # Process the attachment
        result = processor.process_attachment(attachment_data)
        
        print(f"Attachment filename: {result['filename']}")
        print(f"Content type: {result['content_type']}")
        print(f"Is financial: {result['is_financial']}")
        print(f"Text content length: {len(result.get('text_content', ''))}")
        print(f"Text content: {result.get('text_content', '')[:200]}...")
        
        if result['is_financial']:
            print("✅ PDF correctly identified as financial document")
        else:
            print("⚠️  PDF not identified as financial document")
            
        if result.get('text_content'):
            print("✅ PDF text content extracted")
        else:
            print("⚠️  No text content extracted from PDF")
            
    except Exception as e:
        print(f"❌ Error in attachment processing: {e}")
        import traceback
        traceback.print_exc()

def test_ai_extraction_with_pdf():
    """Test AI extraction with PDF content"""
    print("\n=== Testing AI Extraction with PDF ===")
    
    try:
        from app.services.ai_extractor import AIExtractor
        ai_extractor = AIExtractor()
        
        # Create mock email content with PDF attachment
        email_content = {
            'subject': 'Invoice from Test Company',
            'sender': 'billing@testcompany.com',
            'date': '2024-01-15',
            'body': 'Please find attached invoice for services rendered.',
            'html_body': '<p>Please find attached invoice for services rendered.</p>',
            'attachments': [
                {
                    'filename': 'invoice.pdf',
                    'content_type': 'application/pdf',
                    'text_content': 'Invoice\nTest Company\nAmount: $150.00\nDate: 2024-01-15\nInvoice #: INV-001',
                    'is_financial': True
                }
            ]
        }
        
        # Extract financial data
        result = ai_extractor.extract_financial_data(email_content)
        
        print(f"Extracted amount: {result.get('amount')}")
        print(f"Extracted currency: {result.get('currency')}")
        print(f"Extracted vendor: {result.get('vendor')}")
        print(f"Extracted date: {result.get('date')}")
        print(f"Extracted description: {result.get('description')}")
        
        if result.get('amount'):
            print("✅ Amount successfully extracted from PDF")
        else:
            print("⚠️  No amount extracted from PDF")
            
    except ValueError as e:
        if "OpenAI API key is required" in str(e):
            print("⚠️  OpenAI API key not configured - skipping AI extraction test")
            print("   To test AI extraction, set the OPENAI_API_KEY environment variable:")
            print("   - Windows: set OPENAI_API_KEY=your_api_key_here")
            print("   - Linux/Mac: export OPENAI_API_KEY=your_api_key_here")
            print("   - Or add it to your .env file: OPENAI_API_KEY=your_api_key_here")
        else:
            print(f"❌ Error in AI extraction: {e}")
    except Exception as e:
        print(f"❌ Error in AI extraction: {e}")

def test_real_pdf_processing():
    """Test with a more realistic PDF structure"""
    print("\n=== Testing Realistic PDF Processing ===")
    
    processor = EmailProcessor()
    
    # Create a more realistic PDF structure that PyPDF2 can actually parse
    # This is a minimal PDF with actual text content
    realistic_pdf_data = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
>>
endobj
4 0 obj
<<
/Length 89
>>
stream
BT
/F1 12 Tf
72 720 Td
(Invoice) Tj
0 -20 Td
(Company: Test Company) Tj
0 -20 Td
(Amount: $150.00) Tj
0 -20 Td
(Date: 2024-01-15) Tj
0 -20 Td
(Invoice #: INV-001) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000204 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
342
%%EOF"""
    
    try:
        # Test PDF text extraction
        extracted_text = processor.extract_pdf_text(realistic_pdf_data)
        print(f"Realistic PDF extracted text length: {len(extracted_text)}")
        print(f"Extracted text: {extracted_text[:300]}...")
        
        if extracted_text and "Invoice" in extracted_text:
            print("✅ Realistic PDF text extraction working")
        else:
            print("⚠️  Realistic PDF text extraction failed")
            
    except Exception as e:
        print(f"❌ Error in realistic PDF text extraction: {e}")

def main():
    """Run all PDF processing tests"""
    print("PDF Processing Test Suite")
    print("=" * 50)
    
    try:
        test_pdf_text_extraction()
        test_attachment_processing()
        test_real_pdf_processing()
        test_ai_extraction_with_pdf()
        
        print("\n" + "=" * 50)
        print("PDF Processing Tests Complete")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")

if __name__ == "__main__":
    main() 