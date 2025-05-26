#!/usr/bin/env python3
"""
Test script to verify monitoring dashboard files.
"""
import os
import sys

def check_file(file_path, description):
    """Check if a file exists and is readable."""
    try:
        if not os.path.exists(file_path):
            print(f"❌ {description} not found: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(100)  # Read first 100 bytes to check readability
            if not content:
                print(f"⚠️  {description} is empty: {file_path}")
                return False
            
        print(f"✅ {description} found and readable: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error checking {file_path}: {e}")
        return False

def main():
    """Main function to test monitoring files."""
    print("🔍 Checking monitoring dashboard files...")
    
    # Define files to check
    files_to_check = [
        ("monitoring/index.html", "Dashboard HTML file"),
        ("monitoring/style.css", "Dashboard stylesheet"),
        ("monitoring/dashboard.js", "Dashboard JavaScript")
    ]
    
    all_ok = True
    for file_path, description in files_to_check:
        if not check_file(file_path, description):
            all_ok = False
    
    if all_ok:
        print("\n🎉 All monitoring files are present and accessible!")
        print("To start the monitoring dashboard, run:")
        print("  cd monitoring && python3 -m http.server 8000")
        print("Then open http://localhost:8000 in your browser")
        return 0
    else:
        print("\n❌ Some monitoring files are missing or inaccessible")
        return 1

if __name__ == "__main__":
    sys.exit(main())
