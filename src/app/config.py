import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/ledger_db")
    
    # Gmail API
    GMAIL_CREDENTIALS_FILE = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
    GMAIL_TOKEN_FILE = os.getenv("GMAIL_TOKEN_FILE", "token.json")
    GMAIL_SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    # OpenAI API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Email Processing
    EMAIL_BATCH_SIZE = int(os.getenv("EMAIL_BATCH_SIZE", "50"))
    EMAIL_POLL_INTERVAL = int(os.getenv("EMAIL_POLL_INTERVAL", "300"))  # 5 minutes
    
    # Financial Classification
    EXPENSE_CATEGORIES = [
        "meals_and_entertainment",
        "transport",
        "saas_subscriptions",
        "travel",
        "office_supplies",
        "utilities",
        "insurance",
        "professional_services",
        "marketing",
        "other"
    ]
    
    # Email Filters
    FINANCIAL_EMAIL_SENDERS = [
        "noreply@stripe.com",
        "service@paypal.com",
        "noreply@wise.com",
        "notifications@bank.com",
        "receipts@",
        "invoice@",
        "payment@"
    ] 