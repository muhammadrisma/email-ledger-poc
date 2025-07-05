"""
Email Ledger App Package.

Contains the core application logic for email processing and financial data extraction.
"""

from .core.processor import EmailLedgerProcessor
from .db.models import FinancialTransaction, create_tables, get_db
from .config import Config

__all__ = [
    "EmailLedgerProcessor",
    "FinancialTransaction",
    "create_tables", 
    "get_db",
    "Config",
] 