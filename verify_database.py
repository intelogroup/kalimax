#!/usr/bin/env python3
"""
Verify SQLite database and show sample queries
"""

import sqlite3

def verify_kalimax_database():
    # Connect to database
    conn = sqlite3.connect('data/seed/kalimax_seed_data.db')
    cursor = conn.cursor()

    print('📊 Kalimax SQLite Database Summary')
    print('=' * 50)

    # Show database summary
    cursor.execute('SELECT * FROM database_summary;')
    results = cursor.fetchall()

    print('Table Name          Source File             Rows   File Size (KB)')
    print('-' * 70)
    for row in results:
        table, source, rows, timestamp, size_kb = row
        print(f'{table:<18} {source:<22} {rows:>6,} {size_kb:>7} KB')

    print()
    print('🔍 Sample Queries:')
    print('-' * 20)

    # Sample query 1: Medical terms from glossary
    print('1. Medical terms in glossary:')
    cursor.execute("SELECT creole_canonical, english_equivalents FROM glossary WHERE domain='medical' LIMIT 3;")
    for row in cursor.fetchall():
        print(f'   {row[0]} -> {row[1]}')

    print()

    # Sample query 2: High risk instructions
    print('2. High risk medical instructions:')
    cursor.execute("SELECT src_en FROM high_risk WHERE risk_level='high' LIMIT 3;")
    for row in cursor.fetchall():
        print(f'   - {row[0]}')

    print()

    # Sample query 3: Linguistic patterns by type
    print('3. Linguistic patterns by type:')
    cursor.execute("SELECT pattern_type, COUNT(*) as count FROM haitian_patterns GROUP BY pattern_type ORDER BY count DESC LIMIT 5;")
    for row in cursor.fetchall():
        print(f'   {row[0]}: {row[1]} patterns')

    print()

    # Sample query 4: Domain distribution
    print('4. Content by domain:')
    cursor.execute("SELECT domain, COUNT(*) as count FROM corpus GROUP BY domain ORDER BY count DESC LIMIT 5;")
    for row in cursor.fetchall():
        print(f'   {row[0]}: {row[1]} translation pairs')

    conn.close()
    print()
    print('✅ Database verification complete!')

if __name__ == "__main__":
    verify_kalimax_database()