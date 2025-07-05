#!/usr/bin/env python3
"""
Database migration script to add missing columns.
"""

from sqlalchemy import create_engine, text
from ..config import Config

def migrate_database():
    """Add missing columns to the database"""
    engine = create_engine(Config.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if transaction_date column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'financial_transactions' 
            AND column_name = 'transaction_date'
        """))
        
        if not result.fetchone():
            print("Adding transaction_date column...")
            conn.execute(text("""
                ALTER TABLE financial_transactions 
                ADD COLUMN transaction_date TIMESTAMP WITHOUT TIME ZONE
            """))
            conn.commit()
            print("transaction_date column added successfully!")
        else:
            print("transaction_date column already exists.")
        
        # Check if confidence_score column exists (it's in the table but not in the model)
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'financial_transactions' 
            AND column_name = 'confidence_score'
        """))
        
        if result.fetchone():
            print("confidence_score column exists in database but not in model.")
            print("Consider adding it to the model or removing it from the database.")

if __name__ == "__main__":
    migrate_database() 