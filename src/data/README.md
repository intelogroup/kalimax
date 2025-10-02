# Kalimax Data Management Infrastructure

Complete data management system for culturally-aware Haitian Creole translation training data.

## Overview

This directory contains tools for managing the Kalimax corpus:
- **SQLite database schema** with 10+ specialized tables
- **Normalization pipeline** for text preprocessing
- **Training export** with weights, tags, and control tokens
- **Profanity corpus** for harsh language detection

## Quick Start

```powershell
# 1. Initialize database
python src/data/init_db.py

# 2. Test text normalization
python src/data/normalize_text.py

# 3. Export training data (dry-run)
python src/data/export_training.py --dry-run
```

## Database Schema

### Core Tables

1. **corpus** - Main parallel translation pairs
   - Literal vs localized translations
   - Cultural notes, dosage flags, idiom links
   - Context (audience, register, domain)

2. **glossary** - Difficult dictionary
   - Medical/cultural sensitive terms
   - Preferred patient-facing terminology
   - Aliases and alternatives

3. **expressions** - Idioms and proverbs
   - Literal glosses + idiomatic translations
   - Register and regional variants

4. **high_risk** - Safety-critical medical translations
   - Structured dosage information
   - Safety flags for human review

5. **profanity** - Harsh language corpus
   - Severity levels (mild → extreme)
   - Safe alternatives
   - Context where acceptable

6. **normalization_rules** - Text variant mappings
   - Slang → canonical forms
   - Contractions expansion

7. **corrections** - Human feedback log
   - Continuous learning source
   - Audit trail

8. **challenge** - Held-out evaluation sets
   - Never used for training
   - Multiple difficulty levels

9. **monolingual_ht / monolingual_en** - Monolingual corpora
   - For DAPT and back-translation

10. **metadata** - Database versioning

## Tools

### init_db.py

Initialize the database from schema.

```powershell
python src/data/init_db.py          # Create database
python src/data/init_db.py --stats   # Show statistics
```

### normalize_text.py

Text normalization utilities.

**Features:**
- Unicode NFC normalization
- Punctuation/whitespace cleanup
- Haitian Creole contraction expansion
- Dosage pattern detection
- Variant generation

**Usage:**
```python
from src.data.normalize_text import TextNormalizer

normalizer = TextNormalizer(db_path="data/kalimax_corpus.db")
clean_text = normalizer.normalize("M'gen yon tèt fè mal")
# Output: "mwen gen yon tèt fè mal"

has_dosage = normalizer.detect_dosage_pattern("Pran 2 tablèt chak 6 èdtan")
# Output: True
```

### export_training.py

Export corpus to training-ready JSONL with weights and tokens.

**Features:**
- Two-row format (literal/localized) or mode-token format
- Automatic weight calculation by domain
- Control tokens: `<src:LANG> <tgt:LANG> <domain:DOMAIN> <audience:AUDIENCE>`
- Filtering by curation status

**Usage:**
```powershell
# Dry-run export (200 rows)
python src/data/export_training.py --dry-run

# Full export (reviewed+ only)
python src/data/export_training.py --status reviewed

# Export with mode tokens
python src/data/export_training.py --format mode_token

# Limited export for testing
python src/data/export_training.py --limit 500
```

**Output format:**
```json
{
  "id": "c_1001_loc",
  "input_text": "<src:eng_Latn> <tgt:hat_Latn> <domain:medical> <audience:patient> We need to remove your gallbladder.",
  "target_text": "Nou dwe retire sak bil ou.",
  "weight": 3.0,
  "tags": ["mode:localized", "domain:medical", "status:reviewed"],
  "metadata": {
    "cultural_note": "Prefer 'sak bil' with patients",
    "provenance": "seed_clinic_2025"
  }
}
```

## Sampling Weights

Weights for oversampling important data:

| Type | Weight | Rationale |
|------|--------|-----------|
| Medical localized | 3.0× | Patient-facing priority |
| Medical literal | 1.0× | Baseline |
| Idioms | 4.0× | Heavy oversample for coverage |
| Profanity | 2.0× | Ensure model awareness |
| High-risk dosage | 0.7× | Lower (needs strict QA) |
| Synthetic | 0.5× | Lower confidence |

## Data Workflow

1. **Collect** → Raw sources (PDFs, CSVs, APIs)
2. **Normalize** → Unicode, punctuation, contractions
3. **Ingest** → SQLite with metadata
4. **Annotate** → Expert review (Google Sheets export)
5. **Re-import** → Updated entries with fixes
6. **Export** → Training JSONL with weights/tokens
7. **Train** → LoRA fine-tuning
8. **Evaluate** → Challenge sets + human eval
9. **Collect corrections** → Log to corrections table
10. **Iterate** → Back to step 6

## Profanity Corpus

### Purpose
Teach model to:
- Recognize harsh language
- Flag appropriately
- Suggest safe alternatives
- Understand medical/educational contexts where terms are acceptable

### Schema Fields
- `term_creole` / `term_english` - The harsh terms
- `severity` - mild | moderate | severe | extreme
- `category` - profanity | slur | sexual | violence | religious | body | illness
- `safe_alternatives_ht` / `safe_alternatives_en` - JSON lists
- `should_flag` / `should_block` - Behavior flags
- `context` - JSON: when usage might be acceptable

### Example Entry
```json
{
  "id": "prof_001",
  "term_creole": "[redacted example]",
  "term_english": "[equivalent]",
  "severity": "severe",
  "category": "profanity",
  "safe_alternatives_ht": ["[alternative1]", "[alternative2]"],
  "should_flag": 1,
  "should_block": 0,
  "context": {"medical": "acceptable in symptom description"},
  "cultural_note": "Extremely offensive in most contexts"
}
```

## Context Schema

All corpus entries can include context JSON:

```json
{
  "audience": "patient|clinician|general",
  "speaker_role": "doctor|nurse|translator|system",
  "register": "formal|neutral|informal|slang",
  "region": "N-HT|S-HT|Diaspora|Unknown",
  "formality": "formal|neutral|informal",
  "sensitivity": "high|medium|low"
}
```

## Next Steps

1. **Seed data** - Create initial CSVs (50 glossary, 200 corpus, 20 expressions, 10 profanity)
2. **Ingest pipeline** - Build `ingest_sources.py` for bulk imports
3. **Annotation workflow** - Export → Sheets → Re-import cycle
4. **Training integration** - Wire export → LoRA training pipeline
5. **Evaluation** - Build challenge set evaluation script

## Files

```
src/data/
├── README.md              # This file
├── init_db.py             # Database initialization
├── normalize_text.py      # Text normalization utilities
├── export_training.py     # Training data export
└── ingest_sources.py      # (TODO) Bulk data ingestion

data/
├── schema.sql             # Database schema
├── kalimax_corpus.db      # SQLite database (created)
└── training_export.jsonl  # Exported training data
```

## Database Location

Default: `data/kalimax_corpus.db` (relative to project root)

All scripts use this path by default. The database is gitignored.

## Version

Schema version: 1.0.0  
Last updated: 2025-10-02
