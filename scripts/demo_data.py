#!/usr/bin/env python3
"""
Demo Data Generator

This script generates sample financial transactions for testing the ledger system.
"""

import random
import sys
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.app.db.models import get_db, FinancialTransaction, create_tables
from src.app.config import Config

# Sample financial data
SAMPLE_VENDORS = [
    "Stripe", "PayPal", "Wise", "Bank of America", "Chase", "Wells Fargo",
    "Netflix", "Spotify", "Adobe", "Microsoft", "Google", "AWS", "DigitalOcean",
    "Uber", "Lyft", "Airbnb", "Booking.com", "Amazon", "Target", "Walmart",
    "Starbucks", "McDonald's", "Subway", "Pizza Hut", "Domino's"
]

SAMPLE_CATEGORIES = Config.EXPENSE_CATEGORIES

SAMPLE_DESCRIPTIONS = [
    "Monthly subscription payment",
    "Payment for services",
    "Transaction fee",
    "Monthly membership",
    "Service charge",
    "Processing fee",
    "Subscription renewal",
    "Payment confirmation",
    "Transaction completed",
    "Payment received"
]

def generate_demo_transactions(count: int = 50):
    """Generate demo financial transactions"""
    
    # Create database tables
    create_tables()
    
    # Get database session
    db = next(get_db())
    
    transactions_created = 0
    
    try:
        for i in range(count):
            days_ago = random.randint(1, 180)
            transaction_date = datetime.now() - timedelta(days=days_ago)
            
            amount = round(random.uniform(1.0, 1000.0), 2)
            
            vendor = random.choice(SAMPLE_VENDORS)
            category = random.choice(SAMPLE_CATEGORIES)
            
            email_id = f"demo_email_{i}_{random.randint(1000, 9999)}"
            email_subject = f"Payment Receipt - {vendor} - ${amount}"
            email_sender = f"noreply@{vendor.lower().replace(' ', '')}.com"
            
            transaction = FinancialTransaction(
                email_id=email_id,
                email_subject=email_subject,
                email_sender=email_sender,
                email_date=transaction_date,
                
                amount=amount,
                currency="USD",
                vendor=vendor,
                transaction_type="debit",
                reference_id=f"ref_{random.randint(100000, 999999)}",
                description=random.choice(SAMPLE_DESCRIPTIONS),
                
                category=category,
                confidence_score=round(random.uniform(0.7, 1.0), 2),
                
                processed_at=datetime.utcnow(),
                is_processed=True
            )
            
            db.add(transaction)
            transactions_created += 1
            
            if transactions_created % 10 == 0:
                db.commit()
                print(f"Created {transactions_created} demo transactions...")
        
        db.commit()
        print(f"Successfully created {transactions_created} demo transactions!")
        
        print("\n📊 Demo Data Summary:")
        print(f"Total transactions: {transactions_created}")

        categories = db.query(FinancialTransaction.category).all()
        category_counts = {}
        for cat in categories:
            category_counts[cat[0]] = category_counts.get(cat[0], 0) + 1
        
        print("\nCategory breakdown:")
        for category, count in category_counts.items():
            print(f"  {category}: {count}")
        
        total_amount = db.query(FinancialTransaction.amount).filter(
            FinancialTransaction.amount.isnot(None)
        ).all()
        total = sum([t[0] for t in total_amount]) if total_amount else 0
        print(f"\nTotal amount: ${total:,.2f}")
        
    except Exception as e:
        print(f"Error creating demo data: {e}")
        db.rollback()
    finally:
        db.close()

def clear_demo_data():
    """Clear all demo transactions"""
    db = next(get_db())
    
    try:
        deleted = db.query(FinancialTransaction).filter(
            FinancialTransaction.email_id.like("demo_email_%")
        ).delete()
        
        db.commit()
        print(f"Deleted {deleted} demo transactions")
        
    except Exception as e:
        print(f"Error clearing demo data: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate demo data for the ledger system")
    parser.add_argument("--count", type=int, default=50, help="Number of transactions to generate")
    parser.add_argument("--clear", action="store_true", help="Clear existing demo data")
    
    args = parser.parse_args()
    
    if args.clear:
        print("Clearing demo data...")
        clear_demo_data()
    else:
        print(f"Generating {args.count} demo transactions...")
        generate_demo_transactions(args.count)

if __name__ == "__main__":
    main() 