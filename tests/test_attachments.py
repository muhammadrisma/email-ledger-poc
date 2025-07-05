import unittest
from unittest.mock import Mock, patch
import io
from src.app.services.email_processor import EmailProcessor

class TestEmailProcessorAttachments(unittest.TestCase):
    
    def setUp(self):
        self.processor = EmailProcessor()
    
    def test_extract_pdf_text(self):
        """Test PDF text extraction"""
        # Create a simple PDF-like structure for testing
        pdf_data = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
        
        # Mock PyPDF2 to return some text
        with patch('PyPDF2.PdfReader') as mock_pdf_reader:
            mock_page = Mock()
            mock_page.extract_text.return_value = "Test PDF content"
            mock_pdf_reader.return_value.pages = [mock_page]
            
            result = self.processor.extract_pdf_text(pdf_data)
            self.assertEqual(result, "Test PDF content\n")
    
    def test_extract_csv_data(self):
        """Test CSV data extraction"""
        csv_data = b"Date,Amount,Description\n2024-01-01,100.00,Test transaction\n"
        
        result = self.processor.extract_csv_data(csv_data)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['Date'], '2024-01-01')
        self.assertEqual(result[0]['Amount'], '100.00')
        self.assertEqual(result[0]['Description'], 'Test transaction')
    
    def test_process_attachment_pdf(self):
        """Test PDF attachment processing"""
        mock_attachment = Mock()
        mock_attachment.filename = "receipt.pdf"
        mock_attachment.content_type = "application/pdf"
        mock_attachment.data = b"PDF data"
        
        with patch.object(self.processor, 'extract_pdf_text') as mock_extract:
            mock_extract.return_value = "PDF content"
            
            result = self.processor.process_attachment(mock_attachment)
            
            self.assertEqual(result['filename'], "receipt.pdf")
            self.assertEqual(result['content_type'], "application/pdf")
            self.assertEqual(result['text_content'], "PDF content")
            self.assertIsNone(result['csv_data'])
    
    def test_process_attachment_csv(self):
        """Test CSV attachment processing"""
        mock_attachment = Mock()
        mock_attachment.filename = "transactions.csv"
        mock_attachment.content_type = "text/csv"
        mock_attachment.data = b"Date,Amount\n2024-01-01,100.00\n"
        
        with patch.object(self.processor, 'extract_csv_data') as mock_extract:
            mock_extract.return_value = [{'Date': '2024-01-01', 'Amount': '100.00'}]
            
            result = self.processor.process_attachment(mock_attachment)
            
            self.assertEqual(result['filename'], "transactions.csv")
            self.assertEqual(result['content_type'], "text/csv")
            self.assertEqual(result['csv_data'], [{'Date': '2024-01-01', 'Amount': '100.00'}])
            self.assertEqual(result['text_content'], '')
    
    def test_extract_email_content_with_attachments(self):
        """Test email content extraction with attachments"""
        mock_message = Mock()
        mock_message.subject = "Test Email"
        mock_message.sender = "test@example.com"
        mock_message.date = "2024-01-01"
        mock_message.plain = "Email body"
        mock_message.html = "<html><body>HTML content</body></html>"
        
        # Mock attachment
        mock_attachment = Mock()
        mock_attachment.filename = "receipt.pdf"
        mock_attachment.content_type = "application/pdf"
        mock_attachment.data = b"PDF data"
        mock_message.attachments = [mock_attachment]
        
        with patch.object(self.processor, 'process_attachment') as mock_process:
            mock_process.return_value = {
                'filename': 'receipt.pdf',
                'content_type': 'application/pdf',
                'size': 100,
                'text_content': 'PDF content',
                'csv_data': None
            }
            
            result = self.processor.extract_email_content(mock_message)
            
            self.assertEqual(result['subject'], "Test Email")
            self.assertEqual(result['sender'], "test@example.com")
            self.assertEqual(len(result['attachments']), 1)
            self.assertEqual(result['attachments'][0]['filename'], "receipt.pdf")

if __name__ == '__main__':
    unittest.main() 