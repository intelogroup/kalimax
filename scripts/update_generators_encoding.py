#!/usr/bin/env python3
"""
Update all generator scripts to use UTF-8-BOM encoding for Windows compatibility
"""
from pathlib import Path
import re


def update_generator_encoding(file_path):
    """Replace encoding='utf-8' with encoding='utf-8-sig' in generator scripts"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace encoding parameters
        updated = re.sub(
            r'encoding=["\']utf-8["\']',
            'encoding="utf-8-sig"',
            content
        )
        
        # Also handle .open() calls without explicit encoding
        updated = re.sub(
            r'\.open\(["\']w["\'],\s*newline=["\']["\']',
            '.open("w", encoding="utf-8-sig", newline=""',
            updated
        )
        
        if updated != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated)
            print(f"✅ Updated {file_path.name}")
            return True
        else:
            print(f"⏭️  {file_path.name} - no changes needed")
            return False
            
    except Exception as e:
        print(f"❌ {file_path.name}: {e}")
        return False


def main():
    """Update all generator scripts"""
    scripts_dir = Path('scripts')
    
    generators = [
        'generate_normalization_rules.py',
        'generate_profanity_list.py',
        'generate_challenge_set.py',
        'generate_monolingual_ht.py',
        'generate_haitian_patterns.py',
        'generate_corpus_bulk.py',
        'generate_glossary_bulk.py',
        'generate_expressions_bulk.py',
        'generate_high_risk_bulk.py',
    ]
    
    print("🔧 Updating generator scripts to use UTF-8-BOM encoding\n")
    
    updated_count = 0
    for gen_file in generators:
        file_path = scripts_dir / gen_file
        if file_path.exists():
            if update_generator_encoding(file_path):
                updated_count += 1
        else:
            print(f"⚠️  {gen_file} not found")
    
    print(f"\n✅ Updated {updated_count} generator scripts")
    print("   All future generated CSVs will use UTF-8-BOM encoding")


if __name__ == '__main__':
    main()
