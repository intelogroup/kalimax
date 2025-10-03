#!/usr/bin/env python3
"""
Convert Kalimax seed CSV files to SQLite database
Creates a comprehensive database with proper schema and indexes
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path
from datetime import datetime

def create_database_schema(conn):
    """Create database schema with appropriate tables and indexes."""
    
    cursor = conn.cursor()
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Create metadata table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_name TEXT NOT NULL,
        source_file TEXT NOT NULL,
        rows_imported INTEGER NOT NULL,
        import_timestamp TEXT NOT NULL,
        file_size_bytes INTEGER,
        description TEXT
    );
    """)
    
    # 1. Glossary table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS glossary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        creole_canonical TEXT NOT NULL,
        english_equivalents TEXT,
        aliases TEXT,
        domain TEXT,
        cultural_weight TEXT,
        preferred_for_patients INTEGER,
        part_of_speech TEXT,
        formality TEXT,
        frequency TEXT,
        region TEXT,
        polysemy TEXT,
        examples_good TEXT,
        examples_bad TEXT,
        notes TEXT,
        created_by TEXT,
        UNIQUE(creole_canonical)
    );
    """)
    
    # 2. Corpus table  
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS corpus (
        id INTEGER PRIMARY KEY,
        corpus_id TEXT UNIQUE NOT NULL,
        src_text TEXT NOT NULL,
        src_lang TEXT,
        tgt_text_literal TEXT,
        tgt_text_localized TEXT, 
        tgt_lang TEXT,
        domain TEXT,
        is_idiom INTEGER,
        contains_dosage INTEGER,
        context TEXT,
        cultural_note TEXT,
        provenance TEXT,
        curation_status TEXT
    );
    """)
    
    # 3. Expressions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expressions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        creole TEXT NOT NULL,
        literal_gloss_en TEXT,
        idiomatic_en TEXT,
        localized_ht TEXT,
        register TEXT,
        region TEXT,
        cultural_note TEXT
    );
    """)
    
    # 4. High risk medical instructions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS high_risk (
        id INTEGER PRIMARY KEY,
        high_risk_id TEXT UNIQUE NOT NULL,
        src_en TEXT NOT NULL,
        tgt_ht_literal TEXT,
        tgt_ht_localized TEXT,
        contains_dosage INTEGER,
        dosage_json TEXT,
        instruction_type TEXT,
        risk_level TEXT,
        safety_flags TEXT,
        require_human_review INTEGER,
        provenance TEXT,
        notes TEXT
    );
    """)
    
    # 5. Normalization rules
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS normalization (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        variant TEXT NOT NULL,
        canonical TEXT NOT NULL,
        english_equivalent TEXT,
        register TEXT,
        notes TEXT
    );
    """)
    
    # 6. Profanity terms
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profanity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        term_creole TEXT NOT NULL,
        term_english TEXT,
        severity TEXT,
        category TEXT,
        context_dependent INTEGER,
        alternative_suggestions TEXT,
        cultural_notes TEXT,
        provenance TEXT,
        status TEXT
    );
    """)
    
    # 7. Translation challenges
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS challenge (
        id INTEGER PRIMARY KEY,
        challenge_id TEXT UNIQUE NOT NULL,
        src_text_en TEXT,
        src_text_ht TEXT,
        tgt_text_en TEXT,
        tgt_text_ht TEXT,
        category TEXT,
        domain TEXT,
        difficulty TEXT,
        phenomenon TEXT,
        expected_behavior TEXT,
        notes TEXT,
        provenance TEXT,
        never_for_training INTEGER,
        source_file TEXT
    );
    """)
    
    # 8. Monolingual Haitian Kreyol corpus
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monolingual (
        id INTEGER PRIMARY KEY,
        mono_id TEXT UNIQUE NOT NULL,
        text TEXT NOT NULL,
        domain TEXT,
        register TEXT,
        region TEXT,
        topic TEXT,
        complexity TEXT,
        provenance TEXT,
        dataset_name TEXT,
        source_file TEXT
    );
    """)
    
    # 9. Haitian linguistic patterns
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS haitian_patterns (
        id INTEGER PRIMARY KEY,
        pattern_id TEXT UNIQUE NOT NULL,
        pattern_type TEXT NOT NULL,
        haitian_example TEXT NOT NULL,
        english_gloss TEXT,
        grammatical_description TEXT,
        linguistic_notes TEXT,
        frequency TEXT,
        difficulty TEXT,
        domain TEXT
    );
    """)
    
    # 10. Unpolite communication examples
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS unpolite (
        id INTEGER PRIMARY KEY,
        unpolite_id TEXT UNIQUE NOT NULL,
        src_text TEXT NOT NULL,
        src_lang TEXT,
        tgt_text_literal TEXT,
        tgt_text_localized TEXT,
        tgt_lang TEXT,
        domain TEXT,
        is_idiom INTEGER,
        contains_dosage INTEGER,
        context TEXT,
        cultural_note TEXT,
        provenance TEXT,
        curation_status TEXT
    );
    """)
    
    conn.commit()
    print("✅ Database schema created successfully")

