# Kalimax - Haitian Creole Healthcare Translation Model

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Hugging Face](https://img.shields.io/badge/🤗%20Hugging%20Face-Models-yellow)](https://huggingface.co/)

A culturally-aware English-Haitian Creole translation system built on NLLB-200 with LoRA fine-tuning, optimized for medical and cultural contexts.

## 🎯 Project Overview

Kalimax addresses the critical need for accurate, culturally-sensitive translation between English and Haitian Creole, particularly in medical and emergency contexts. By leveraging Meta's NLLB-200 model and expert-curated datasets, we deliver translations that preserve both linguistic accuracy and cultural appropriateness.

### Key Features
- **NLLB-200 Base Model**: Superior performance for low-resource languages
- **LoRA Fine-tuning**: Cost-effective, parameter-efficient training
- **Cultural Awareness**: Expert-annotated "hiccup corpus" for cultural nuances
- **Medical Focus**: Specialized terminology and context handling
- **Budget Optimized**: On-demand GPU training, <$50/month operational costs

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- CUDA-compatible GPU (for training)
- 16GB+ RAM recommended

### Installation
```bash
# Clone the repository
git clone https://github.com/intelogroup/kalimax.git
cd kalimax

# Create virtual environment
conda create -n kalimax-ht python=3.8
conda activate kalimax-ht

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage
```python
from src.translator import KalimaxTranslator

# Initialize translator
translator = KalimaxTranslator()

# Translate text
result = translator.translate(
    text="The patient needs immediate medical attention",
    source_lang="eng_Latn",
    target_lang="hat_Latn"
)

print(result.translation)  # Malad la bezwen atansyon medikal imedyatman
print(result.cultural_notes)  # Any cultural context notes
```

## 📁 Project Structure

```
kalimax/
├── src/                    # Core source code
│   ├── models/            # Model definitions and wrappers
│   ├── data/              # Data processing utilities
│   ├── training/          # Training scripts and configurations
│   └── evaluation/        # Evaluation metrics and tools
├── data/                  # Datasets and corpora
│   ├── raw/               # Original datasets
│   ├── processed/         # Cleaned and formatted data
│   └── hiccup_corpus/     # Expert-curated difficult cases
├── models/                # Trained model artifacts
│   ├── base/              # Base NLLB-200 model
│   └── lora_adapters/     # Fine-tuned LoRA adapters
├── scripts/               # Utility and automation scripts
├── notebooks/             # Jupyter notebooks for experimentation
├── tests/                 # Unit and integration tests
├── configs/               # Configuration files
└── docs/                  # Documentation
```

## 🔧 Development Phases

### Phase 1: CRAWL (Months 1-2) - Foundation
- [x] Project setup and infrastructure
- [ ] Data collection and preprocessing pipeline
- [ ] Initial NLLB-200 model integration
- [ ] LoRA configuration and testing
- [ ] Hiccup corpus workflow establishment

### Phase 2: WALK (Months 3-4) - Training & Evaluation  
- [ ] Full LoRA fine-tuning pipeline
- [ ] Human evaluation framework
- [ ] Iterative model improvement
- [ ] Hugging Face Space deployment

### Phase 3: RUN (Month 5+) - Production
- [ ] Production API deployment
- [ ] Pilot partner onboarding
- [ ] Continuous improvement pipeline
- [ ] Performance monitoring

## 📊 Performance Metrics

| Metric | Baseline (NLLB-200) | Current Model | Target |
|--------|---------------------|---------------|--------|
| BLEU Score | TBD | TBD | +20% improvement |
| chrF Score | TBD | TBD | +15% improvement |
| Cultural Adequacy | TBD | TBD | 90%+ |
| Response Time | <3s | TBD | <2s |

## 💡 The "Hiccup Corpus" Approach

Our unique methodology captures translation challenges through expert annotation:

1. **Capture**: Systematic logging of difficult translation cases
2. **Annotate**: Expert review with cultural context
3. **Train**: Oversampling challenging cases in training data
4. **Evaluate**: Human validation of cultural appropriateness
5. **Iterate**: Continuous improvement based on real-world usage

## 🛠️ Technology Stack

- **Base Model**: facebook/nllb-200-distilled-600M
- **Fine-tuning**: PEFT/LoRA with QLoRA quantization
- **Training**: PyTorch, Transformers, Accelerate
- **Deployment**: FastAPI, Gradio, Hugging Face Spaces
- **Infrastructure**: On-demand GPU (Vast.ai, RunPod)
- **Evaluation**: SacreBLEU, custom cultural metrics

## 🏥 Medical Domain Focus

Special attention to medical terminology and contexts:
- Emergency phrases and instructions
- Symptom descriptions and medical history
- Treatment explanations and medication instructions
- Cultural considerations in medical communication

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Areas for Contribution
- Translation quality evaluation
- Cultural context annotation  
- Medical terminology validation
- Model performance optimization
- Documentation improvements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Meta AI for the NLLB-200 model
- Hugging Face for the transformers library and hosting
- The Haitian Creole linguistic community
- Medical professionals providing domain expertise

## 📞 Contact

- **Project Lead**: [Your Name]
- **Organization**: InteloGroup
- **Email**: [contact@intelogroup.com]
- **Issues**: [GitHub Issues](https://github.com/intelogroup/kalimax/issues)

## 🗺️ Roadmap

See our [Master Plan](masterplan.md) for detailed project roadmap and [Agent Progress](AGENT.md) for current status.

---

**Built with ❤️ for the Haitian community**
