#!/usr/bin/env python3
"""
Fix UTF-8 encoding issues in Haitian Kreyol corpus files.

This script:
1. Detects encoding problems (double-encoded UTF-8, mojibake)
2. Fixes common Kreyol character corruption
3. Removes BOM (Byte Order Mark)
4. Re-saves with clean UTF-8 encoding
"""

import os
import sys
import csv
import chardet
from pathlib import Path
import shutil
from datetime import datetime


# Common Kreyol character corruptions (double-encoded UTF-8)
ENCODING_FIXES = {
    # è corruptions
    'Ã¨': 'è',
    'Ã©': 'é',
    'Ã ': 'à',
    'Ã´': 'ô',
    'Ã¹': 'ù',
    'Ãª': 'ê',
    'Ã®': 'î',
    'Ã»': 'û',
    'Ã¯': 'ï',
    'Ã¶': 'ö',
    
    # Accented capitals
    'Ã‰': 'É',
    'Ãˆ': 'È',
    'Ã€': 'À',
    'Ã"': 'Ô',
    'Ãš': 'Ù',
    'ÃŠ': 'Ê',
    'ÃŽ': 'Î',
    'Ã›': 'Û',
    
    # Special combinations seen in the corpus
    'fyÃ¨l': 'fyèl',
    'tÃ¨t': 'tèt',
    'bÃ­l': 'bíl',
    'kÃ¨': 'kè',
    'zÃ²rÃ¨y': 'zòrèy',
    'gÃ²j': 'gòj',
    'zÃ²tÃ¨y': 'zòtèy',
    
    # Other common patterns
    'Ã§': 'ç',
    'Ã±': 'ñ',
    'Ã¿': 'ÿ',
}


def detect_encoding(file_path):
    """Detect the actual encoding of a file."""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding'], result['confidence']


def has_bom(file_path):
    """Check if file starts with UTF-8 BOM."""
    with open(file_path, 'rb') as f:
        first_bytes = f.read(3)
        return first_bytes == b'\xef\xbb\xbf'


def remove_bom(content):
    """Remove BOM from string content."""
    if content.startswith('\ufeff'):
        return content[1:]
    return content


def fix_mojibake(text):
    """Fix common UTF-8 double-encoding issues."""
    if not text:
        return text
    
    fixed_text = text
    for wrong, correct in ENCODING_FIXES.items():
        fixed_text = fixed_text.replace(wrong, correct)
    
    return fixed_text


def fix_csv_file(input_path, output_path, backup_path):
    """Fix encoding issues in a CSV file."""
    print(f"\n{'='*60}")
    print(f"Processing: {input_path.name}")
    print(f"{'='*60}")
    
    # Detect current encoding
    detected_encoding, confidence = detect_encoding(input_path)
    print(f"Detected encoding: {detected_encoding} (confidence: {confidence:.2%})")
    
    # Check for BOM
    has_bom_marker = has_bom(input_path)
    if has_bom_marker:
        print("⚠️  BOM detected - will be removed")
    
    # Create backup
    shutil.copy2(input_path, backup_path)
    print(f"✅ Backup created: {backup_path.name}")
    
    # Read file
    try:
        with open(input_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try with detected encoding
        with open(input_path, 'r', encoding=detected_encoding) as f:
            content = f.read()
    
    # Remove BOM if present
    content = remove_bom(content)
    
    # Count issues before fixing
    issues_found = 0
    for wrong in ENCODING_FIXES.keys():
        count = content.count(wrong)
        if count > 0:
            issues_found += count
            print(f"  Found: '{wrong}' ({count} occurrences)")
    
    if issues_found == 0 and not has_bom_marker:
        print("✅ No encoding issues detected")
        return False
    
    if issues_found > 0:
        print(f"\n🔧 Fixing {issues_found} encoding issues...")
    elif has_bom_marker:
        print(f"\n🔧 Removing BOM...")
    
    # Fix mojibake
    fixed_content = fix_mojibake(content)
    
    # Write corrected file
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        f.write(fixed_content)
    
    print(f"✅ Fixed file saved: {output_path.name}")
    
    # Verify the fix
    with open(output_path, 'r', encoding='utf-8') as f:
        verification = f.read()
    
    verification_issues = 0
    for wrong in ENCODING_FIXES.keys():
        verification_issues += verification.count(wrong)
    
    if verification_issues == 0:
        print("✅ Verification passed - all issues resolved")
        return True
    else:
        print(f"⚠️  Warning: {verification_issues} issues remain after fixing")
        return True


def main():
    """Main execution function."""
    print("\n" + "="*60)
    print("HAITIAN KREYOL CORPUS ENCODING FIX UTILITY")
    print("="*60)
    
    # Setup paths
    project_root = Path(__file__).parent.parent
    seed_dir = project_root / 'data' / 'seed'
    backup_dir = project_root / 'data' / 'seed_backup'
    
    # Create backup directory with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = backup_dir / f"backup_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSource directory: {seed_dir}")
    print(f"Backup directory: {backup_dir}")
    
    # Find all CSV files
    csv_files = list(seed_dir.glob('*.csv'))
    
    if not csv_files:
        print("\n❌ No CSV files found in seed directory")
        sys.exit(1)
    
    print(f"\nFound {len(csv_files)} CSV files to process")
    
    # Process each file
    fixed_count = 0
    for csv_file in sorted(csv_files):
        backup_path = backup_dir / csv_file.name
        output_path = csv_file  # Overwrite original
        
        was_fixed = fix_csv_file(csv_file, output_path, backup_path)
        if was_fixed:
            fixed_count += 1
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Files processed: {len(csv_files)}")
    print(f"Files fixed: {fixed_count}")
    print(f"Files unchanged: {len(csv_files) - fixed_count}")
    print(f"\nBackups saved to: {backup_dir}")
    print("\n✅ Encoding fix complete!")
    print("\nNext steps:")
    print("1. Review the fixed files")
    print("2. Run your data loading scripts to verify")
    print("3. If issues remain, check the backup directory")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
