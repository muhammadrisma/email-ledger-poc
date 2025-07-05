import re
import json
from typing import Dict, Optional, List
from openai import OpenAI
from bs4 import BeautifulSoup
from ..config import Config
from ..prompts import FINANCIAL_EXTRACTION_PROMPT, EXPENSE_CLASSIFICATION_PROMPT

class AIExtractor:
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY environment variable or add it to your .env file.")
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
    def extract_financial_data(self, email_content: Dict) -> Dict:
        """
        Extract financial data from email using AI.
        
        Analyzes email content and attachments to extract transaction details
        including amounts, currency, vendor, dates, and reference information.
        
        Args:
            email_content: Dictionary containing email data including subject,
                         sender, body, HTML content, and attachments
                         
        Returns:
            Dictionary containing extracted financial data with keys:
            - date: Transaction date (YYYY-MM-DD format)
            - amount: Transaction amount (float or None)
            - currency: Currency code (USD, EUR, etc.)
            - vendor: Company/merchant name
            - transaction_type: "debit" or "credit"
            - reference_id: Transaction reference number
            - description: Transaction description
        """
        
        content = f"""
        Email Subject: {email_content['subject']}
        Sender: {email_content['sender']}
        Date: {email_content['date']}
        
        Email Body:
        {email_content['body']}
        
        HTML Content:
        {email_content['html_body']}
        """
        
        # Check if this is a forwarded email and include the full forwarded content
        if 'Fwd:' in email_content.get('subject', '') or 'Fw:' in email_content.get('subject', ''):
            body_text = f"{email_content.get('body', '')} {email_content.get('html_body', '')}"
            
            # Include the full forwarded email content
            content += f"\n\n=== FORWARDED EMAIL CONTENT ===\n"
            content += f"FULL FORWARDED EMAIL BODY:\n{body_text}\n"
            
            # Also extract specific patterns for debugging
            forwarded_patterns = [
                r'From:\s*([^\n]+)',
                r'Sent:\s*([^\n]+)',
                r'To:\s*([^\n]+)',
                r'Subject:\s*([^\n]+)',
                r'We charged\s+\$([\d,]+\.?\d*)',
                r'charged\s+\$([\d,]+\.?\d*)',
                r'credit card ending in (\d+)',
                r'funded your ([^.]*)',
            ]
            
            forwarded_info = []
            for pattern in forwarded_patterns:
                matches = re.findall(pattern, body_text, re.IGNORECASE)
                if matches:
                    forwarded_info.extend(matches)
            
            if forwarded_info:
                content += f"\nEXTRACTED FORWARDED PATTERNS: {forwarded_info}\n"
        
        if email_content.get('attachments'):
            content += "\n\n=== ATTACHMENTS ===\n"
            for i, attachment in enumerate(email_content['attachments'], 1):
                content += f"\n--- Attachment {i}: {attachment['filename']} ({attachment['content_type']}) ---\n"
                if attachment.get('is_financial'):
                    content += "  [FINANCIAL DOCUMENT - IMPORTANT TO EXTRACT DATA FROM]\n"
                
                if attachment.get('text_content'):
                    # Special handling for PDF content
                    if attachment.get('content_type') == 'application/pdf':
                        content += f"  PDF TEXT CONTENT (CRITICAL FOR EXTRACTION):\n"
                        content += f"  {attachment['text_content']}\n"
                    else:
                        content += f"  TEXT CONTENT:\n{attachment['text_content']}\n"
                
                if attachment.get('csv_data'):
                    content += f"  CSV DATA:\n{str(attachment['csv_data'])}\n"
                
                if attachment.get('content_type', '').startswith('image/'):
                    content += f"  [IMAGE FILE: {attachment['filename']} - May contain receipt/invoice]\n"
                
                content += "\n"
        
        # Use the imported prompt template
        prompt = FINANCIAL_EXTRACTION_PROMPT.format(content=content)
        
        print(f"DEBUG: Sending content to AI (first 500 chars): {content[:500]}...")
        print(f"DEBUG: Email body length: {len(email_content.get('body', ''))}")
        print(f"DEBUG: HTML body length: {len(email_content.get('html_body', ''))}")
        print(f"DEBUG: Number of attachments: {len(email_content.get('attachments', []))}")
        
        # Debug attachment content
        for i, attachment in enumerate(email_content.get('attachments', [])):
            print(f"DEBUG: Attachment {i+1}: {attachment.get('filename', 'unknown')}")
            print(f"DEBUG: Attachment content type: {attachment.get('content_type', 'unknown')}")
            print(f"DEBUG: Attachment text content length: {len(attachment.get('text_content', ''))}")
            if attachment.get('text_content'):
                print(f"DEBUG: Attachment text preview: {attachment['text_content'][:200]}...")
        
        # Debug full content for forwarded emails
        if 'Fwd:' in email_content.get('subject', '') or 'Fw:' in email_content.get('subject', ''):
            print(f"DEBUG: This is a forwarded email")
            print(f"DEBUG: Full content being sent to AI:")
            print(f"DEBUG: {content}")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial data extraction specialist. Extract ALL required fields: Date, Amount, Currency, Vendor, Transaction Type, Reference ID, and Description. Be thorough and extract from both email body, HTML tables, and attachments. If a field cannot be found, use null or empty string. For currency, look for symbols ($, €, £, SGD) or codes (USD, EUR, GBP, SGD) and use USD as default if none found. CRITICAL: If you find ANY amount mentioned in the email or attachments, extract it as a number. Do not return null for amount unless you are absolutely certain no amount is mentioned anywhere in the email or attachments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1200
            )
            
            result_text = response.choices[0].message.content.strip()
            print(f"AI Response: {result_text}")
            
            try:
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = json.loads(result_text)
                    
                print(f"DEBUG: AI returned JSON: {result}")
                print(f"DEBUG: Amount in AI response: {result.get('amount')}")
                validated_result = self._validate_extraction_result(result, email_content)
                print(f"DEBUG: Validated result: {validated_result}")
                return validated_result
                
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Raw response: {result_text}")
                return self._fallback_extraction(email_content)
                
        except Exception as e:
            print(f"Error in AI extraction: {e}")
            return self._fallback_extraction(email_content)
    
    def classify_expense(self, email_content: Dict, financial_data: Dict) -> Dict:
        """
        Classify the expense category using AI.
        
        Analyzes the financial transaction data and email content to determine
        the appropriate expense category for the transaction.
        
        Args:
            email_content: Dictionary containing email data
            financial_data: Dictionary containing extracted financial data
            
        Returns:
            Dictionary with classification result containing:
            - category: The classified expense category
        """
        
        content = f"""
        Email Subject: {email_content['subject']}
        Sender: {email_content['sender']}
        Vendor: {financial_data.get('vendor', '')}
        Description: {financial_data.get('description', '')}
        Amount: {financial_data.get('amount', '')} {financial_data.get('currency', '')}
        Reference ID: {financial_data.get('reference_id', '')}
        
        Email Body:
        {email_content['body']}
        """
        
        if email_content.get('attachments'):
            content += "\n\nAttachments:\n"
            for i, attachment in enumerate(email_content['attachments'], 1):
                content += f"\nAttachment {i}: {attachment['filename']} ({attachment['content_type']})\n"
                if attachment.get('text_content'):
                    content += f"Content: {attachment['text_content'][:1500]}...\n"
                if attachment.get('csv_data'):
                    content += f"CSV Data: {str(attachment['csv_data'][:5])}...\n"
        
        categories = ", ".join(Config.EXPENSE_CATEGORIES)
        
        # Use the imported prompt template
        prompt = EXPENSE_CLASSIFICATION_PROMPT.format(
            categories=categories,
            content=content
        )
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expense classification specialist. Classify expenses into appropriate categories based on vendor, description, and context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content.strip()
            
            try:
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = json.loads(result_text)
                    
                return {
                    "category": result.get("category", "other")
                }
                
            except json.JSONDecodeError:
                return {"category": "other"}
                
        except Exception as e:
            print(f"Error in classification: {e}")
            return {"category": "other"}
    
    def _validate_extraction_result(self, result: Dict, email_content: Dict) -> Dict:
        """
        Validate and clean the extraction result.
        
        Ensures all extracted financial data is in the correct format and
        provides fallback values when data is missing or invalid.
        
        Args:
            result: Raw extraction result from AI
            email_content: Original email content for fallback values
            
        Returns:
            Dictionary with validated and cleaned financial data
        """
        validated = {
            "date": None,
            "amount": None,
            "currency": "USD",
            "vendor": "",
            "transaction_type": "debit",
            "reference_id": "",
            "description": ""
        }
        
        if result.get("date"):
            try:
                date_str = str(result["date"])
                if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                    validated["date"] = date_str
                else:
                    validated["date"] = email_content.get('date', '')
            except:
                validated["date"] = email_content.get('date', '')
        else:
            validated["date"] = email_content.get('date', '')
        
        # Trust AI for amount extraction, only use regex as last resort
        if result.get("amount") is not None:
            try:
                validated["amount"] = float(result["amount"])
                print(f"DEBUG: Successfully extracted amount from AI: {validated['amount']}")
            except (ValueError, TypeError) as e:
                print(f"DEBUG: Error converting AI amount '{result['amount']}': {e}")
                validated["amount"] = None
        else:
            print(f"DEBUG: AI returned null amount, trying simple regex fallback")
            # Simple regex fallback for very obvious amount patterns
            text = f"{email_content.get('subject', '')} {email_content.get('body', '')} {email_content.get('html_body', '')}"
            for attachment in email_content.get('attachments', []):
                if attachment.get('text_content'):
                    text += f" {attachment['text_content']}"
            
            # Look for simple amount patterns
            amount_patterns = [
                r'\$([\d,]+\.?\d*)',
                r'charged\s+\$([\d,]+\.?\d*)',
                r'We charged\s+\$([\d,]+\.?\d*)',
                r'paid\s+\$([\d,]+\.?\d*)',
                r'payment\s+of\s+\$([\d,]+\.?\d*)',
                r'amount[:\s]*\$([\d,]+\.?\d*)',
                r'billed\s+\$([\d,]+\.?\d*)',
                r'Total[:\s]*\$?([\d,]+\.?\d*)',
                r'Amount[:\s]*\$?([\d,]+\.?\d*)',
            ]
            
            for pattern in amount_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    try:
                        amount_value = float(matches[0].replace(',', ''))
                        validated["amount"] = amount_value
                        print(f"DEBUG: Found amount via regex fallback: {amount_value}")
                        break
                    except Exception as e:
                        print(f"DEBUG: Error in regex fallback: {e}")
                        continue
            
            if validated["amount"] is None:
                print(f"DEBUG: No amount found in regex fallback")
                validated["amount"] = None
                
        currency = result.get("currency", "USD")
        if currency and currency.upper() in ["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "SEK", "NOK", "DKK", "SGD"]:
            validated["currency"] = currency.upper()
            print(f"DEBUG: Using AI currency: {validated['currency']}")
        else:
            validated["currency"] = "USD"
            print(f"DEBUG: Using default currency: USD")
            
        if result.get("vendor"):
            validated["vendor"] = str(result["vendor"])
        else:
            sender = email_content.get('sender', '')
            if '@' in sender:
                domain = sender.split('@')[1]
                validated["vendor"] = domain.split('.')[0].title()
            
        if result.get("transaction_type") in ["debit", "credit"]:
            validated["transaction_type"] = result["transaction_type"]
            
        if result.get("reference_id"):
            validated["reference_id"] = str(result["reference_id"])
            
        if result.get("description"):
            validated["description"] = str(result["description"])
        else:
            validated["description"] = email_content.get('subject', '')
                
        return validated
    

    
    def _fallback_extraction(self, email_content: Dict) -> Dict:
        """
        Fallback extraction using pattern matching and HTML table parsing.
        
        Used when AI extraction fails to parse JSON. Performs regex-based
        pattern matching to extract financial data from email content and
        attachments.
        
        Args:
            email_content: Dictionary containing email data and attachments
            
        Returns:
            Dictionary with extracted financial data using pattern matching
        """
        text_parts = [
            email_content.get('subject', ''),
            email_content.get('body', ''),
            email_content.get('html_body', '')
        ]
        
        # For forwarded emails, prioritize the forwarded content
        if 'Fwd:' in email_content.get('subject', '') or 'Fw:' in email_content.get('subject', ''):
            # Look for forwarded email content patterns
            body_text = f"{email_content.get('body', '')} {email_content.get('html_body', '')}"
            forwarded_patterns = [
                r'From:\s*([^\n]+)',
                r'Sent:\s*([^\n]+)',
                r'To:\s*([^\n]+)',
                r'Subject:\s*([^\n]+)',
                r'Hi\s+([^,]+),',
                r'We charged\s+\$([\d,]+\.?\d*)',
                r'charged\s+\$([\d,]+\.?\d*)',
                r'credit card ending in (\d+)',
                r'funded your ([^.]*)',
            ]
            
            for pattern in forwarded_patterns:
                matches = re.findall(pattern, body_text, re.IGNORECASE)
                if matches:
                    text_parts.insert(0, ' '.join(matches))
        
        for attachment in email_content.get('attachments', []):
            if attachment.get('text_content'):
                # For financial documents, prioritize attachment content
                attachment_text = attachment['text_content']
                # Look for amount patterns in attachment text
                amount_matches = re.findall(r'[\$€£]?\s*([\d,]+\.?\d*)\s*(USD|EUR|GBP|SGD)?', attachment_text, re.IGNORECASE)
                if amount_matches:
                    text_parts.insert(0, attachment_text)
                else:
                    text_parts.append(attachment_text)
            if attachment.get('csv_data'):
                csv_text = str(attachment['csv_data'])
                text_parts.insert(0, csv_text)
        
        text = " ".join(text_parts)
        
        # Simplified fallback - just extract basic info without complex regex
        amount = None
        currency = "USD"
        vendor = ""
        description = email_content.get('subject', '')
        reference_id = ""
        date = email_content.get('date', '')
        transaction_type = "debit"
        
        # Simple vendor extraction from sender
        sender = email_content.get('sender', '')
        if '@' in sender:
            domain = sender.split('@')[1]
            parts = domain.split('.')
            if len(parts) >= 2:
                company_part = parts[0] if parts[0] not in ['www', 'mail', 'smtp', 'finops', 'noreply', 'service'] else parts[1]
                vendor = company_part.title()
            else:
                vendor = parts[0].title()
                        
        # For forwarded emails, try to extract vendor from original sender
        if 'Fwd:' in email_content.get('subject', '') or 'Fw:' in email_content.get('subject', ''):
            body_text = f"{email_content.get('body', '')} {email_content.get('html_body', '')}"
            from_match = re.search(r'From:\s*([^\n]+)', body_text, re.IGNORECASE)
            if from_match:
                original_sender = from_match.group(1)
                if '@' in original_sender:
                    original_domain = original_sender.split('@')[1]
                    if 'openai' in original_domain.lower():
                        vendor = 'OpenAI'
                    elif 'stripe' in original_domain.lower():
                        vendor = 'Stripe'
                    elif 'paypal' in original_domain.lower():
                        vendor = 'PayPal'
                    else:
                        parts = original_domain.split('.')
                        if len(parts) >= 2:
                            company_part = parts[0] if parts[0] not in ['www', 'mail', 'smtp', 'noreply', 'service'] else parts[1]
                            vendor = company_part.title()
                        else:
                            vendor = parts[0].title()
                
        match = re.search(r'Customer Number[:#]?\s*(\w+)', text, re.IGNORECASE)
        if match:
            reference_id = match.group(1)
            
        return {
            "date": date,
            "amount": amount,
            "currency": currency,
            "vendor": vendor,
            "transaction_type": transaction_type,
            "reference_id": reference_id,
            "description": description
        } 