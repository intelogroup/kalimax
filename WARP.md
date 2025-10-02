# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**Kalimax** is a culturally-aware English-Haitian Creole translation system built on Meta's NLLB-200 model with LoRA fine-tuning. The project focuses on medical and cultural contexts, using a unique "Hiccup Corpus" methodology to capture challenging translation cases. 

**Key Technologies**: PyTorch, Transformers (Hugging Face), PEFT/LoRA, QLoRA quantization, FastAPI, Gradio  
**Budget**: $200/month (on-demand GPU rentals)  
**Timeline**: 5 months (Crawl-Walk-Run approach)  
**Current Phase**: Phase 1 - CRAWL (Foundation Setup)

## Development Commands

### Environment Setup
```powershell
# Create conda environment
conda create -n kalimax-ht python=3.8
conda activate kalimax-ht

# Install dependencies
pip install -r requirements.txt

# Run initial setup (creates directories, downloads NLLB model, tests basic translation)
python scripts/setup.py
```

### Testing
```powershell
# Run all tests (when implemented)
pytest tests/

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_translator.py

# Run single test
pytest tests/test_translator.py::test_basic_translation
```

### Code Quality
```powershell
# Format code with Black
black src/ scripts/ tests/

# Lint with flake8
flake8 src/ scripts/ tests/

# Run pre-commit hooks (if configured)
pre-commit run --all-files
```

### Training and Model Development
```powershell
# Test NLLB model inference (manual test during setup)
python -c "from src.translator import KalimaxTranslator; t = KalimaxTranslator(); print(t.translate('Hello'))"

# Training scripts will be added to scripts/ as development progresses
# Training runs will use on-demand GPU services (Vast.ai, RunPod, Lambda Labs)
```

### Data Management
```powershell
# Hiccup corpus workflow: Google Sheets → CSV → JSON
# CSV files will be placed in data/hiccup_corpus/
# Processed files go to data/processed/

# List data files
Get-ChildItem -Path data -Recurse -File

# Check data directory structure
tree data /F
```

## Code Architecture

### Core Translation Pipeline

The system uses a **modular, parameter-efficient fine-tuning approach**:

1. **Base Model Layer**: NLLB-200-distilled-600M (600M parameters)
   - Meta's NLLB (No Language Left Behind) model, optimized for low-resource languages
   - Superior to M2M-100 for Haitian Creole translation

2. **Fine-tuning Layer**: LoRA (Low-Rank Adaptation)
   - QLoRA with 4-bit quantization for memory efficiency
   - Target modules: `q_proj`, `v_proj`, `k_proj`, `out_proj`
   - Rank (r): 8, Alpha: 32, Dropout: 0.05
   - Cost-effective training on on-demand GPUs

3. **Data Pipeline**: "Hiccup Corpus" Methodology
   - Google Sheets for expert annotation of challenging cases
   - Structured schema: `id`, `src_en`, `tgt_ht_literal`, `tgt_ht_localized`, `domain`, `cultural_note`, `flags`, `editor_notes`, `provenance`
   - CSV export → JSON conversion → training data
   - Oversampling of difficult cases for focused learning

4. **Deployment Pipeline**:
   - Phase 1 (Current): Free Hugging Face Spaces with Gradio UI
   - Phase 2: Small VPS with FastAPI for production API
   - Progressive scaling based on usage

### Directory Structure

```
src/                          # Core source code (main translation logic)
├── translator.py             # KalimaxTranslator class (main interface)
├── __init__.py              # Package initialization

data/                         # All datasets and corpora
├── raw/                     # Original datasets
├── processed/               # Cleaned and formatted data
├── hiccup_corpus/           # Expert-curated difficult cases (CSV files)
└── examples/                # Small example datasets (tracked in git)

models/                       # Model artifacts (ignored by git - too large)
├── base/                    # Base NLLB-200 model
├── lora_adapters/           # Fine-tuned LoRA adapters
└── cache/                   # Hugging Face model cache

configs/                      # Configuration files
└── base_config.yaml         # Main configuration (model, LoRA, training, data, API settings)

scripts/                      # Utility and automation scripts
└── setup.py                 # Initial setup: directories, model download, basic tests

outputs/                      # Training outputs (ignored by git)
├── training/                # Training checkpoints and logs
└── evaluation/              # Evaluation results

notebooks/                    # Jupyter notebooks for experimentation

tests/                        # Unit and integration tests (to be implemented)

logs/                         # Application logs (ignored by git)
```

### Key Design Patterns