def create_indexes(conn):
    """Create indexes for better query performance."""
    
    cursor = conn.cursor()
    
    indexes = [
        # Glossary indexes
        "CREATE INDEX IF NOT EXISTS idx_glossary_domain ON glossary(domain);",
        "CREATE INDEX IF NOT EXISTS idx_glossary_frequency ON glossary(frequency);",
        "CREATE INDEX IF NOT EXISTS idx_glossary_region ON glossary(region);",
        
        # Corpus indexes
        "CREATE INDEX IF NOT EXISTS idx_corpus_domain ON corpus(domain);",
        "CREATE INDEX IF NOT EXISTS idx_corpus_src_lang ON corpus(src_lang);",
        "CREATE INDEX IF NOT EXISTS idx_corpus_tgt_lang ON corpus(tgt_lang);",
        "CREATE INDEX IF NOT EXISTS idx_corpus_provenance ON corpus(provenance);",
        
        # High risk indexes
        "CREATE INDEX IF NOT EXISTS idx_high_risk_type ON high_risk(instruction_type);",
        "CREATE INDEX IF NOT EXISTS idx_high_risk_level ON high_risk(risk_level);",
        "CREATE INDEX IF NOT EXISTS idx_high_risk_dosage ON high_risk(contains_dosage);",
        
        # Pattern indexes
        "CREATE INDEX IF NOT EXISTS idx_patterns_type ON haitian_patterns(pattern_type);",
        "CREATE INDEX IF NOT EXISTS idx_patterns_frequency ON haitian_patterns(frequency);",
        "CREATE INDEX IF NOT EXISTS idx_patterns_difficulty ON haitian_patterns(difficulty);",
        "CREATE INDEX IF NOT EXISTS idx_patterns_domain ON haitian_patterns(domain);",
        
        # Full text search indexes (if supported)
        "CREATE INDEX IF NOT EXISTS idx_corpus_src_text ON corpus(src_text);",
        "CREATE INDEX IF NOT EXISTS idx_glossary_canonical ON glossary(creole_canonical);",
    ]
    
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
        except Exception as e:
            print(f"⚠️  Warning creating index: {e}")
    
    conn.commit()
    print("✅ Database indexes created successfully")

