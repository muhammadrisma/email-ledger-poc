#!/usr/bin/env python3
"""
Test script to verify the package structure and imports work correctly.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all main imports work correctly"""
    print("🧪 Testing package imports...")
    
    try:
        # Test main package import
        from src.app.core.processor import EmailLedgerProcessor
        from src.app.db.models import FinancialTransaction, create_tables, get_db
        print("✅ Main package imports successful")
        
        # Test services imports
        from src.app.services.email_processor import EmailProcessor
        from src.app.services.ai_extractor import AIExtractor
        from src.app.services.ledger_service import LedgerService
        print("✅ Services imports successful")
        
        # Test API imports
        from src.app.api.app import app
        print("✅ API imports successful")
        
        # Test CLI imports
        from src.cli.main import main
        print("✅ CLI imports successful")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_package_structure():
    """Test that the package structure is correct"""
    print("\n📁 Testing package structure...")
    
    expected_files = [
        "src/__init__.py",
        "src/app/__init__.py",
        "src/app/config.py",
        "src/app/core/__init__.py",
        "src/app/core/processor.py",
        "src/app/services/__init__.py",
        "src/app/services/email_processor.py",
        "src/app/services/ai_extractor.py",
        "src/app/services/ledger_service.py",
        "src/app/db/__init__.py",
        "src/app/db/models.py",
        "src/app/api/__init__.py",
        "src/app/api/app.py",
        "src/app/api/routes.py",
        "src/app/schema/__init__.py",
        "src/app/schema/schemas.py",
        "src/cli/__init__.py",
        "src/cli/main.py",
    ]
    
    missing_files = []
    for file_path in expected_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All expected files present")
        return True

def main():
    """Main test function"""
    print("🚀 Email Ledger POC - Package Test")
    print("=" * 50)
    
    # Test package structure
    structure_ok = test_package_structure()
    
    # Test imports
    imports_ok = test_imports()
    
    if structure_ok and imports_ok:
        print("\n🎉 Package setup is correct!")
        print("\n📖 You can now:")
        print("1. Install the package: pip install -e .")
        print("2. Run the CLI: python -m src.cli.main setup")
        print("3. Start the API: python -m src.app.api.app")
    else:
        print("\n❌ Package setup has issues!")
        sys.exit(1)

if __name__ == "__main__":
    main() 