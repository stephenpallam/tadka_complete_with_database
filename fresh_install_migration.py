#!/usr/bin/env python3
"""
Tadka News Platform - Fresh Installation Migration Script
This script sets up a fresh database with all exported data
"""

import sqlite3
import json
import os
import sys
from datetime import datetime

def setup_fresh_database():
    """Setup fresh database with all data"""
    
    print("🚀 Setting up fresh Tadka database...")
    
    # Database path
    db_path = 'backend/blog_cms.db'
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        backup_name = f"blog_cms_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        os.rename(db_path, backup_name)
        print(f"📦 Existing database backed up as: {backup_name}")
    
    # Check if data files exist
    if not os.path.exists('database_export.json'):
        print("❌ database_export.json not found!")
        print("   Make sure to place the exported database files in the project root")
        sys.exit(1)
    
    if not os.path.exists('database_export.sql'):
        print("❌ database_export.sql not found!")
        sys.exit(1)
    
    # Create database directory if it doesn't exist
    os.makedirs('backend', exist_ok=True)
    
    # Execute SQL import
    print("📊 Importing database schema and data...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Read and execute SQL file
        with open('database_export.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Execute SQL statements
        cursor.executescript(sql_content)
        conn.commit()
        
        # Verify import
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        total_records = 0
        print("\n📊 Import verification:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_records += count
            print(f"   {table_name}: {count} records")
        
        print(f"\n✅ Database setup completed!")
        print(f"   Total tables: {len(tables)}")
        print(f"   Total records: {total_records}")
        
    except Exception as e:
        print(f"❌ Error during database setup: {str(e)}")
        conn.rollback()
        sys.exit(1)
    
    finally:
        conn.close()
    
    # Create .env file with database URL if it doesn't exist
    env_file = 'backend/.env'
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write('MONGO_URL=sqlite:///./blog_cms.db\n')
        print(f"📝 Created {env_file} with database configuration")
    
    print("\n🎉 Fresh Tadka installation is ready!")
    print("\nNext steps:")
    print("1. Install backend dependencies: pip install -r backend/requirements.txt")
    print("2. Install frontend dependencies: cd frontend && yarn install")
    print("3. Start backend: cd backend && uvicorn server:app --reload --host 0.0.0.0 --port 8001")
    print("4. Start frontend: cd frontend && yarn start")

if __name__ == "__main__":
    setup_fresh_database()
