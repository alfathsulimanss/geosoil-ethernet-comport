#!/usr/bin/env python3
"""
Debug script to verify data in database and test data retrieval
Run this to diagnose data reading issues
"""

import sys
from database_handler import DatabaseHandler
from config import DATABASE_CONFIG, TEST_TYPE_COLUMNS

def main():
    print("=" * 70)
    print("DATABASE DEBUG TOOL - LabVIEW Test Data Display")
    print("=" * 70)
    print()
    
    # Show configuration
    print("📋 Database Configuration:")
    print(f"  Host: {DATABASE_CONFIG['host']}")
    print(f"  Database: {DATABASE_CONFIG['database']}")
    print(f"  User: {DATABASE_CONFIG['user']}")
    print()
    
    # Connect
    db = DatabaseHandler()
    print("🔗 Connecting to database...")
    if not db.connect():
        print("❌ Connection failed!")
        return 1
    print("✓ Connected successfully")
    print()
    
    # Show available columns
    print("📊 Available columns in historydata table:")
    columns = db.get_actual_columns()
    if columns:
        for i, col in enumerate(columns, 1):
            print(f"  {i}. {col}")
    else:
        print("  ❌ No columns found!")
    print()
    
    # Show test types
    print("📋 Configured test types:")
    for test_id, info in sorted(TEST_TYPE_COLUMNS.items()):
        col_count = len(info['columns'])
        print(f"  Type {test_id}: {info['name']} ({col_count} columns)")
    print()
    
    # Test with specific file ID if provided
    if len(sys.argv) > 1:
        fileid = sys.argv[1]
        print(f"🔍 Querying data for File ID: {fileid}")
        print()
        
        # Get testtype
        testtype = db.get_testtype(fileid)
        print(f"  Test Type: {testtype}")
        
        if testtype and testtype in TEST_TYPE_COLUMNS:
            test_info = TEST_TYPE_COLUMNS[testtype]
            print(f"  Test Name: {test_info['name']}")
            print(f"  Expected Columns: {len(test_info['columns'])}")
        print()
        
        # Get available stages
        print(f"📋 Available stages for File ID {fileid}:")
        stages = db.get_available_stages(fileid)
        if stages:
            for i, stage in enumerate(stages, 1):
                count = db.get_available_data_count(fileid, stage)
                print(f"  {i}. '{stage}' ({count} records)")
        else:
            print("  ❌ No stages found!")
        print()
        
        # Test retrieval with first stage if available
        if stages:
            stage_name = stages[0]
            print(f"🔄 Testing data retrieval for: '{stage_name}'")
            print()
            
            data, columns_info = db.get_stage_data(fileid, stage_name)
            
            if data:
                print(f"✓ Retrieved {len(data)} records")
                print()
                print("📊 Sample data (first 3 records):")
                for i, row in enumerate(data[:3], 1):
                    print(f"\n  Record {i}:")
                    for key, value in row.items():
                        # Truncate long values
                        val_str = str(value)
                        if len(val_str) > 50:
                            val_str = val_str[:50] + "..."
                        print(f"    {key}: {val_str}")
            else:
                print("❌ No data retrieved!")
        print()
    else:
        print("💡 To test data retrieval, run:")
        print("  python debug_data.py <fileid>")
        print()
        print("  Example:")
        print("  python debug_data.py 1")
        print()
    
    # Close connection
    db.disconnect()
    print("✓ Disconnected from database")
    print()
    print("=" * 70)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
