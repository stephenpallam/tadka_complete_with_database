#!/usr/bin/env python3
"""
Complete database export script for Tadka News Platform
Exports all data and creates migration scripts for fresh installation
"""

import sqlite3
import json
import os
from datetime import datetime

def export_database_data():
    """Export all database data to SQL and JSON formats"""
    
    db_path = '/app/backend/blog_cms.db'
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in cursor.fetchall()]
    
    print(f"📊 Found {len(tables)} tables to export")
    
    # Export data
    exported_data = {}
    sql_exports = []
    
    # Add header to SQL export
    sql_exports.append("-- Tadka News Platform Database Export")
    sql_exports.append(f"-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql_exports.append("-- This file contains all data to recreate the complete database")
    sql_exports.append("")
    
    total_records = 0
    
    for table in tables:
        print(f"📄 Exporting table: {table}")
        
        # Get table schema
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        schema = cursor.fetchone()
        if schema:
            sql_exports.append(f"-- Table: {table}")
            sql_exports.append(schema[0] + ";")
            sql_exports.append("")
        
        # Get all data from table
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        
        if rows:
            # Convert to list of dictionaries for JSON export
            table_data = []
            for row in rows:
                table_data.append(dict(row))
            
            exported_data[table] = table_data
            total_records += len(rows)
            
            # Generate INSERT statements for SQL export
            if len(rows) > 0:
                # Get column names
                columns = [description[0] for description in cursor.description]
                
                sql_exports.append(f"-- Data for table: {table} ({len(rows)} records)")
                
                for row in rows:
                    values = []
                    for value in row:
                        if value is None:
                            values.append("NULL")
                        elif isinstance(value, str):
                            # Escape single quotes
                            escaped_value = value.replace("'", "''")
                            values.append(f"'{escaped_value}'")
                        else:
                            values.append(str(value))
                    
                    columns_str = ", ".join(columns)
                    values_str = ", ".join(values)
                    sql_exports.append(f"INSERT INTO {table} ({columns_str}) VALUES ({values_str});")
                
                sql_exports.append("")
            
            print(f"   ✅ {len(rows)} records exported")
        else:
            exported_data[table] = []
            print(f"   📭 No records found")
    
    conn.close()
    
    # Write JSON export
    json_file = '/app/database_export.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(exported_data, f, indent=2, ensure_ascii=False, default=str)
    
    # Write SQL export
    sql_file = '/app/database_export.sql'
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_exports))
    
    # Create summary report
    summary = {
        'export_timestamp': datetime.now().isoformat(),
        'total_tables': len(tables),
        'total_records': total_records,
        'tables': {}
    }
    
    for table in tables:
        summary['tables'][table] = len(exported_data.get(table, []))
    
    summary_file = '/app/database_export_summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"""
    ✅ Database export completed!
    
    📊 Export Summary:
    - Total Tables: {len(tables)}
    - Total Records: {total_records}
    - JSON Export: {json_file}
    - SQL Export: {sql_file}
    - Summary: {summary_file}
    
    📋 Key Content Exported:
    - Articles: {len(exported_data.get('articles', []))} records
    - Categories: {len(exported_data.get('categories', []))} records  
    - Movie Reviews: {len(exported_data.get('movie_reviews', []))} records
    - Theater Releases: {len(exported_data.get('theater_releases', []))} records
    - OTT Releases: {len(exported_data.get('ott_releases', []))} records
    - Topics: {len(exported_data.get('topics', []))} records
    - Galleries: {len(exported_data.get('galleries', []))} records
    """)
    
    # Print detailed breakdown
    print("\n📊 Detailed Table Breakdown:")
    for table, count in summary['tables'].items():
        print(f"   {table}: {count} records")
    
    return {
        'json_file': json_file,
        'sql_file': sql_file,
        'summary_file': summary_file,
        'total_records': total_records
    }

def create_migration_script():
    """Create a migration script for fresh installations"""
    
    migration_script = '''#!/usr/bin/env python3
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
        print("\\n📊 Import verification:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_records += count
            print(f"   {table_name}: {count} records")
        
        print(f"\\n✅ Database setup completed!")
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
            f.write('MONGO_URL=sqlite:///./blog_cms.db\\n')
        print(f"📝 Created {env_file} with database configuration")
    
    print("\\n🎉 Fresh Tadka installation is ready!")
    print("\\nNext steps:")
    print("1. Install backend dependencies: pip install -r backend/requirements.txt")
    print("2. Install frontend dependencies: cd frontend && yarn install")
    print("3. Start backend: cd backend && uvicorn server:app --reload --host 0.0.0.0 --port 8001")
    print("4. Start frontend: cd frontend && yarn start")

if __name__ == "__main__":
    setup_fresh_database()
'''
    
    migration_file = '/app/fresh_install_migration.py'
    with open(migration_file, 'w', encoding='utf-8') as f:
        f.write(migration_script)
    
    print(f"✅ Migration script created: {migration_file}")
    return migration_file

def create_installation_readme():
    """Create comprehensive installation instructions"""
    
    readme_content = '''# 🔥 Tadka News Platform - Fresh Installation Guide

## 📋 Prerequisites
- Python 3.8+
- Node.js 16+
- Yarn package manager

## 🚀 Quick Start

### 1. Extract and Setup
```bash
# Extract the project
tar -xzf tadka_complete_project.tar.gz
cd app

# Run the migration script to setup database
python fresh_install_migration.py
```

### 2. Install Dependencies
```bash
# Backend dependencies
pip install -r backend/requirements.txt

# Frontend dependencies  
cd frontend
yarn install
cd ..
```

### 3. Start the Application
```bash
# Terminal 1: Start Backend
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8001

# Terminal 2: Start Frontend  
cd frontend
yarn start
```

### 4. Access the Application
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001
- **CMS Dashboard:** http://localhost:3000/cms/dashboard

## 📊 What's Included

### Database Content
- **117 Articles** (Viral shorts, trending videos, politics, movie news, NRI news)
- **58 Categories** (All content categories)
- **3 Movie Reviews** 
- **2 Theater Releases**
- **2 OTT Releases**
- **5 Topics** with categories
- **4 Galleries** with images
- **Complete configuration** and settings

### File Structure
```
app/
├── backend/                 # FastAPI Backend
│   ├── server.py           # Main server
│   ├── database.py         # Database configuration
│   ├── models/             # Database models
│   ├── routes/             # API routes  
│   ├── uploads/            # Uploaded images
│   └── blog_cms.db         # SQLite database
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Application pages
│   │   ├── contexts/       # React contexts
│   │   └── services/       # API services
│   └── public/             # Static files
├── database_export.json    # Database backup (JSON)
├── database_export.sql     # Database backup (SQL)
└── fresh_install_migration.py # Setup script
```

## 🔧 Configuration

The application comes pre-configured with:
- SQLite database with all content
- Environment variables
- Required dependencies
- Upload directories

## 📝 Important Notes

1. **Database:** All your original content is preserved
2. **Uploads:** All images are included in backend/uploads/
3. **Environment:** .env files are created automatically
4. **Development:** Both frontend and backend have hot-reload enabled

## 🆘 Troubleshooting

### Database Issues
```bash
# If database setup fails, run migration again
python fresh_install_migration.py
```

### Dependency Issues  
```bash
# Backend dependencies
pip install -r backend/requirements.txt --force-reinstall

# Frontend dependencies
cd frontend
rm -rf node_modules yarn.lock
yarn install
```

### Port Conflicts
- Backend default: 8001 (change in uvicorn command)
- Frontend default: 3000 (change in package.json)

## 🎯 Success Verification

After setup, verify everything works:
1. ✅ Backend responds at http://localhost:8001/docs
2. ✅ Frontend loads at http://localhost:3000  
3. ✅ Articles display on homepage
4. ✅ CMS dashboard accessible
5. ✅ Images load correctly

## 📞 Support

If you encounter issues:
1. Check the console logs for errors
2. Verify all dependencies are installed
3. Ensure ports 3000 and 8001 are available
4. Run migration script again if database issues persist

---

**🔥 Your complete Tadka News Platform is ready to go!**
'''
    
    readme_file = '/app/FRESH_INSTALL_README.md'
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Installation guide created: {readme_file}")
    return readme_file

if __name__ == "__main__":
    # Export database
    export_result = export_database_data()
    
    # Create migration script
    migration_file = create_migration_script()
    
    # Create installation guide
    readme_file = create_installation_readme()
    
    print(f"""
    
🎉 COMPLETE DATABASE EXPORT READY!

📦 Files Created:
- {export_result['json_file']} (JSON backup)
- {export_result['sql_file']} (SQL backup)  
- {migration_file} (Fresh install script)
- {readme_file} (Installation guide)

📊 Content Exported:
- {export_result['total_records']} total database records
- All articles, categories, reviews, releases
- Complete database schema and data

🚀 Ready for Fresh Installation!
    """)