**Configuration-Driven Development**: All hyperparameters, paths, and settings in `configs/base_config.yaml`
- Model settings, LoRA parameters, training config, data paths, API settings
- Language codes use NLLB format: `eng_Latn` (English), `hat_Latn` (Haitian Creole)

**Result Object Pattern**: `TranslationResult` dataclass contains:
- `translation` (str): The translated text
- `confidence` (float): Translation confidence score
- `cultural_notes` (Optional[str]): Cultural context annotations
- `domain` (Optional[str]): Domain classification (e.g., "medical")
- `processing_time` (Optional[float]): Inference latency

**Expert-in-the-Loop**: Human evaluation is core to the workflow
- Weekly expert review cycles
- Cultural appropriateness scoring (target: 90%+)
- Systematic error categorization and feedback integration

### Development Phases (Crawl-Walk-Run)

**Phase 1: CRAWL (Months 1-2)** - Foundation Building
- ✅ Project setup and infrastructure
- Current: Data collection, NLLB integration, LoRA configuration, hiccup corpus workflow
- Deliverable: 500+ curated examples, functional training pipeline

**Phase 2: WALK (Months 3-4)** - Training & Evaluation
- Full LoRA training runs, human evaluation framework
- Iterative improvement based on expert feedback
- Target: +20% BLEU score improvement, 90%+ cultural adequacy

**Phase 3: RUN (Month 5+)** - Production & Pilot
- Production API deployment, pilot partner onboarding
- Continuous improvement pipeline, performance monitoring

### Budget Constraints

**Critical**: This project operates under strict budget limits ($200/month)
- Use **on-demand GPU rentals** (Vast.ai, RunPod, Lambda Labs) instead of monthly subscriptions
- ~$5-10 per training run on RTX 3090/4090
- Batch multiple experiments in single GPU session
- Free tier usage maximized (HF Spaces, cloud storage free tiers)

### Domain-Specific Considerations

**Medical Translation Focus**: 
- Emergency phrases, symptom descriptions, treatment explanations
- Cultural sensitivity in medical communication is paramount
- Terminology accuracy for medications and procedures

**Cultural Awareness**:
- Literal vs. localized translations (captured in hiccup corpus)
- Preferred terminology in Haitian Creole community
- Cultural context annotations guide model training

### Testing Strategy

Current Status: Basic testing infrastructure in place, comprehensive tests to be implemented

When writing tests:
- Use pytest framework
- Mock model loading for speed (NLLB model is 600MB+)
- Focus on data pipeline validation and cultural annotation preservation
- Human evaluation results should be version-controlled

## Important File Locations

- **Main translator class**: `src/translator.py`
- **Configuration**: `configs/base_config.yaml`
- **Setup script**: `scripts/setup.py`
- **Requirements**: `requirements.txt`
- **Project tracking**: `AGENT.md` (current status), `masterplan.md` (detailed roadmap)
- **README**: `README.md` (public-facing documentation)

## Language and Translation Details

**Language Codes** (NLLB format):
- English: `eng_Latn`
- Haitian Creole: `hat_Latn`

**Model Identifier**: `facebook/nllb-200-distilled-600M`

**Key Translation Parameters**:
- Max sequence length: 512 tokens
- Default batch size: 4 (with gradient accumulation)
- Generation strategy: Beam search with forced target language token

## Development Workflow

1. **Always check current phase status** in `AGENT.md` before making changes
2. **Respect budget constraints**: Avoid unnecessary GPU usage or cloud resources
3. **Data validation**: All hiccup corpus entries must follow schema strictly
4. **Version control**: Commit training runs with hyperparameters and results documented
5. **Expert review required**: Cultural annotations must be validated before training
6. **Progressive deployment**: Test on free HF Spaces before considering paid infrastructure

## Notes for Future Development

- **LoRA training scripts**: To be implemented in `src/training/` directory
- **Evaluation metrics**: BLEU, chrF, TER implementations to be added to `src/evaluation/`
- **Data processing utilities**: CSV→JSON converters to be added to `src/data/`
- **Model deployment**: Gradio interface code for HF Spaces deployment
- **API wrapper**: FastAPI implementation for production endpoints

## Current Development Status

**Week 1 Progress** (from AGENT.md):
- ✅ Repository structure initialized
- ✅ README and documentation created
- ✅ Basic translator class structure
- ⏳ Development environment setup (pending)
- ⏳ GPU service registration (pending)
- ⏳ Hiccup corpus Google Sheet creation (pending)
- ⏳ NLLB model download and testing (pending)

See `AGENT.md` for detailed weekly progress tracking and `masterplan.md` for comprehensive 5-month roadmap.
