#!/usr/bin/env python3
"""
Database reset script.
Drops all tables and recreates them from scratch.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.db.models import Base
from app.config import Config
from sqlalchemy import create_engine

def reset_database():
    """Reset the database by dropping all tables and recreating them"""
    engine = create_engine(Config.DATABASE_URL)
    
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped successfully!")
    
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")
    
    print("Database reset completed!")

if __name__ == "__main__":
    print("Resetting database...")
    reset_database() 