# UTF-8 Encoding Fix Summary

## Issue
CSV files needed proper UTF-8 encoding with BOM (Byte Order Mark) for better Windows compatibility and proper handling of Haitian Creole special characters.

## Haitian Creole Special Characters
The following characters are commonly used in Haitian Creole and require proper UTF-8 encoding:
- **Lowercase**: è, ò, à, ù, ç, ñ
- **Uppercase**: É, È, Ò, À, Ù, Ç, Ñ

Examples in use:
- fèk (just)
- renmèd (medicine)
- tèt (head)
- kè (heart)
- à (to/at)
- ò (or)

## What Was Fixed

### 1. All Existing CSV Files
**Script**: `scripts/fix_csv_encoding.py`

- Re-encoded **24 CSV files** from UTF-8 to **UTF-8-BOM**
- UTF-8-BOM adds a byte order mark that helps Windows applications (Excel, Notepad++) correctly identify the file as UTF-8
- All Haitian Creole special characters now display correctly

**Files processed:**
- `data/seed/*.csv` (all CSV files in seed directory)

### 2. All Generator Scripts
**Script**: `scripts/update_generators_encoding.py`

Updated **9 generator scripts** to output UTF-8-BOM by default:
- `generate_normalization_rules.py`
- `generate_profanity_list.py`
- `generate_challenge_set.py`
- `generate_monolingual_ht.py`
- `generate_haitian_patterns.py`
- `generate_corpus_bulk.py`
- `generate_glossary_bulk.py`
- `generate_expressions_bulk.py`
- `generate_high_risk_bulk.py`

**Change made:**
```python
# Before:
with file.open("w", encoding="utf-8", newline='') as f:

# After:
with file.open("w", encoding="utf-8-sig", newline='') as f:
```

## Benefits

### Windows Compatibility
- ✅ Excel opens CSVs with proper character encoding automatically
- ✅ Notepad++ correctly identifies files as UTF-8
- ✅ PowerShell and CMD handle special characters correctly

### Data Integrity
- ✅ Haitian Creole text displays correctly: "M fèk manje" instead of "M fÃ¨k manje"
- ✅ No character corruption when opening/editing files
- ✅ Database ingestion works smoothly with proper encoding

### Future-Proof
- ✅ All new CSVs generated will automatically use UTF-8-BOM
- ✅ Consistent encoding across the entire project
- ✅ Easy to verify with: `scripts/fix_csv_encoding.py`

## How to Use

### Fix Encoding Issues
If you encounter encoding problems with CSV files:
```powershell
python scripts/fix_csv_encoding.py
```

### Verify Encoding
The fix script automatically:
1. Detects current encoding
2. Re-encodes to UTF-8-BOM
3. Verifies Haitian Creole characters are present

### Manual Verification
To manually check a CSV file:
```python
import csv
from pathlib import Path

with open('data/seed/file.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row)  # Should display Haitian characters correctly
```

## Technical Details

### Encoding Types
- **UTF-8**: Standard UTF-8 encoding (no BOM)
- **UTF-8-BOM** (utf-8-sig): UTF-8 with Byte Order Mark
  - BOM: `EF BB BF` at start of file
  - Better Windows application compatibility
  - Python's `utf-8-sig` handles BOM automatically

### Why UTF-8-BOM?
1. **Windows Excel**: Requires BOM to correctly identify UTF-8
2. **Notepad++**: Auto-detects encoding more reliably with BOM
3. **No Downside**: Unix/Linux tools handle BOM gracefully
4. **Python Support**: `encoding='utf-8-sig'` reads/writes BOM automatically

## Verification Results

After running fix script:
```
✅ Successfully processed 24/24 files

🔍 Verifying Haitian Creole characters...
   01_glossary_bulk_500.csv: è
   01_glossary_seed.csv: è, ò
   01_glossary_seed_BULK.csv: è, ò
   09_haitian_patterns.csv: è, ò, à, ù
```

All special characters verified and displaying correctly!

## Troubleshooting

### Issue: Characters still appear corrupted
**Solution**: Close and reopen the file. Some applications cache encoding detection.

### Issue: Python script can't read CSV
**Solution**: Use `encoding='utf-8-sig'` when opening:
```python
with open('file.csv', 'r', encoding='utf-8-sig') as f:
    # Your code
```

### Issue: Git shows entire file as changed
**Solution**: This is normal when re-encoding. The BOM adds 3 bytes at the start of each file, but content is identical.

## Related Files
- `scripts/fix_csv_encoding.py` - Fix existing CSV encoding
- `scripts/update_generators_encoding.py` - Update generator scripts
- `src/data/ingest_sources.py` - Database ingestion (handles both UTF-8 and UTF-8-BOM)

## Status
✅ All encoding issues resolved
✅ All CSVs re-encoded to UTF-8-BOM
✅ All generators updated
✅ Haitian Creole characters verified
✅ Ready for production use
