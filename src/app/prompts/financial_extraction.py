"""
Financial data extraction prompt template.
"""

FINANCIAL_EXTRACTION_PROMPT = """
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

SPECIAL INSTRUCTIONS FOR FORWARDED EMAILS:
- When email subject contains "Fwd:" or "Fw:", look for forwarded content in the body
- Extract financial data from the forwarded email content
- Look for patterns like "We charged $X.XX" or "charged $X.XX"
- Extract vendor from the original sender (e.g., noreply@tm.openai.com -> OpenAI)
- Look for credit card information and transaction details in forwarded content
- Use the original email date if available in forwarded content
- IMPORTANT: For forwarded emails, the financial data is usually in the forwarded content, not the email body
- Look for amounts in the forwarded email body, especially after "From:", "Sent:", "Subject:" lines
- Common patterns: "charged $X.XX", "billed $X.XX", "payment of $X.XX", "amount: $X.XX"

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
- For charges, look for "charged $X.XX", "We charged $X.XX", "charged X.XX USD"
- For payments, look for "paid $X.XX", "payment of $X.XX", "amount: $X.XX"
- For refunds, look for "refunded $X.XX", "refund of $X.XX"
- For subscriptions, look for "billed $X.XX", "monthly charge $X.XX"
- Extract the largest amount if multiple amounts found (usually the total)
- Look for amounts in line items and sum them if no total is found
- IMPORTANT: If you find ANY amount in the email or attachments, extract it as a number (e.g., $10.50 -> 10.50)
- Look for amounts in forwarded email content, especially after "From:", "Sent:", "Subject:" lines

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
- If multiple amounts found, use the largest/total amount (usually the final total)
- For invoice emails, use "invoice" as transaction type if unclear
- Look for line items and sum them if no total is explicitly stated
- Extract amounts from tables, especially the last row which usually contains the total
- For charges, look for the charged amount
- For payments, look for the payment amount
- For refunds, look for the refunded amount
- CRITICAL: If you find ANY amount mentioned in the email or attachments, extract it as a number

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