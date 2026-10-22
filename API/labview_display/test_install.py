#!/usr/bin/env python3
"""
Test script to verify the installation and database connection
Run this before using the main application
"""

import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    required_packages = {
        'mysql.connector': 'mysql-connector-python',
        'pandas': 'pandas',
        'matplotlib': 'matplotlib',
        'numpy': 'numpy'
    }
    
    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - NOT INSTALLED")
            missing.append(package)
    
    return len(missing) == 0, missing

def test_database():
    """Test database connection"""
    print("\nTesting database connection...")
    try:
        from database_handler import DatabaseHandler
        db = DatabaseHandler()
        
        if db.connect():
            print("  ✓ Connected to database successfully")
            
            # Test a simple query
            db.cursor.execute("SELECT COUNT(*) as count FROM historydata")
            result = db.cursor.fetchone()
            count = result['count'] if result else 0
            print(f"  ✓ Found {count} records in historydata table")
            
            # Check test types
            db.cursor.execute("SELECT DISTINCT testtype FROM historydata ORDER BY testtype")
            test_types = db.cursor.fetchall()
            if test_types:
                types = [str(t['testtype']) for t in test_types]
                print(f"  ✓ Available test types: {', '.join(types)}")
            else:
                print("  ! No test types found in database")
            
            db.disconnect()
            return True
        else:
            print("  ✗ Failed to connect to database")
            print("    Check if MySQL is running on localhost")
            print("    Check config.py for correct credentials")
            return False
    
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

def test_config():
    """Test configuration file"""
    print("\nTesting configuration...")
    try:
        from config import DATABASE_CONFIG, TEST_TYPE_COLUMNS
        
        print(f"  ✓ Database: {DATABASE_CONFIG['database']}")
        print(f"  ✓ Host: {DATABASE_CONFIG['host']}")
        print(f"  ✓ User: {DATABASE_CONFIG['user']}")
        print(f"  ✓ Test types configured: {len(TEST_TYPE_COLUMNS)}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("LabVIEW Test Data Display - Installation Test")
    print("=" * 60)
    
    # Test imports
    imports_ok, missing = test_imports()
    if not imports_ok:
        print("\n⚠ Missing packages detected!")
        print("Install missing packages with:")
        print(f"  pip install {' '.join(missing)}")
        print("\nOr use:")
        print("  pip install -r requirements.txt")
        return 1
    
    # Test configuration
    config_ok = test_config()
    
    # Test database
    db_ok = test_database()
    
    print("\n" + "=" * 60)
    if imports_ok and config_ok and db_ok:
        print("✓ All tests passed! Ready to use.")
        print("\nUsage from LabVIEW (System Exec):")
        print("  display.bat 1 \"Stage 1\"")
        print("\nUsage from command line:")
        print("  python main.py 1 \"Stage 1\"")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
