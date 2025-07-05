import time
import logging
from datetime import datetime
from typing import List, Dict
from ..services.email_processor import EmailProcessor
from ..services.ai_extractor import AIExtractor
from ..services.ledger_service import LedgerService
from ..db.models import get_db, create_tables
from ..config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmailLedgerProcessor: 
    def __init__(self):
        """
        Initialize the Email Ledger Processor.
        
        Sets up the email processor, AI extractor, and ledger service
        components needed for processing financial emails.
        """
        self.email_processor = EmailProcessor()
        self.ai_extractor = AIExtractor()
        self.ledger_service = LedgerService()
        
    def process_emails(self) -> Dict:
        """
        Process emails and extract financial data.
        
        Fetches unprocessed emails from Gmail, extracts financial information
        using AI, and saves transactions to the database.
        
        Returns:
            Dictionary containing processing statistics:
            - processed_count: Number of emails processed
            - successful_extractions: Number of successful financial extractions
            - timestamp: Processing completion timestamp
        """
        logger.info("Starting email processing...")
        
        try:
            db = next(get_db())
            
            unprocessed_emails = self.email_processor.get_unprocessed_emails(db)
            logger.info(f"Found {len(unprocessed_emails)} unprocessed emails")
            
            processed_count = 0
            successful_extractions = 0
            
            for email_content in unprocessed_emails:
                try:
                    logger.info(f"Processing email: {email_content['subject']}")
                    
                    financial_data = self.ai_extractor.extract_financial_data(email_content)
                    logger.info(f"Extracted financial data: {financial_data}")
                    
                    has_financial_data = (
                        financial_data.get('amount') is not None or
                        (financial_data.get('vendor') and any(keyword in financial_data.get('vendor', '').lower() 
                         for keyword in ['stripe', 'paypal', 'wise', 'bank', 'payment', 'invoice', 'receipt', 'billing'])) or
                        any(keyword in email_content.get('subject', '').lower() 
                            for keyword in ['invoice', 'receipt', 'bill', 'payment']) or
                        any(keyword in email_content.get('body', '').lower() 
                            for keyword in ['invoice attached', 'receipt attached', 'bill attached'])
                    )
                    
                    if has_financial_data:
                        classification = self.ai_extractor.classify_expense(email_content, financial_data)
                        logger.info(f"Classification: {classification}")
                        
                        transaction = self.ledger_service.save_transaction(
                            db, email_content, financial_data, classification
                        )
                        
                        logger.info(f"Saved transaction: {transaction.amount} {transaction.currency} - {transaction.vendor}")
                        successful_extractions += 1
                    else:
                        logger.info(f"No meaningful financial data found in email: {email_content['subject']}")
                        logger.info(f"Email content preview: {email_content.get('body', '')[:200]}...")
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing email {email_content.get('message_id', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Processing complete. Processed: {processed_count}, Successful: {successful_extractions}")
            
            return {
                "processed_count": processed_count,
                "successful_extractions": successful_extractions,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in email processing: {e}")
            raise
        finally:
            db.close()
    
    def run_continuous_processing(self):
        """
        Run continuous email processing.
        
        Continuously processes emails at regular intervals defined by
        Config.EMAIL_POLL_INTERVAL. Handles interruptions gracefully.
        """
        logger.info("Starting continuous email processing...")
        
        while True:
            try:
                self.process_emails()
                logger.info(f"Sleeping for {Config.EMAIL_POLL_INTERVAL} seconds...")
                time.sleep(Config.EMAIL_POLL_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Stopping continuous processing...")
                break
            except Exception as e:
                logger.error(f"Error in continuous processing: {e}")
                time.sleep(60) 