import re
import email
import base64
import io
import PyPDF2
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from ..config import Config
import os

class EmailProcessor:
    def __init__(self):
        self.service = self._get_gmail_service()
        
    def _get_gmail_service(self):
        """Get Gmail service using credentials directly"""
        creds = None
        
        # Load existing token
        if Config.GMAIL_TOKEN_FILE and os.path.exists(Config.GMAIL_TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(Config.GMAIL_TOKEN_FILE, Config.GMAIL_SCOPES)
        
        # If no valid credentials, use credentials.json to get new token
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(Config.GMAIL_CREDENTIALS_FILE):
                    raise FileNotFoundError(f"Credentials file not found: {Config.GMAIL_CREDENTIALS_FILE}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.GMAIL_CREDENTIALS_FILE, Config.GMAIL_SCOPES)
                creds = flow.run_local_server(port=8080)
            
            # Save the credentials for next run
            if Config.GMAIL_TOKEN_FILE:
                with open(Config.GMAIL_TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    def is_financial_email(self, message_data: Dict) -> bool:
        """Check if email is from a financial service provider"""
        headers = message_data.get('payload', {}).get('headers', [])
        
        # Extract sender and subject from headers
        sender = ""
        subject = ""
        
        for header in headers:
            if header['name'].lower() == 'from':
                sender = header['value'].lower()
            elif header['name'].lower() == 'subject':
                subject = header['value'].lower()
        
        # Check sender patterns for financial services
        financial_senders = [
            'stripe.com', 'paypal.com', 'wise.com', 'bank.com',
            'receipt@', 'invoice@', 'payment@', 'billing@',
            'noreply@stripe.com', 'service@paypal.com',
            'noreply@', 'service@', 'notifications@', 'confirmation@', 'finops@',
            'finance@', 'accounting@', 'billing@'
        ]
        
        for pattern in financial_senders:
            if pattern in sender:
                return True
        
        # Check subject patterns for financial keywords
        financial_keywords = [
            'receipt', 'invoice', 'payment', 'transaction', 'charge',
            'billing', 'statement', 'confirmation', 'order', 'purchase',
            'transfer', 'withdrawal', 'deposit', 'refund', 'renewal',
            'subscription', 'fee', 'amount', 'total', 'balance',
            '$', '€', '£', 'usd', 'eur', 'gbp', 'sgd', 'hrs', 'hours'
        ]
        
        for keyword in financial_keywords:
            if keyword in subject:
                return True
        
        # Check if email has financial attachments
        if self._has_financial_attachments(message_data):
            return True
        
        # Additional check: Look for currency symbols or amounts in the email body
        try:
            body = self.extract_email_content(message_data)
            body_text = f"{body.get('body', '')} {body.get('html_body', '')}"
            
            # Look for currency symbols or amounts
            import re
            currency_patterns = [
                r'\$\d+\.?\d*',  # $100, $100.50
                r'€\d+\.?\d*',   # €100, €100.50
                r'£\d+\.?\d*',   # £100, £100.50
                r'SGD\s*\d+\.?\d*',  # SGD 100, SGD 100.50
                r'\d+\.?\d*\s*(USD|EUR|GBP|SGD)',  # 100 USD, 100.50 EUR
            ]
            
            for pattern in currency_patterns:
                if re.search(pattern, body_text, re.IGNORECASE):
                    return True
            
            # Check for attachment-related keywords that suggest financial documents
            attachment_keywords = [
                'invoice attached', 'receipt attached', 'statement attached',
                'bill attached', 'payment attached', 'document attached',
                'find attached', 'please find attached', 'see attached'
            ]
            
            for keyword in attachment_keywords:
                if keyword.lower() in body_text.lower():
                    return True
                    
        except Exception:
            pass
        
        return False
    
    def _has_financial_attachments(self, message_data: Dict) -> bool:
        """Check if email has financial-related attachments"""
        payload = message_data.get('payload', {})
        
        # Check for attachments in multipart messages
        if payload.get('mimeType') == 'multipart/mixed' or payload.get('mimeType') == 'multipart/alternative':
            parts = payload.get('parts', [])
            for part in parts:
                if part.get('filename'):
                    filename = part.get('filename', '').lower()
                    # Check for financial document patterns
                    financial_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.csv', '.xlsx', '.xls']
                    financial_keywords = ['invoice', 'receipt', 'statement', 'payment', 'bill', 'quote']
                    
                    # Check file extension
                    for ext in financial_extensions:
                        if ext in filename:
                            return True
                    
                    # Check filename keywords
                    for keyword in financial_keywords:
                        if keyword in filename:
                            return True
        
        return False
    
    def extract_pdf_text(self, pdf_data: bytes) -> str:
        """Extract text content from PDF attachment"""
        try:
            if not pdf_data:
                return ""
                
            pdf_file = io.BytesIO(pdf_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""
    
    def extract_csv_data(self, csv_data: bytes) -> List[Dict]:
        """Extract data from CSV attachment"""
        try:
            csv_text = csv_data.decode('utf-8')
            csv_file = io.StringIO(csv_text)
            reader = csv.DictReader(csv_file)
            return [row for row in reader]
        except Exception as e:
            print(f"Error extracting CSV data: {e}")
            return []
    
    def process_attachment(self, attachment_data: Dict) -> Dict:
        """Process a single attachment and extract its content"""
        attachment_info = {
            'filename': attachment_data.get('filename', 'unknown'),
            'content_type': attachment_data.get('mimeType', 'unknown'),
            'size': len(attachment_data.get('data', b'')),
            'text_content': '',
            'csv_data': None,
            'is_financial': False
        }
        
        # Check if this is a financial attachment
        filename = attachment_info['filename'].lower()
        financial_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.csv', '.xlsx', '.xls']
        financial_keywords = ['invoice', 'receipt', 'statement', 'payment', 'bill', 'quote']
        
        # Check file extension and filename
        for ext in financial_extensions:
            if ext in filename:
                attachment_info['is_financial'] = True
                break
        
        for keyword in financial_keywords:
            if keyword in filename:
                attachment_info['is_financial'] = True
                break
        
        # Decode attachment data
        try:
            data = base64.urlsafe_b64decode(attachment_data.get('data', ''))
        except Exception as e:
            print(f"Error decoding attachment data: {e}")
            return attachment_info
        
        # Handle different file types
        content_type = attachment_info['content_type']
        
        if content_type == 'application/pdf':
            attachment_info['text_content'] = self.extract_pdf_text(data)
            if attachment_info['text_content']:
                attachment_info['is_financial'] = True
        elif content_type == 'text/csv':
            attachment_info['csv_data'] = self.extract_csv_data(data)
            if attachment_info['csv_data']:
                attachment_info['is_financial'] = True
        elif content_type.startswith('text/'):
            try:
                attachment_info['text_content'] = data.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    attachment_info['text_content'] = data.decode('latin-1')
                except:
                    attachment_info['text_content'] = "Unable to decode text content"
        elif content_type.startswith('image/'):
            # For images, we'll mark as financial if filename suggests it
            # In a real implementation, you might use OCR here
            attachment_info['text_content'] = f"[Image file: {attachment_info['filename']}]"
        
        return attachment_info
    
    def extract_email_content(self, message_data: Dict) -> Dict:
        """Extract text content from email including attachments"""
        content = {
            'message_id': message_data['id'],
            'subject': '',
            'sender': '',
            'date': '',
            'body': '',
            'html_body': '',
            'attachments': [],
            'has_financial_attachments': False
        }
        
        # Extract headers
        headers = message_data.get('payload', {}).get('headers', [])
        for header in headers:
            if header['name'].lower() == 'subject':
                content['subject'] = header['value']
            elif header['name'].lower() == 'from':
                content['sender'] = header['value']
            elif header['name'].lower() == 'date':
                content['date'] = header['value']
        
        # Extract body content
        payload = message_data.get('payload', {})
        
        # Handle multipart messages
        if payload.get('mimeType') == 'multipart/mixed' or payload.get('mimeType') == 'multipart/alternative':
            parts = payload.get('parts', [])
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    try:
                        body_data = base64.urlsafe_b64decode(part.get('data', ''))
                        content['body'] = body_data.decode('utf-8')
                    except:
                        pass
                elif part.get('mimeType') == 'text/html':
                    try:
                        html_data = base64.urlsafe_b64decode(part.get('data', ''))
                        soup = BeautifulSoup(html_data.decode('utf-8'), 'html.parser')
                        # Remove scripts and styles
                        for script in soup(["script", "style"]):
                            script.decompose()
                        content['html_body'] = soup.get_text()
                    except:
                        pass
                elif part.get('filename'):  # Attachment
                    attachment_info = self.process_attachment(part)
                    content['attachments'].append(attachment_info)
                    if attachment_info['is_financial']:
                        content['has_financial_attachments'] = True
        else:
            # Simple text message
            try:
                body_data = base64.urlsafe_b64decode(payload.get('data', ''))
                if payload.get('mimeType') == 'text/html':
                    soup = BeautifulSoup(body_data.decode('utf-8'), 'html.parser')
                    for script in soup(["script", "style"]):
                        script.decompose()
                    content['html_body'] = soup.get_text()
                else:
                    content['body'] = body_data.decode('utf-8')
            except:
                pass
        
        return content
    
    def get_recent_financial_emails(self, days_back: int = 7) -> List[Dict]:
        """Fetch recent financial emails from Gmail using Gmail API"""
        # Calculate date for query
        date_after = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
        
        # Build query for recent emails
        query = f'after:{date_after}'
        
        try:
            # Get messages from Gmail API
            results = self.service.users().messages().list(
                userId='me', 
                q=query,
                maxResults=100  # Limit to recent emails
            ).execute()
            
            messages = results.get('messages', [])
            financial_emails = []
            
            for message in messages:
                # Get full message details
                msg = self.service.users().messages().get(
                    userId='me', 
                    id=message['id'],
                    format='full'
                ).execute()
                
                if self.is_financial_email(msg):
                    email_content = self.extract_email_content(msg)
                    financial_emails.append(email_content)
                    print(f"Found financial email: {email_content['subject']}")
                    
                    # Log attachment info
                    if email_content['has_financial_attachments']:
                        print(f"  📎 Has financial attachments")
                        for attachment in email_content['attachments']:
                            if attachment['is_financial']:
                                print(f"    - {attachment['filename']} ({attachment['content_type']})")
            
            print(f"Found {len(financial_emails)} financial emails from the last {days_back} days")
            return financial_emails
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def get_unprocessed_emails(self, db_session) -> List[Dict]:
        """Get emails that haven't been processed yet"""
        from ..db.models import FinancialTransaction
        
        # Get all processed email IDs
        processed_ids = db_session.query(FinancialTransaction.email_id).all()
        processed_ids = [row[0] for row in processed_ids]
        
        # Get recent financial emails
        recent_emails = self.get_recent_financial_emails()
        
        # Filter out already processed emails
        unprocessed_emails = [
            email for email in recent_emails 
            if email['message_id'] not in processed_ids
        ]
        
        return unprocessed_emails 