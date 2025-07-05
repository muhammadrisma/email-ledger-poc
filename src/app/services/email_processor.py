import re
import email
import base64
import io
import PyPDF2
import csv
import tempfile
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from ..config import Config

class EmailProcessor:
    def __init__(self):
        self.service = self._get_gmail_service()
        
    def _get_gmail_service(self):
        """Get Gmail service using credentials directly"""
        creds = None
        
        if Config.GMAIL_TOKEN_FILE and os.path.exists(Config.GMAIL_TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(Config.GMAIL_TOKEN_FILE, Config.GMAIL_SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(Config.GMAIL_CREDENTIALS_FILE):
                    raise FileNotFoundError(f"Credentials file not found: {Config.GMAIL_CREDENTIALS_FILE}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.GMAIL_CREDENTIALS_FILE, Config.GMAIL_SCOPES)
                creds = flow.run_local_server(port=8080)
            
            if Config.GMAIL_TOKEN_FILE:
                with open(Config.GMAIL_TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    def is_financial_email(self, message_data: Dict) -> bool:
        """Check if email is from a financial service provider"""
        headers = message_data.get('payload', {}).get('headers', [])
        
        sender = ""
        subject = ""
        
        for header in headers:
            if header['name'].lower() == 'from':
                sender = header['value'].lower()
            elif header['name'].lower() == 'subject':
                subject = header['value'].lower()
        
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
        
        financial_keywords = [
            'receipt', 'invoice', 'payment', 'transaction', 'charge',
            'billing', 'statement', 'confirmation', 'order', 'purchase',
            'transfer', 'withdrawal', 'deposit', 'refund', 'renewal',
            'subscription', 'fee', 'amount', 'total', 'balance',
            '$', '€', '£', 'usd', 'eur', 'gbp', 'sgd', 'hrs', 'hours',
            'funded', 'charged', 'credit card', 'api account'
        ]
        
        for keyword in financial_keywords:
            if keyword in subject:
                return True
        
        if self._has_financial_attachments(message_data):
            return True
        
        try:
            body = self.extract_email_content(message_data)
            body_text = f"{body.get('body', '')} {body.get('html_body', '')}"
            
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
        
        if payload.get('mimeType') == 'multipart/mixed' or payload.get('mimeType') == 'multipart/alternative':
            parts = payload.get('parts', [])
            for part in parts:
                if part.get('filename'):
                    filename = part.get('filename', '').lower()
                    financial_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.csv', '.xlsx', '.xls']
                    financial_keywords = ['invoice', 'receipt', 'statement', 'payment', 'bill', 'quote']
                    
                    for ext in financial_extensions:
                        if ext in filename:
                            return True
                    
                    for keyword in financial_keywords:
                        if keyword in filename:
                            return True
        
        return False
    
    def extract_pdf_text(self, pdf_data: bytes) -> str:
        """Extract text content from PDF attachment with enhanced processing"""
        try:
            if not pdf_data:
                return ""
            
            print(f"DEBUG: Processing PDF with {len(pdf_data)} bytes")
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(pdf_data)
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    
                    print(f"DEBUG: PDF has {len(pdf_reader.pages)} pages")
                    
                    text = ""
                    for page_num, page in enumerate(pdf_reader.pages):
                        try:
                            page_text = page.extract_text()
                            if page_text:
                                text += f"\n--- Page {page_num + 1} ---\n"
                                text += page_text + "\n"
                                print(f"DEBUG: Extracted {len(page_text)} characters from page {page_num + 1}")
                            else:
                                print(f"DEBUG: No text found on page {page_num + 1}")
                        except Exception as e:
                            print(f"DEBUG: Error extracting text from page {page_num + 1}: {e}")
                            continue
                
                if text:
                    print(f"DEBUG: Successfully extracted PDF text: {len(text)} total characters")
                    print(f"DEBUG: PDF text preview: {text[:300]}...")
                else:
                    print(f"DEBUG: No text extracted from PDF")
                
                return text
                
            finally:
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    print(f"DEBUG: Error cleaning up temp file: {e}")
                    
        except Exception as e:
            print(f"DEBUG: Error extracting PDF text: {e}")
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
    
    def save_attachment_to_temp(self, data: bytes, filename: str) -> str:
        """
        Save attachment data to a temporary file.
        
        Args:
            data: Attachment data as bytes
            filename: Original filename for extension
            
        Returns:
            Path to temporary file
        """
        _, ext = os.path.splitext(filename)
        if not ext:
            ext = '.tmp'
        
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
            temp_file.write(data)
            return temp_file.name
    
    def cleanup_temp_file(self, temp_path: str):
        """Clean up temporary file"""
        try:
            os.unlink(temp_path)
        except:
            pass

    def process_attachment(self, attachment_data: Dict) -> Dict:
        """Process a single attachment and extract its content with enhanced PDF handling"""
        attachment_info = {
            'filename': attachment_data.get('filename', 'unknown'),
            'content_type': attachment_data.get('content_type', attachment_data.get('mimeType', 'unknown')),
            'size': attachment_data.get('size', 0),
            'text_content': '',
            'csv_data': None,
            'is_financial': False
        }
        
        # Check if this is a financial attachment
        filename = attachment_info['filename'].lower()
        financial_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.csv', '.xlsx', '.xls']
        financial_keywords = ['invoice', 'receipt', 'statement', 'payment', 'bill', 'quote', 'transaction']
        
        # Check file extension and filename
        for ext in financial_extensions:
            if ext in filename:
                attachment_info['is_financial'] = True
                break
        
        for keyword in financial_keywords:
            if keyword in filename:
                attachment_info['is_financial'] = True
                break
        
        data = attachment_data.get('data', b'')
        
        if isinstance(data, str):
            try:
                data = base64.urlsafe_b64decode(data)
                print(f"DEBUG: Decoded base64 attachment data: {len(data)} bytes")
            except Exception as e:
                print(f"DEBUG: Error decoding attachment data: {e}")
                data = b''
        
        print(f"DEBUG: Processing attachment: {attachment_info['filename']}")
        print(f"DEBUG: Attachment size: {len(data)} bytes")
        print(f"DEBUG: Content type: {attachment_info['content_type']}")
        print(f"DEBUG: Is financial: {attachment_info['is_financial']}")
        
        if not data:
            print(f"DEBUG: No data found in attachment")
            return attachment_info
        
        content_type = attachment_info['content_type']
        temp_file_path = None
        
        try:
            if content_type == 'application/pdf':
                print(f"DEBUG: Processing PDF attachment: {attachment_info['filename']}")
                attachment_info['text_content'] = self.extract_pdf_text(data)
                if attachment_info['text_content']:
                    attachment_info['is_financial'] = True
                    print(f"DEBUG: Successfully extracted PDF text: {len(attachment_info['text_content'])} characters")
                    print(f"DEBUG: PDF text preview: {attachment_info['text_content'][:500]}...")
                else:
                    print(f"DEBUG: Failed to extract text from PDF")
            elif content_type == 'text/csv':
                print(f"DEBUG: Processing CSV attachment: {attachment_info['filename']}")
                attachment_info['csv_data'] = self.extract_csv_data(data)
                if attachment_info['csv_data']:
                    attachment_info['is_financial'] = True
                    print(f"DEBUG: Extracted CSV data: {len(attachment_info['csv_data'])} rows")
                    print(f"DEBUG: CSV preview: {str(attachment_info['csv_data'][:3])}")
            elif content_type.startswith('text/'):
                print(f"DEBUG: Processing text attachment: {attachment_info['filename']}")
                try:
                    attachment_info['text_content'] = data.decode('utf-8')
                    print(f"DEBUG: Extracted text content: {len(attachment_info['text_content'])} characters")
                    print(f"DEBUG: Text preview: {attachment_info['text_content'][:300]}...")
                except UnicodeDecodeError:
                    try:
                        attachment_info['text_content'] = data.decode('latin-1')
                        print(f"DEBUG: Extracted text content (latin-1): {len(attachment_info['text_content'])} characters")
                    except:
                        attachment_info['text_content'] = "Unable to decode text content"
                        print(f"DEBUG: Failed to decode text content")
            elif content_type.startswith('image/'):
                print(f"DEBUG: Processing image attachment: {attachment_info['filename']}")
                attachment_info['text_content'] = f"[Image file: {attachment_info['filename']}]"
                print(f"DEBUG: Image file detected: {attachment_info['filename']}")
            else:
                print(f"DEBUG: Processing unknown file type: {attachment_info['filename']}")
                try:
                    attachment_info['text_content'] = data.decode('utf-8')
                    print(f"DEBUG: Extracted unknown file type as text: {len(attachment_info['text_content'])} characters")
                except:
                    attachment_info['text_content'] = f"[Binary file: {attachment_info['filename']}]"
                    print(f"DEBUG: Binary file detected: {attachment_info['filename']}")
        
        except Exception as e:
            print(f"DEBUG: Error processing attachment {attachment_info['filename']}: {e}")
            attachment_info['text_content'] = f"[Error processing file: {str(e)}]"
        
        finally:
            if temp_file_path:
                self.cleanup_temp_file(temp_file_path)
        
        return attachment_info
    
    def _extract_text_from_parts(self, parts: List[Dict], content: Dict) -> None:
        """
        Recursively extract text content from multipart message parts.
        
        Args:
            parts: List of message parts
            content: Dictionary to store extracted content
        """
        for i, part in enumerate(parts):
            print(f"DEBUG: Processing part {i}: mimeType={part.get('mimeType')}, filename={part.get('filename')}")
            
            if part.get('mimeType') == 'text/plain':
                try:
                    body_data = base64.urlsafe_b64decode(part.get('data', ''))
                    content['body'] = body_data.decode('utf-8')
                    print(f"DEBUG: Extracted plain text body: {content['body'][:200]}...")
                except Exception as e:
                    print(f"DEBUG: Error extracting plain text: {e}")
            elif part.get('mimeType') == 'text/html':
                try:
                    html_data = base64.urlsafe_b64decode(part.get('data', ''))
                    soup = BeautifulSoup(html_data.decode('utf-8'), 'html.parser')
                    for script in soup(["script", "style"]):
                        script.decompose()
                    content['html_body'] = soup.get_text()
                    print(f"DEBUG: Extracted HTML body: {content['html_body'][:200]}...")
                except Exception as e:
                    print(f"DEBUG: Error extracting HTML: {e}")
            elif part.get('filename'):  # Attachment
                attachment_info = self.process_attachment(part)
                content['attachments'].append(attachment_info)
                if attachment_info['is_financial']:
                    content['has_financial_attachments'] = True
            elif part.get('mimeType') in ['multipart/alternative', 'multipart/mixed', 'multipart/related']:
                print(f"DEBUG: Found nested multipart: {part.get('mimeType')}")
                nested_parts = part.get('parts', [])
                self._extract_text_from_parts(nested_parts, content)

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
        
        headers = message_data.get('payload', {}).get('headers', [])
        for header in headers:
            if header['name'].lower() == 'subject':
                content['subject'] = header['value']
            elif header['name'].lower() == 'from':
                content['sender'] = header['value']
            elif header['name'].lower() == 'date':
                content['date'] = header['value']
        
        try:
            raw_message = self.service.users().messages().get(
                userId='me',
                id=message_data['id'],
                format='raw'
            ).execute()
            
            import base64
            raw_data = base64.urlsafe_b64decode(raw_message['raw'])
            email_message = email.message_from_bytes(raw_data)
            
            body_parts = []
            html_parts = []
            
            def extract_parts(part):
                if part.is_multipart():
                    for subpart in part.get_payload():
                        extract_parts(subpart)
                else:
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        try:
                            text = part.get_payload(decode=True).decode('utf-8')
                            body_parts.append(text)
                        except:
                            pass
                    elif content_type == 'text/html':
                        try:
                            html = part.get_payload(decode=True).decode('utf-8')
                            soup = BeautifulSoup(html, 'html.parser')
                            for script in soup(["script", "style"]):
                                script.decompose()
                            html_parts.append(soup.get_text())
                        except:
                            pass
                    elif part.get_filename():  # Attachment
                        try:
                            filename = part.get_filename()
                            attachment_data = part.get_payload(decode=True)
                            
                            attachment_info = {
                                'filename': filename,
                                'content_type': part.get_content_type(),
                                'data': attachment_data,
                                'size': len(attachment_data) if attachment_data else 0
                            }
                            
                            processed_attachment = self.process_attachment(attachment_info)
                            content['attachments'].append(processed_attachment)
                            
                            if processed_attachment['is_financial']:
                                content['has_financial_attachments'] = True
                                
                            print(f"DEBUG: Processed attachment: {filename}")
                            print(f"DEBUG: Attachment text content length: {len(processed_attachment.get('text_content', ''))}")
                            
                        except Exception as e:
                            print(f"DEBUG: Error processing attachment: {e}")
            
            extract_parts(email_message)
            
            content['body'] = '\n'.join(body_parts)
            content['html_body'] = '\n'.join(html_parts)
            
            print(f"DEBUG: Extracted body length: {len(content['body'])}")
            print(f"DEBUG: Extracted HTML length: {len(content['html_body'])}")
            if content['body']:
                print(f"DEBUG: Body preview: {content['body'][:300]}...")
            if content['html_body']:
                print(f"DEBUG: HTML preview: {content['html_body'][:300]}...")
                
        except Exception as e:
            print(f"DEBUG: Error extracting raw email content: {e}")
            payload = message_data.get('payload', {})
            if payload.get('mimeType') == 'multipart/mixed' or payload.get('mimeType') == 'multipart/alternative':
                parts = payload.get('parts', [])
                self._extract_text_from_parts(parts, content)
            else:
                try:
                    body_data = base64.urlsafe_b64decode(payload.get('data', ''))
                    if payload.get('mimeType') == 'text/html':
                        soup = BeautifulSoup(body_data.decode('utf-8'), 'html.parser')
                        for script in soup(["script", "style"]):
                            script.decompose()
                        content['html_body'] = soup.get_text()
                    else:
                        content['body'] = body_data.decode('utf-8')
                except Exception as e:
                    print(f"DEBUG: Error extracting simple text: {e}")
        
        return content
    
    def get_recent_financial_emails(self, days_back: int = 7) -> List[Dict]:
        """Fetch recent financial emails from Gmail using Gmail API"""
        date_after = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
        
        query = f'after:{date_after}'
        
        try:
            results = self.service.users().messages().list(
                userId='me', 
                q=query,
                maxResults=100  # Limit to recent emails
            ).execute()
            
            messages = results.get('messages', [])
            financial_emails = []
            
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', 
                    id=message['id'],
                    format='full'
                ).execute()
                
                if self.is_financial_email(msg):
                    email_content = self.extract_email_content(msg)
                    financial_emails.append(email_content)
                    print(f"Found financial email: {email_content['subject']}")
                    
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

    def get_recent_emails(self, email_count: int = 10) -> List[Dict]:
        """
        Fetch a specific number of recent emails from Gmail.
        
        Args:
            email_count: Number of recent emails to fetch (1-100)
            
        Returns:
            List of email content dictionaries
        """
        try:
            results = self.service.users().messages().list(
                userId='me', 
                maxResults=email_count
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', 
                    id=message['id'],
                    format='full'
                ).execute()
                
                email_content = self.extract_email_content(msg)
                emails.append(email_content)
                print(f"Found email: {email_content['subject']}")
                
                if email_content['has_financial_attachments']:
                    print(f"  📎 Has financial attachments")
                    for attachment in email_content['attachments']:
                        if attachment['is_financial']:
                            print(f"    - {attachment['filename']} ({attachment['content_type']})")
            
            print(f"Found {len(emails)} recent emails")
            return emails
            
        except Exception as e:
            print(f"Error fetching recent emails: {e}")
            return []
    
    def get_unprocessed_emails(self, db_session) -> List[Dict]:
        """Get emails that haven't been processed yet"""
        from ..db.models import FinancialTransaction
        
        processed_ids = db_session.query(FinancialTransaction.email_id).all()
        processed_ids = [row[0] for row in processed_ids]
        
        recent_emails = self.get_recent_financial_emails()
        
        unprocessed_emails = [
            email for email in recent_emails 
            if email['message_id'] not in processed_ids
        ]
        
        return unprocessed_emails 