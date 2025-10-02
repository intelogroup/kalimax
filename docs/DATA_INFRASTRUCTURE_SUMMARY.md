# Kalimax Data Infrastructure - Build Summary

## ✅ What We Built

A complete, production-ready data management system for the Kalimax Haitian Creole translation project with **profanity corpus** included.

### Core Components

1. **SQLite Database Schema** (`data/schema.sql`)
   - 10 specialized tables with proper constraints and indices
   - Support for literal vs localized translations
   - Cultural notes and medical safety flags
   - **NEW: Profanity/harsh language corpus with severity levels**

2. **Database Initialization** (`src/data/init_db.py`)
   - Creates database from schema
   - Shows statistics
   - Validates table creation

3. **Text Normalization Pipeline** (`src/data/normalize_text.py`)
   - Unicode NFC normalization
   - Haitian Creole contraction expansion (m' → mwen, etc.)
   - Dosage pattern detection
   - Variant generation
   - Database-backed normalization rules

4. **Training Export System** (`src/data/export_training.py`)
   - JSONL export with control tokens
   - Automatic weight calculation by domain/mode
   - Two-row format (literal/localized) or mode-token format
   - Filtering by curation status
   - Dry-run mode for testing

5. **Profanity Corpus**
   - Severity levels: mild → moderate → severe → extreme
   - Categories: profanity, slur, sexual, violence, religious, body, illness
   - Safe alternatives in both languages
   - Context-aware (medical/educational exceptions)
   - Flags for should_flag/should_block behavior

### Database Tables

| Table | Purpose | Key Features |
|-------|---------|--------------|
| **corpus** | Main parallel pairs | Literal/localized, context, cultural notes, dosage flags |
| **glossary** | Difficult dictionary | Medical terms, cultural weight, patient-preferred forms |
| **expressions** | Idioms/proverbs | Literal gloss + idiomatic translation, regional variants |
| **high_risk** | Safety-critical medical | Structured dosage JSON, safety flags, human review required |
| **profanity** | Harsh language | Severity, category, safe alternatives, context |
| **normalization_rules** | Text variants | Slang → canonical, contraction expansion |
| **corrections** | Human feedback log | Continuous learning, audit trail |
| **challenge** | Held-out eval sets | Never for training, difficulty levels |
| **monolingual_ht/en** | Monolingual corpora | For DAPT and back-translation |
| **metadata** | Database versioning | Schema version, export tracking |

## 🎯 Key Features

### Sampling Weights (Automatic)
- **Medical localized**: 3.0× (patient-facing priority)
- **Medical literal**: 1.0× (baseline)
- **Idioms**: 4.0× (heavy oversample for coverage)
- **Profanity**: 2.0× (ensure model awareness)
- **High-risk dosage**: 0.7× (needs strict QA, less training weight)
- **Synthetic**: 0.5× (lower confidence)

### Control Tokens
Every training example includes:
```
<src:eng_Latn> <tgt:hat_Latn> <domain:medical> <audience:patient> [<mode:localized>] TEXT
```

### Context Schema
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

## 📊 Training Export Format

Example JSONL output:
```json
{
  "id": "c_1001_loc",
  "input_text": "<src:eng_Latn> <tgt:hat_Latn> <domain:medical> <audience:patient> We need to remove your gallbladder.",
  "target_text": "Nou dwe retire sak bil ou.",
  "weight": 3.0,
  "tags": ["mode:localized", "domain:medical", "status:reviewed"],
  "metadata": {
    "cultural_note": "Prefer 'sak bil' with patients; 'fyèl' may evoke death",
    "provenance": "seed_clinic_2025"
  }
}
```

## 🚀 Quick Start Commands

```powershell
# Initialize database
python src/data/init_db.py

# Test normalization
python src/data/normalize_text.py

# Dry-run export (200 rows)
python src/data/export_training.py --dry-run

# Full export (reviewed+ only)
python src/data/export_training.py --status reviewed

# View database stats
python src/data/init_db.py --stats
```

## 📁 Files Created

```
data/
└── schema.sql                      # Complete database schema (225 lines)

src/data/
├── __init__.py                     # Module exports
├── README.md                       # Comprehensive documentation (251 lines)
├── init_db.py                      # Database initialization (150 lines)
├── normalize_text.py               # Text normalization (288 lines)
└── export_training.py              # Training export (419 lines)

docs/
└── DATA_INFRASTRUCTURE_SUMMARY.md  # This file
```

**Total**: ~1,350 lines of production code + documentation

## 🔄 Data Workflow

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

## 🎓 What This Enables

### Immediate
- ✅ Database-backed corpus management
- ✅ Consistent text normalization
- ✅ Training-ready JSONL exports
- ✅ Profanity awareness and detection
- ✅ Cultural and medical safety tracking

### Next Steps (Week 2)
- Create seed data (50 glossary, 200 corpus, 20 expressions, 10 profanity)
- Build bulk ingestion pipeline (`ingest_sources.py`)
- Set up annotation workflow (Export → Sheets → Re-import)
- Run first LoRA dry-run training

### Medium-term (Weeks 3-4)
- Collect real medical translations
- Integrate human corrections loop
- Build challenge set evaluation
- Pilot deployment with corrections collection

## 🔒 Safety & Quality Features

1. **High-Risk Flagging**
   - Dosage detection with structured JSON
   - Automatic `require_human_review` flag
   - Safety flags for blocking/disclaimers

2. **Profanity Handling**
   - Model learns to recognize harsh language
   - Context-aware (medical exceptions)
   - Provides safe alternatives
   - Configurable flag/block behavior

3. **Cultural Awareness**
   - Cultural weight tracking (neutral|negative|positive|taboo)
   - Preferred patient-facing terms
   - Regional variant support
   - Cultural notes preserved in metadata

4. **Audit Trail**
   - Provenance for every entry
   - Human corrections logged
   - Dataset versioning
   - Curation status tracking (draft→reviewed→approved)

## 📈 What Changed from Original Plan

### Additions
1. ✅ **Profanity corpus** (as requested)
2. ✅ **Context schema** with explicit enumerations
3. ✅ **Structured dosage JSON** (not just boolean flag)
4. ✅ **Safety flags** (requires_disclaimer, block_if_uncertain, human_review_required)
5. ✅ **Normalization cache** from database
6. ✅ **Two export formats** (two-row and mode-token)
7. ✅ **Dry-run mode** for quick testing

### Refinements
- Consistent table naming (corpus, glossary, expressions, etc.)
- NLLB language codes everywhere (eng_Latn, hat_Latn)
- Unique constraints to prevent duplicates
- Comprehensive indexing for fast queries
- Weight calculation as explicit function (not magic numbers)
- Tags as list for filtering (not just metadata)

## 💡 Key Design Decisions

1. **SQLite over PostgreSQL**: Simpler for small team, portable, gitignore-friendly
2. **JSON for context/aliases**: Flexible schema evolution without migrations
3. **Two-row format default**: Simpler sampling logic than mode tokens
4. **Weight oversampling**: Mathematical approach to handling asymmetric data
5. **Control tokens**: Explicit conditioning vs implicit learning
6. **Curation status**: Draft→reviewed→approved workflow
7. **Profanity as separate table**: Allows independent curation and updates

## 🎉 What You Can Do Now

1. **Initialize the database** and explore the schema
2. **Test text normalization** with Haitian Creole examples
3. **Run a dry-run export** to see JSONL format
4. **Start collecting seed data** following the schema
5. **Review the comprehensive README** in `src/data/`
6. **Plan annotation workflow** using the export scripts

## 📚 Documentation

- **Full README**: `src/data/README.md` (comprehensive guide)
- **This summary**: `docs/DATA_INFRASTRUCTURE_SUMMARY.md`
- **Schema**: `data/schema.sql` (with inline comments)
- **Code comments**: All scripts heavily commented

## Next Meeting Topics

1. **Seed data collection**: Who will create initial 50 glossary entries?
2. **Profanity curation**: Source for Haitian Creole harsh language corpus?
3. **Annotation workflow**: Google Sheets template design?
4. **Training timeline**: When to run first LoRA dry-run?
5. **Medical expert access**: For high-risk validation?

---

**Status**: ✅ Complete and pushed to GitHub  
**Commit**: `b02cf1e` - Add complete data management infrastructure  
**Lines of Code**: ~1,350  
**Time to Build**: ~2 hours  
**Ready for**: Seed data collection and annotation workflow setup
