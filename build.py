#!/usr/bin/env python3
"""
Simple build script for Email Ledger POC.
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

def clean_build():
    """Clean build artifacts"""
    print("🧹 Cleaning build artifacts...")
    
    # Remove build directories
    build_dirs = ["build", "dist", "*.egg-info"]
    for pattern in build_dirs:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                import shutil
                shutil.rmtree(path)
                print(f"  Removed: {path}")
    
    # Remove Python cache
    for pycache in Path(".").rglob("__pycache__"):
        if pycache.is_dir():
            import shutil
            shutil.rmtree(pycache)
            print(f"  Removed: {pycache}")

def build_package():
    """Build the package"""
    print("📦 Building package...")
    
    # Clean first
    clean_build()
    
    # Build using setuptools
    if not run_command("python setup.py sdist bdist_wheel", "Building package"):
        return False
    
    print("✅ Package built successfully!")
    return True

def install_package():
    """Install the package in development mode"""
    print("📥 Installing package in development mode...")
    
    if not run_command("pip install -e .", "Installing package"):
        return False
    
    print("✅ Package installed successfully!")
    return True

def test_package():
    """Test the package"""
    print("🧪 Testing package...")
    
    # Run the test script
    test_script = Path("scripts/test_package.py")
    if test_script.exists():
        if not run_command(f"python {test_script}", "Running package tests"):
            return False
    else:
        print("⚠️  Test script not found: scripts/test_package.py")
        return False
    
    print("✅ Package tests passed!")
    return True

def main():
    """Main build function"""
    print("🚀 Email Ledger POC - Build Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("setup.py").exists():
        print("❌ setup.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Build steps
    steps = [
        ("Clean", clean_build),
        ("Build", build_package),
        ("Install", install_package),
        ("Test", test_package),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 Step: {step_name}")
        if not step_func():
            print(f"❌ {step_name} failed!")
            sys.exit(1)
    
    print("\n🎉 Build completed successfully!")
    print("\n📖 Next steps:")
    print("1. Set up your environment variables")
    print("2. Configure Gmail API credentials")
    print("3. Run: python -m src.cli.main setup")
    print("4. Run: python -m src.cli.main process")

if __name__ == "__main__":
    main() 