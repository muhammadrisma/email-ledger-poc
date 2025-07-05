"""
Email Ledger POC - AI-powered email scraping to live ledger system.

This package provides functionality to:
- Extract financial data from emails using AI
- Process and classify expenses
- Store transactions in a database
- Provide API endpoints for data access
"""

__version__ = "1.0.0"
__author__ = "Email Ledger POC Team"
__email__ = "team@example.com"

# Import main components for easy access
from .app.core.processor import EmailLedgerProcessor
from .app.db.models import FinancialTransaction, create_tables, get_db

__all__ = [
    "EmailLedgerProcessor",
    "FinancialTransaction", 
    "create_tables",
    "get_db",
] 