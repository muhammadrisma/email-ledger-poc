#!/usr/bin/env python3
"""
Main CLI entry point for the Email Ledger POC.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.app.core.processor import EmailLedgerProcessor
from src.app.db.models import create_tables, reset_database

def main():
    """
    Main CLI function.
    
    Parses command line arguments and executes the appropriate
    command for email processing or database setup.
    """
    parser = argparse.ArgumentParser(
        description="Email Ledger POC - AI-powered email scraping to live ledger",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.cli.main process     # Process emails once
  python -m src.cli.main continuous  # Run continuous processing
  python -m src.cli.main setup       # Setup database tables
  python -m src.cli.main reset       # Reset database (drops all data)
  python -m src.app.api.app          # Start API server
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    process_parser = subparsers.add_parser("process", help="Process emails once")
    process_parser.add_argument(
        "--continuous", 
        action="store_true", 
        help="Run continuous processing"
    )
    
    setup_parser = subparsers.add_parser("setup", help="Setup database tables")
    
    reset_parser = subparsers.add_parser("reset", help="Reset database (drops all data)")
    reset_parser.add_argument(
        "--confirm", 
        action="store_true", 
        help="Skip confirmation prompt"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "setup":
            print("Setting up database tables...")
            create_tables()
            print("Database tables created successfully!")
            
        elif args.command == "reset":
            if not args.confirm:
                response = input("This will delete ALL data in the database. Are you sure? (y/N): ")
                if response.lower() != 'y':
                    print("Database reset cancelled.")
                    return
            
            print("Resetting database...")
            reset_database()
            
        elif args.command == "process":
            print("Initializing Email Ledger Processor...")
            processor = EmailLedgerProcessor()
            
            if args.continuous:
                print("Starting continuous email processing...")
                processor.run_continuous_processing()
            else:
                print("Processing emails once...")
                result = processor.process_emails()
                print(f"Processing complete: {result}")
                
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 