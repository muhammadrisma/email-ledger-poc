import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.app.services.email_processor import EmailProcessor
from src.app.services.ai_extractor import AIExtractor
from src.app.services.ledger_service import LedgerService
from src.app.db.models import FinancialTransaction

class TestEmailProcessor:
    def test_is_financial_email(self):
        processor = EmailProcessor()
        
        # Test financial email
        mock_message = Mock()
        mock_message.sender = "noreply@stripe.com"
        mock_message.subject = "Payment receipt"
        
        assert processor.is_financial_email(mock_message) == True
        
        # Test non-financial email
        mock_message.sender = "friend@example.com"
        mock_message.subject = "Hello there"
        
        assert processor.is_financial_email(mock_message) == False

class TestAIExtractor:
    @patch('src.app.services.ai_extractor.OpenAI')
    def test_extract_financial_data(self, mock_openai):
        extractor = AIExtractor()
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices[0].message.content = '''
        {
            "amount": 99.99,
            "currency": "USD",
            "vendor": "Stripe",
            "transaction_type": "debit",
            "reference_id": "txn_123",
            "description": "Payment for subscription",
            "confidence_score": 0.95
        }
        '''
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        email_content = {
            'subject': 'Payment receipt',
            'sender': 'noreply@stripe.com',
            'date': datetime.now(),
            'body': 'Your payment of $99.99 has been processed',
            'html_body': '<p>Payment processed</p>'
        }
        
        result = extractor.extract_financial_data(email_content)
        
        assert result['amount'] == 99.99
        assert result['currency'] == 'USD'
        assert result['vendor'] == 'Stripe'
        assert result['confidence_score'] == 0.95

class TestLedgerService:
    def test_save_transaction(self):
        service = LedgerService()
        
        email_content = {
            'message_id': 'test_123',
            'subject': 'Test payment',
            'sender': 'test@example.com',
            'date': datetime.now()
        }
        
        financial_data = {
            'amount': 50.00,
            'currency': 'USD',
            'vendor': 'Test Vendor',
            'transaction_type': 'debit',
            'reference_id': 'ref_123',
            'description': 'Test transaction',
            'confidence_score': 0.8
        }
        
        classification = {
            'category': 'other',
            'confidence_score': 0.7
        }
        
        # Mock database session
        mock_db = Mock()
        mock_transaction = Mock()
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        result = service.save_transaction(mock_db, email_content, financial_data, classification)
        
        assert mock_db.add.called
        assert mock_db.commit.called 