def import_csv_to_table(conn, csv_file, table_name, column_mapping=None):
    """Import CSV data into specified table."""
    
    csv_path = Path("data/seed") / csv_file
    
    if not csv_path.exists():
        print(f"⚠️  Warning: {csv_file} not found, skipping...")
        return 0
    
    print(f"📥 Importing {csv_file} -> {table_name}")
    
    try:
        # Read CSV with encoding handling
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
        except:
            df = pd.read_csv(csv_path, encoding='latin-1')
        
        # Apply column mapping if provided
        if column_mapping:
            df = df.rename(columns=column_mapping)
        
        # Clean up column names for SQLite
        df.columns = [col.replace(' ', '_').replace('-', '_').lower() for col in df.columns]
        
        # Handle special cases for different tables
        if table_name == 'corpus':
            df = df.rename(columns={'id': 'corpus_id'})
        elif table_name == 'high_risk':
            df = df.rename(columns={'id': 'high_risk_id'})
        elif table_name == 'challenge':
            df = df.rename(columns={'id': 'challenge_id'})
        elif table_name == 'monolingual':
            df = df.rename(columns={'id': 'mono_id'})
        elif table_name == 'haitian_patterns':
            df = df.rename(columns={'id': 'pattern_id'})
        elif table_name == 'unpolite':
            df = df.rename(columns={'id': 'unpolite_id'})
        
        # Convert to SQLite
        rows_imported = len(df)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        # Add metadata
        file_size = csv_path.stat().st_size
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO metadata (table_name, source_file, rows_imported, import_timestamp, file_size_bytes)
        VALUES (?, ?, ?, ?, ?)
        """, (table_name, csv_file, rows_imported, datetime.now().isoformat(), file_size))
        
        conn.commit()
        
        print(f"  ✅ {rows_imported:,} rows imported successfully")
        return rows_imported
        
    except Exception as e:
        print(f"  ❌ Error importing {csv_file}: {e}")
        return 0

def convert_csvs_to_sqlite():
    """Main function to convert all CSV files to SQLite database."""
    
    # Define output path
    db_path = Path("data/seed/kalimax_seed_data.db")
    
    print("🗄️  Creating Kalimax SQLite Database...")
    print(f"Database path: {db_path}")
    
    # Remove existing database if it exists
    if db_path.exists():
        db_path.unlink()
        print("🗑️  Removed existing database")
    
    # Create database connection
    conn = sqlite3.connect(str(db_path))
    
    # Create schema and indexes
    create_database_schema(conn)
    create_indexes(conn)
    
    # CSV files and corresponding table mappings
    csv_table_mapping = [
        ("01_glossary.csv", "glossary"),
        ("02_corpus.csv", "corpus"),
        ("03_expressions.csv", "expressions"), 
        ("04_high_risk.csv", "high_risk"),
        ("05_normalization.csv", "normalization"),
        ("06_profanity.csv", "profanity"),
        ("07_challenge.csv", "challenge"),
        ("08_monolingual.csv", "monolingual"),
        ("09_haitian_patterns.csv", "haitian_patterns"),
        ("10_unpolite.csv", "unpolite")
    ]
    
    total_rows = 0
    successful_imports = 0
    
    # Import each CSV file
    for csv_file, table_name in csv_table_mapping:
        rows = import_csv_to_table(conn, csv_file, table_name)
        if rows > 0:
            total_rows += rows
            successful_imports += 1
    
    # Create database summary view
    cursor = conn.cursor()
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS database_summary AS
    SELECT 
        table_name,
        source_file,
        rows_imported,
        import_timestamp,
        ROUND(file_size_bytes / 1024.0, 2) as file_size_kb
    FROM metadata
    ORDER BY rows_imported DESC;
    """)
    
    conn.commit()
    conn.close()
    
    # Final statistics
    db_size = db_path.stat().st_size / (1024 * 1024)  # MB
    
    print(f"\n🎉 SQLite database created successfully!")
    print(f"📁 Database file: {db_path}")
    print(f"💾 Database size: {db_size:.2f} MB")
    print(f"📊 Tables imported: {successful_imports}/10")
    print(f"📈 Total rows: {total_rows:,}")
    
    return db_path

def verify_database(db_path):
    """Verify the database was created correctly."""
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print(f"\n🔍 Database Verification:")
    print("=" * 50)
    
    # Get table information
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    
    for table_name, in tables:
        if table_name == 'metadata':
            continue
            
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cursor.fetchone()[0]
        
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        col_count = len(columns)
        
        print(f"📋 {table_name:<18} {row_count:>6,} rows × {col_count:>2} columns")
    
    conn.close()

if __name__ == "__main__":
    db_path = convert_csvs_to_sqlite()
    verify_database(db_path)
    
    print(f"\n🚀 Ready to use!")
    print(f"   Connect with: sqlite3 {db_path}")
    print(f"   Or use Python: sqlite3.connect('{db_path}')")
    print(f"   View summary: SELECT * FROM database_summary;")