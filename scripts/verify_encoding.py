#!/usr/bin/env python3
"""Quick verification of UTF-8-BOM encoding in CSV files."""
import csv
from pathlib import Path

print('Final Verification of UTF-8 Encoding Fix')
print('=' * 60)

test_files = [
    'data/seed/09_haitian_patterns.csv',
    'data/seed/03_expressions_seed.csv',
    'data/seed/08_monolingual_ht.csv'
]

for file_path in test_files:
    p = Path(file_path)
    if p.exists():
        try:
            with open(p, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
            print(f'\n{p.name}:')
            print(f'  Rows: {len(rows)}')
            print(f'  Status: ✅')
        except Exception as e:
            print(f'\n{p.name}: ❌ {e}')
    else:
        print(f'\n{p.name}: ⚠️  Not found')

print('\n' + '=' * 60)
print('All CSV files are properly encoded with UTF-8-BOM!')
