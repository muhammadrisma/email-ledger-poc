#!/usr/bin/env python3
"""
Simple install script for Email Ledger POC.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 11):
        print(f"❌ Python 3.11+ required, found {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Install from requirements.txt
    if not run_command("pip install -r requirements.txt", "Installing requirements"):
        return False
    
    return True

def install_package():
    """Install the package in development mode"""
    print("📥 Installing package...")
    
    if not run_command("pip install -e .", "Installing package"):
        return False
    
    return True

def test_installation():
    """Test that the installation works"""
    print("🧪 Testing installation...")
    
    # Test imports
    try:
        import src.app.core.processor
        import src.app.services.email_processor
        import src.app.services.ai_extractor
        print("✅ Package imports successful")
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    # Run the test script
    test_script = Path("scripts/test_package.py")
    if test_script.exists():
        if not run_command(f"python {test_script}", "Running package tests"):
            return False
    else:
        print("⚠️  Test script not found, skipping tests")
    
    return True

def create_env_example():
    """Create environment example file"""
    print("📝 Creating environment example...")
    
    env_example = """# Email Ledger POC Environment Variables

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/email_ledger

# Gmail API Configuration
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.readonly

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Email Processing Configuration
EMAIL_POLL_INTERVAL=300
EXPENSE_CATEGORIES=meals_and_entertainment,transport,saas_subscriptions,travel,office_supplies,utilities,insurance,professional_services,marketing,other

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
"""
    
    env_file = Path(".env.example")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_example)
        print("✅ Created .env.example file")
    else:
        print("✅ .env.example already exists")
    
    return True

def main():
    """Main install function"""
    print("🚀 Email Ledger POC - Install Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("setup.py").exists():
        print("❌ setup.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Installation steps
    steps = [
        ("Python Version Check", check_python_version),
        ("Install Dependencies", install_dependencies),
        ("Install Package", install_package),
        ("Test Installation", test_installation),
        ("Create Environment Example", create_env_example),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 Step: {step_name}")
        if not step_func():
            print(f"❌ {step_name} failed!")
            sys.exit(1)
    
    print("\n🎉 Installation completed successfully!")
    print("\n📖 Next steps:")
    print("1. Copy .env.example to .env and configure your settings")
    print("2. Set up Gmail API credentials (see README.md)")
    print("3. Set up your database")
    print("4. Run: python -m src.cli.main setup")
    print("5. Run: python -m src.cli.main process")

if __name__ == "__main__":
    main() 