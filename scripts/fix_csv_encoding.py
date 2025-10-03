#!/usr/bin/env python3
"""
Fix UTF-8 encoding issues in CSV files

This script:
1. Detects encoding of CSV files
2. Re-encodes them to UTF-8 with BOM for better Windows compatibility
3. Ensures proper handling of Haitian Creole special characters (è, ò, à, etc.)

Usage:
  python scripts/fix_csv_encoding.py
"""
import csv
from pathlib import Path
import sys


def detect_encoding(file_path):
    """Attempt to detect file encoding by trying common encodings"""
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                f.read()
            return enc
        except (UnicodeDecodeError, LookupError):
            continue
    
    return None


def fix_csv_encoding(file_path, output_path=None):
    """Re-encode CSV file to UTF-8 with BOM"""
    if output_path is None:
        output_path = file_path
    
    # Detect current encoding
    encoding = detect_encoding(file_path)
    if encoding is None:
        print(f"❌ Could not detect encoding for {file_path.name}")
        return False
    
    print(f"📄 {file_path.name:35s} - detected: {encoding}")
    
    # Read with detected encoding
    try:
        with open(file_path, 'r', encoding=encoding, newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Write with UTF-8 BOM (better Windows compatibility)
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        print(f"   ✅ Re-encoded to UTF-8-BOM")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    """Process all CSV files in data/seed"""
    seed_dir = Path('data/seed')
    
    if not seed_dir.exists():
        print(f"❌ Directory not found: {seed_dir}")
        return 1
    
    csv_files = list(seed_dir.glob('*.csv'))
    
    if not csv_files:
        print(f"❌ No CSV files found in {seed_dir}")
        return 1
    
    print(f"🔍 Found {len(csv_files)} CSV files to process\n")
    
    success_count = 0
    for csv_file in sorted(csv_files):
        if fix_csv_encoding(csv_file):
            success_count += 1
    
    print(f"\n✅ Successfully processed {success_count}/{len(csv_files)} files")
    
    # Verify special characters
    print("\n🔍 Verifying Haitian Creole characters...")
    test_chars = ['è', 'ò', 'à', 'ù', 'É', 'Ò', 'À', 'Ù', 'ç', 'ñ']
    
    for csv_file in sorted(csv_files)[:3]:  # Check first 3 files
        try:
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                found_chars = [c for c in test_chars if c in content]
                if found_chars:
                    print(f"   {csv_file.name}: {', '.join(found_chars)}")
        except:
            pass
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
