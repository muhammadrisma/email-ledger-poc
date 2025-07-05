from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from ..config import Config

Base = declarative_base()

class FinancialTransaction(Base):
    """
    Financial Transaction database model.
    
    Represents a financial transaction extracted from email data,
    including metadata about the source email and any attachments.
    """
    __tablename__ = "financial_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String, unique=True, index=True)
    email_subject = Column(String)
    email_sender = Column(String)
    email_date = Column(DateTime)
    
    transaction_date = Column(DateTime)
    amount = Column(Float)
    currency = Column(String(3))
    vendor = Column(String)
    transaction_type = Column(String)
    reference_id = Column(String)
    description = Column(Text)
    
    category = Column(String)
    
    processed_at = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Boolean, default=False)
    
    attachment_info = Column(Text)
    
    def __repr__(self):
        return f"<FinancialTransaction(id={self.id}, amount={self.amount} {self.currency}, vendor={self.vendor})>"

engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """
    Create all database tables.
    
    Creates the financial_transactions table and any other tables
    defined in the models.
    """
    Base.metadata.create_all(bind=engine)

def reset_database():
    """
    Reset the database by dropping all tables and recreating them.
    
    This will delete all data in the database and recreate the schema
    from scratch. Use with caution!
    """
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped successfully!")
    
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")
    
    print("Database reset completed!")

def get_db():
    """
    Get database session.
    
    Yields a database session and ensures proper cleanup.
    
    Yields:
        Database session object
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 