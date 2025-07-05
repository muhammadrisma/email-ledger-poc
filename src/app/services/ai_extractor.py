import re
import json
from typing import Dict, Optional, List
from openai import OpenAI
from bs4 import BeautifulSoup
from ..config import Config

class AIExtractor:
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required")
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
        
        if email_content.get('attachments'):
            content += "\n\n=== ATTACHMENTS ===\n"
            for i, attachment in enumerate(email_content['attachments'], 1):
                content += f"\n--- Attachment {i}: {attachment['filename']} ({attachment['content_type']}) ---\n"
                if attachment.get('is_financial'):
                    content += "  [FINANCIAL DOCUMENT - IMPORTANT TO EXTRACT DATA FROM]\n"
                
                if attachment.get('text_content'):
                    content += f"  TEXT CONTENT:\n{attachment['text_content']}\n"
                
                if attachment.get('csv_data'):
                    content += f"  CSV DATA:\n{str(attachment['csv_data'])}\n"
                
                if attachment.get('content_type', '').startswith('image/'):
                    content += f"  [IMAGE FILE: {attachment['filename']} - May contain receipt/invoice]\n"
                
                content += "\n"
        
        # Create the prompt for financial data extraction
        prompt = f"""
        Extract ALL financial transaction data from the following email and attachments.
        
        REQUIRED FIELDS TO EXTRACT:
        1. Date: Transaction date (from email date or document date)
        2. Amount: Payment/transaction amount (look for numbers with currency symbols)
        3. Currency: Currency code (USD, EUR, GBP, SGD, etc.) - look for currency symbols ($, €, £, SGD, etc.) or currency codes
        4. Vendor: Company/merchant name
        5. Transaction Type: "debit" (money going out) or "credit" (money coming in)
        6. Reference ID: Order number, invoice number, transaction ID, or reference
        7. Description: Clear description of what the transaction is for
        
        CRITICAL: PROCESS ALL ATTACHMENTS CAREFULLY
        - PDF attachments often contain the most important financial data
        - CSV files may contain transaction details
        - Image files (PNG, JPG) may be receipts or invoices
        - Extract amounts, dates, and vendor information from ALL attachments
        - If email body is empty or unclear, focus on attachment content
        - For invoice emails, the attachment usually contains the actual financial data
        
        SPECIAL INSTRUCTIONS FOR INVOICE EMAILS:
        - When email mentions "invoice attached" or similar, focus on attachment content
        - Extract vendor name from sender domain or attachment content
        - Look for invoice numbers, reference IDs in attachments
        - Extract total amount from attachment (not email body)
        - Use invoice date from attachment if available
        
        SPECIAL INSTRUCTIONS FOR HTML EMAILS:
        - If the email contains a table (like a receipt or invoice), extract the line items, subtotal, tax, and total from the table.
        - Use the total as the transaction amount.
        - Extract the currency from the price column or total (e.g., SGD, USD, etc.).
        - If the payment method and last digits are present, include them in the description.
        - Use the vendor from the sender or the logo/company name in the email.
        - If a customer number or reference is present, use it as the reference ID.
        
        CURRENCY DETECTION:
        - Look for currency symbols: $ (USD), € (EUR), £ (GBP), SGD, etc.
        - Look for currency codes: USD, EUR, GBP, SGD, etc.
        - Look for currency words: dollars, euros, pounds, etc.
        - If no currency is found, use USD as default
        
        AMOUNT DETECTION:
        - Look for amounts in various formats ($100, 100 USD, €50, SGD 95.90, etc.)
        - Check for "Total:", "Amount:", "Subtotal:", "Grand Total:" followed by numbers
        - Look for amounts in tables, especially in the last row or "Total" row
        - Check both email body AND all attachments for amounts
        - For invoices, look for "Total Due:", "Amount Due:", "Invoice Total:"
        
        VENDOR DETECTION:
        - Extract from sender domain (e.g., finops@earlybirdapp.co -> Earlybird)
        - Look for company names in attachment content
        - Check for vendor information in invoice headers
        
        IMPORTANT: 
        - Process ALL attachments thoroughly - they often contain the financial data
        - For invoice emails, the attachment is the primary source of financial data
        - Extract vendor from sender domain or document content
        - Determine transaction type based on context (invoice = debit, payment = debit, refund = credit)
        - Find reference numbers (Order #123, Invoice #456, etc.)
        - If multiple amounts found, use the largest/total amount
        - For invoice emails, use "invoice" as transaction type if unclear
        
        Return the data in JSON format with the following structure:
        {{
            "date": "YYYY-MM-DD or null",
            "amount": float or null,
            "currency": "USD" or other currency code,
            "vendor": "company name",
            "transaction_type": "debit" or "credit",
            "reference_id": "transaction reference",
            "description": "transaction description"
        }}
        
        Email content:
        {content}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial data extraction specialist. Extract ALL required fields: Date, Amount, Currency, Vendor, Transaction Type, Reference ID, and Description. Be thorough and extract from both email body, HTML tables, and attachments. If a field cannot be found, use null or empty string. For currency, look for symbols ($, €, £, SGD) or codes (USD, EUR, GBP, SGD) and use USD as default if none found."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
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
                    
                print(f"Parsed JSON: {result}")
                validated_result = self._validate_extraction_result(result, email_content)
                print(f"Validated result: {validated_result}")
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
        
        prompt = f"""
        Classify this expense into one of the following categories:
        {categories}
        
        Consider the vendor name, description, amount, and email content to determine the most appropriate category.
        
        Categories explained:
        - meals_and_entertainment: Food, restaurants, entertainment
        - transport: Uber, Lyft, gas, parking, public transport
        - saas_subscriptions: Software subscriptions, online services
        - travel: Flights, hotels, travel expenses
        - office_supplies: Office materials, equipment
        - utilities: Electricity, water, internet, phone bills
        - insurance: Insurance payments
        - professional_services: Legal, consulting, professional fees
        - marketing: Advertising, marketing expenses
        - other: Anything that doesn't fit above categories
        
        Return the result in JSON format:
        {{
            "category": "category_name"
        }}
        
        Content to classify:
        {content}
        """
        
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
        
        if result.get("amount") is not None:
            try:
                validated["amount"] = float(result["amount"])
            except (ValueError, TypeError):
                pass
                
        currency = result.get("currency", "USD")
        if currency and currency.upper() in ["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "SEK", "NOK", "DKK"]:
            validated["currency"] = currency.upper()
        else:
            text = f"{email_content.get('subject', '')} {email_content.get('body', '')} {email_content.get('html_body', '')}"
            detected_currency = self._detect_currency_from_text(text)
            validated["currency"] = detected_currency
            
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
    
    def _detect_currency_from_text(self, text: str) -> str:
        """
        Detect currency from text using pattern matching.
        
        Searches for currency symbols, codes, and words in the given text
        to determine the appropriate currency code.
        
        Args:
            text: Text content to search for currency indicators
            
        Returns:
            Currency code (USD, EUR, GBP, etc.) or USD as default
        """
        text = text.upper()
        
        currency_patterns = [
            (r'\$', 'USD'),
            (r'€', 'EUR'),
            (r'£', 'GBP'),
            (r'C\$', 'CAD'),
            (r'A\$', 'AUD'),
            (r'¥', 'JPY'),
            (r'CHF', 'CHF'),
            (r'SEK', 'SEK'),
            (r'NOK', 'NOK'),
            (r'DKK', 'DKK'),
        ]
        
        for pattern, currency in currency_patterns:
            if re.search(pattern, text):
                return currency
        
        currency_codes = ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CHF', 'SEK', 'NOK', 'DKK']
        for code in currency_codes:
            if re.search(rf'\b{code}\b', text):
                return code
        
        currency_words = {
            'DOLLAR': 'USD',
            'EURO': 'EUR',
            'POUND': 'GBP',
            'YEN': 'JPY',
            'FRANC': 'CHF',
            'KRONA': 'SEK',
            'KRONE': 'NOK',
            'KRONE': 'DKK',
        }
        
        for word, currency in currency_words.items():
            if word in text:
                return currency
        
        return "USD"
    
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
        
        for attachment in email_content.get('attachments', []):
            if attachment.get('text_content'):
                text_parts.insert(0, attachment['text_content'])
            if attachment.get('csv_data'):
                csv_text = str(attachment['csv_data'])
                text_parts.insert(0, csv_text)
        
        text = " ".join(text_parts)
        
        html = email_content.get('html_body', '')
        amount = None
        currency = "USD"
        vendor = ""
        description = email_content.get('subject', '')
        reference_id = ""
        date = email_content.get('date', '')
        transaction_type = "debit"
        
        for attachment in email_content.get('attachments', []):
            if attachment.get('text_content') and not amount:
                attachment_text = attachment['text_content']
                amount_match = re.search(r'(?:Total|Amount|Subtotal|Grand Total)[:\s]*([\d,]+\.?\d*)', attachment_text, re.IGNORECASE)
                if amount_match:
                    try:
                        amount = float(amount_match.group(1).replace(',', ''))
                    except Exception:
                        pass
                
                currency_match = re.search(r'(SGD|USD|EUR|GBP|\$|€|£)', attachment_text, re.IGNORECASE)
                if currency_match:
                    currency = currency_match.group(1).replace('$', 'USD').replace('€', 'EUR').replace('£', 'GBP')
        
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            for row in soup.find_all('tr'):
                cells = [c.get_text(strip=True) for c in row.find_all(['td', 'th'])]
                if any('total' in cell.lower() for cell in cells):
                    for cell in cells:
                        match = re.search(r'(SGD|USD|EUR|GBP|\$|€|£)\s?([\d,.]+)', cell, re.IGNORECASE)
                        if match:
                            currency = match.group(1).replace('$', 'USD').replace('€', 'EUR').replace('£', 'GBP')
                            try:
                                amount = float(match.group(2).replace(',', ''))
                            except Exception:
                                pass
                            break
                if amount:
                    break
            if not vendor:
                logo = soup.find('img', alt=True)
                if logo and 'alt' in logo.attrs:
                    vendor = logo['alt']
            if not vendor:
                for strong in soup.find_all(['strong', 'b']):
                    if 'godaddy' in strong.get_text(strip=True).lower():
                        vendor = 'GoDaddy'
                        break
                        
        if not amount:
            amount_patterns = [
                r'(SGD|USD|EUR|GBP|\$|€|£)\s?([\d,]+\.?\d*)',
                r'([\d,]+\.?\d*)\s*(SGD|USD|EUR|GBP)',
                r'Total[:\s]*([\d,]+\.?\d*)',
                r'Amount[:\s]*([\d,]+\.?\d*)',
                r'Total Due[:\s]*([\d,]+\.?\d*)',
                r'Amount Due[:\s]*([\d,]+\.?\d*)',
                r'Invoice Total[:\s]*([\d,]+\.?\d*)',
                r'([\d,]+\.?\d*)\s*(dollars?|euros?|pounds?)',
            ]
            
            for pattern in amount_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    if match.group(1) in ['SGD', 'USD', 'EUR', 'GBP', '$', '€', '£']:
                        currency = match.group(1).replace('$', 'USD').replace('€', 'EUR').replace('£', 'GBP')
                        try:
                            amount = float(match.group(2).replace(',', ''))
                        except Exception:
                            pass
                    else:
                        try:
                            amount = float(match.group(1).replace(',', ''))
                            if len(match.groups()) > 1 and match.group(2):
                                currency = match.group(2).upper()
                                if currency in ['DOLLARS', 'DOLLAR']:
                                    currency = 'USD'
                                elif currency in ['EUROS', 'EURO']:
                                    currency = 'EUR'
                                elif currency in ['POUNDS', 'POUND']:
                                    currency = 'GBP'
                        except Exception:
                            pass
                    if amount:
                        break
                        
        if not vendor:
            sender = email_content.get('sender', '')
            if '@' in sender:
                domain = sender.split('@')[1]
                # Handle subdomains and extract company name
                parts = domain.split('.')
                if len(parts) >= 2:
                    # For domains like finops@earlybirdapp.co -> Earlybird
                    company_part = parts[0] if parts[0] not in ['www', 'mail', 'smtp', 'finops', 'noreply', 'service'] else parts[1]
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