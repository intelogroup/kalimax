#!/usr/bin/env python3
"""
Initialize Kalimax corpus database from schema

This script creates the SQLite database and all tables based on schema.sql
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime


def init_database(db_path: str = "data/kalimax_corpus.db", schema_path: str = "data/schema.sql"):
    """
    Initialize the Kalimax corpus database
    
    Args:
        db_path: Path to SQLite database file
        schema_path: Path to SQL schema file
    """
    # Resolve paths relative to project root
    project_root = Path(__file__).parent.parent.parent
    db_file = project_root / db_path
    schema_file = project_root / schema_path
    
    # Ensure data directory exists
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if database already exists
    if db_file.exists():
        response = input(f"⚠️  Database already exists at {db_file}. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Aborted. Database unchanged.")
            return False
        db_file.unlink()
        print(f"🗑️  Deleted existing database")
    
    # Read schema
    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        return False
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Create database and execute schema
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        print(f"📊 Creating database at {db_file}")
        cursor.executescript(schema_sql)
        
        # Verify tables were created
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        tables = cursor.fetchall()
        
        print(f"✅ Created {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Update metadata
        cursor.execute("""
            UPDATE metadata 
            SET value = datetime('now'), updated_at = datetime('now')
            WHERE key = 'created_at'
        """)
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Database initialized successfully!")
        print(f"📍 Location: {db_file.absolute()}")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def get_db_stats(db_path: str = "data/kalimax_corpus.db"):
    """Print database statistics"""
    project_root = Path(__file__).parent.parent.parent
    db_file = project_root / db_path
    
    if not db_file.exists():
        print(f"❌ Database not found: {db_file}")
        return
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    print("\n📊 Database Statistics:")
    print("=" * 50)
    
    # Count rows in each main table
    tables = ['corpus', 'glossary', 'expressions', 'high_risk', 
              'normalization_rules', 'profanity', 'corrections', 
              'challenge', 'monolingual_ht', 'monolingual_en']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   {table:20s}: {count:>6,} rows")
    
    # Print metadata
    cursor.execute("SELECT key, value FROM metadata")
    metadata = cursor.fetchall()
    
    print("\n📋 Metadata:")
    print("=" * 50)
    for key, value in metadata:
        print(f"   {key:25s}: {value}")
    
    conn.close()


def main():
    """Main entry point"""
    print("🚀 Kalimax Corpus Database Initialization\n")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--stats':
            get_db_stats()
            return
        elif sys.argv[1] == '--help':
            print("Usage:")
            print("  python init_db.py          # Initialize database")
            print("  python init_db.py --stats  # Show database statistics")
            print("  python init_db.py --help   # Show this help")
            return
    
    success = init_database()
    
    if success:
        get_db_stats()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
