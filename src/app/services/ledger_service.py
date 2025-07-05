import json
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ..db.models import FinancialTransaction, get_db
from ..config import Config
import re

class LedgerService:
    def __init__(self):
        """
        Initialize the Ledger Service.
        
        Provides database operations for financial transactions including
        saving, retrieving, updating, and deleting transaction records.
        """
    
    def save_transaction(self, db: Session, email_content: Dict, financial_data: Dict, classification: Dict) -> FinancialTransaction:
        """
        Save a financial transaction to the database.
        
        Creates a new FinancialTransaction record from extracted email data,
        including attachment information and proper date parsing.
        
        Args:
            db: Database session
            email_content: Original email data including attachments
            financial_data: Extracted financial information
            classification: Expense classification data
            
        Returns:
            FinancialTransaction: The saved transaction record
        """
        
        attachment_info = None
        if email_content.get('attachments'):
            attachment_summary = []
            for attachment in email_content['attachments']:
                summary = {
                    'filename': attachment['filename'],
                    'content_type': attachment['content_type'],
                    'size': attachment['size'],
                    'has_text_content': bool(attachment.get('text_content')),
                    'has_csv_data': bool(attachment.get('csv_data')),
                    'is_financial': attachment.get('is_financial', False)
                }
                attachment_summary.append(summary)
            attachment_info = json.dumps(attachment_summary)
        
        transaction_date = None
        if financial_data.get('date'):
            try:
                date_str = str(financial_data['date'])
                if 'T' in date_str:
                    transaction_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                elif re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                    transaction_date = datetime.strptime(date_str, '%Y-%m-%d')
                else:
                    email_date = email_content.get('date', '')
                    if email_date:
                        transaction_date = datetime.fromisoformat(email_date.replace('Z', '+00:00'))
            except:
                email_date = email_content.get('date', '')
                if email_date:
                    try:
                        transaction_date = datetime.fromisoformat(email_date.replace('Z', '+00:00'))
                    except:
                        transaction_date = datetime.utcnow()
                else:
                    transaction_date = datetime.utcnow()
        else:
            email_date = email_content.get('date', '')
            if email_date:
                try:
                    transaction_date = datetime.fromisoformat(email_date.replace('Z', '+00:00'))
                except:
                    transaction_date = datetime.utcnow()
            else:
                transaction_date = datetime.utcnow()
        
        transaction = FinancialTransaction(
            email_id=email_content['message_id'],
            email_subject=email_content['subject'],
            email_sender=email_content['sender'],
            email_date=email_content['date'],
            transaction_date=transaction_date,
            amount=financial_data.get('amount'),
            currency=financial_data.get('currency', 'USD'),
            vendor=financial_data.get('vendor', ''),
            transaction_type=financial_data.get('transaction_type', 'debit'),
            reference_id=financial_data.get('reference_id', ''),
            description=financial_data.get('description', ''),
            category=classification.get('category', 'other'),
            processed_at=datetime.utcnow(),
            is_processed=True,
            attachment_info=attachment_info
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return transaction
    
    def get_transactions(self, db: Session, limit: int = 100, offset: int = 0) -> List[FinancialTransaction]:
        """
        Get transactions from the database.
        
        Retrieves financial transactions with pagination support,
        ordered by processing date (most recent first).
        
        Args:
            db: Database session
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip
            
        Returns:
            List of FinancialTransaction objects
        """
        return db.query(FinancialTransaction).order_by(
            FinancialTransaction.processed_at.desc()
        ).offset(offset).limit(limit).all()
    
    def get_transactions_by_category(self, db: Session, category: str) -> List[FinancialTransaction]:
        """
        Get transactions by category.
        
        Args:
            db: Database session
            category: Expense category to filter by
            
        Returns:
            List of FinancialTransaction objects in the specified category
        """
        return db.query(FinancialTransaction).filter(
            FinancialTransaction.category == category
        ).order_by(FinancialTransaction.processed_at.desc()).all()
    
    def get_transactions_by_date_range(self, db: Session, start_date: datetime, end_date: datetime) -> List[FinancialTransaction]:
        """
        Get transactions within a date range.
        
        Args:
            db: Database session
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            List of FinancialTransaction objects within the date range
        """
        return db.query(FinancialTransaction).filter(
            FinancialTransaction.transaction_date >= start_date,
            FinancialTransaction.transaction_date <= end_date
        ).order_by(FinancialTransaction.transaction_date.desc()).all()
    
    def get_summary_stats(self, db: Session) -> Dict:
        """
        Get summary statistics.
        
        Calculates total transactions, total amount, and category breakdown.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary containing:
            - total_transactions: Total number of transactions
            - total_amount: Sum of all transaction amounts
            - category_breakdown: Count of transactions by category
        """
        total_transactions = db.query(FinancialTransaction).count()
        total_amount = db.query(FinancialTransaction.amount).filter(
            FinancialTransaction.amount.isnot(None)
        ).all()
        total_amount = sum([t[0] for t in total_amount]) if total_amount else 0
        
        categories = db.query(FinancialTransaction.category).all()
        category_counts = {}
        for cat in categories:
            category_counts[cat[0]] = category_counts.get(cat[0], 0) + 1
        
        return {
            "total_transactions": total_transactions,
            "total_amount": total_amount,
            "category_breakdown": category_counts
        }
    
    def delete_transaction(self, db: Session, transaction_id: int) -> bool:
        """
        Delete a transaction.
        
        Args:
            db: Database session
            transaction_id: ID of the transaction to delete
            
        Returns:
            True if transaction was deleted, False if not found
        """
        transaction = db.query(FinancialTransaction).filter(
            FinancialTransaction.id == transaction_id
        ).first()
        
        if transaction:
            db.delete(transaction)
            db.commit()
            return True
        return False
    
    def update_transaction(self, db: Session, transaction_id: int, updates: Dict) -> Optional[FinancialTransaction]:
        """
        Update a transaction.
        
        Args:
            db: Database session
            transaction_id: ID of the transaction to update
            updates: Dictionary of field names and new values
            
        Returns:
            Updated FinancialTransaction object or None if not found
        """
        transaction = db.query(FinancialTransaction).filter(
            FinancialTransaction.id == transaction_id
        ).first()
        
        if transaction:
            for key, value in updates.items():
                if hasattr(transaction, key):
                    setattr(transaction, key, value)
            
            db.commit()
            db.refresh(transaction)
            return transaction
        return None 