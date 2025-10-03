#!/usr/bin/env python3
"""
Analyze and merge glossary CSV files, removing duplicates and cleaning data.
"""
import csv
from pathlib import Path
from collections import defaultdict

def analyze_glossary_files():
    """Analyze all glossary CSV files."""
    print("=" * 70)
    print("GLOSSARY FILES ANALYSIS")
    print("=" * 70)
    
    glossary_files = [
        'data/seed/01_glossary_seed.csv',
        'data/seed/01_glossary_seed_BULK.csv',
        'data/seed/01_glossary_bulk_500.csv'
    ]
    
    all_data = []
    
    for file_path in glossary_files:
        p = Path(file_path)
        if not p.exists():
            print(f"\n⚠️  {p.name} - NOT FOUND")
            continue
            
        try:
            with open(p, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
            print(f"\n📄 {p.name}")
            print(f"   Rows: {len(rows)}")
            if rows:
                print(f"   Columns: {list(rows[0].keys())}")
                print(f"   Sample: {rows[0]}")
                all_data.extend([(file_path, row) for row in rows])
            else:
                print("   ⚠️  Empty file")
                
        except Exception as e:
            print(f"\n❌ {p.name} - Error: {e}")
    
    return all_data

def merge_glossary_files(all_data):
    """Merge glossary files, removing duplicates based on creole term."""
    print("\n" + "=" * 70)
    print("MERGING GLOSSARY FILES")
    print("=" * 70)
    
    # Track unique entries by creole term (case-insensitive)
    seen = {}
    duplicates = defaultdict(list)
    
    for source_file, row in all_data:
        creole = row.get('creole_canonical', '').strip()
        if not creole:
            continue
            
        key = creole.lower()
        
        if key in seen:
            duplicates[key].append((source_file, row))
        else:
            seen[key] = (source_file, row)
    
    print(f"\n📊 Statistics:")
    print(f"   Total entries processed: {len(all_data)}")
    print(f"   Unique entries: {len(seen)}")
    print(f"   Duplicates found: {len(duplicates)}")
    
    if duplicates:
        print(f"\n🔍 Sample duplicates (first 5):")
        for i, (key, dups) in enumerate(list(duplicates.items())[:5]):
            print(f"\n   {i+1}. '{key}':")
            original_file, original = seen[key]
            print(f"      Original: {Path(original_file).name}")
            for dup_file, dup in dups:
                print(f"      Duplicate: {Path(dup_file).name}")
    
    # Create merged data
    merged_data = [row for _, row in seen.values()]
    
    return merged_data

def save_merged_glossary(merged_data):
    """Save merged glossary to a new file."""
    output_path = Path('data/seed/01_glossary_merged.csv')
    
    if not merged_data:
        print("\n❌ No data to save!")
        return
    
    # Ensure all expected columns are present
    fieldnames = list(merged_data[0].keys())
    
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged_data)
    
    print(f"\n✅ Merged glossary saved to: {output_path}")
    print(f"   Total entries: {len(merged_data)}")
    print(f"   Columns: {fieldnames}")

def main():
    # Analyze files
    all_data = analyze_glossary_files()
    
    if not all_data:
        print("\n❌ No glossary data found!")
        return
    
    # Merge files
    merged_data = merge_glossary_files(all_data)
    
    # Save merged file
    save_merged_glossary(merged_data)
    
    print("\n" + "=" * 70)
    print("✅ GLOSSARY MERGE COMPLETE!")
    print("=" * 70)

if __name__ == '__main__':
    main()
