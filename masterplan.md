# Haitian Creole Translation Project - Master Plan

## Executive Summary

This project implements a "Crawl, Walk, Run" approach to develop an accurate, culturally-aware English-Haitian Creole translation model using Meta's NLLB-200 as the base model, fine-tuned with LoRA (Low-Rank Adaptation) techniques. The strategy prioritizes budget efficiency ($200/month) and leverages domain expertise through a structured "hiccup corpus" workflow.

## Strategic Overview

### Core Innovation
- **Base Model**: Switch from M2M-100 to `nllb-200-distilled-600M` for superior low-resource language performance
- **Training Approach**: LoRA fine-tuning with on-demand GPU rentals for cost efficiency
- **Expert Integration**: Structured workflow to capture and integrate challenging translation cases
- **Deployment**: Progressive deployment from free HF Spaces to production-ready API

### Key Success Factors
1. **Domain Expertise Integration**: Systematic capture of translation "hiccups" and cultural nuances
2. **Budget Optimization**: On-demand GPU usage (~$5-10 per training run vs. monthly subscriptions)
3. **Quality Focus**: Human evaluation-driven iterative improvement
4. **Scalable Architecture**: Foundation for advanced features in future phases

## Technical Stack

### Core Components
- **Base Model**: `nllb-200-distilled-600M` (600M parameters, optimized for low-resource languages)
- **Fine-tuning**: PEFT/LoRA with QLoRA (4-bit quantization)
- **Training Infrastructure**: On-demand GPU rentals (RunPod, Vast.ai, Lambda Labs)
- **Deployment**: 
  - Phase 1: Free Hugging Face Spaces with Gradio
  - Phase 2: Small VPS with FastAPI for production API
- **Data Management**: Google Sheets → CSV → JSON pipeline for corpus management

### Development Environment
```
Python 3.8+
Key Libraries:
- transformers (Hugging Face)
- peft (Parameter-Efficient Fine-Tuning)
- bitsandbytes (quantization)
- datasets
- torch
- accelerate
- gradio (UI)
- fastapi (API)
- sacrebleu (evaluation)
```

## Implementation Phases

### Phase 1: CRAWL (Months 1-2) - Foundation
**Objective**: Establish core infrastructure and initial dataset

#### Week 1: Project Setup
- [ ] Initialize Git repository with proper structure
- [ ] Set up development environment (conda/pyenv)
- [ ] Install required dependencies
- [ ] Register with on-demand GPU services (RunPod, Vast.ai)
- [ ] Create "Hiccup Corpus" Google Sheet with defined schema
- [ ] Download and test NLLB-200-distilled-600M model

#### Weeks 2-3: Data Foundation
- [ ] Populate initial "Difficult Dictionary" (100+ entries)
- [ ] Gather/create initial parallel corpus (500+ high-quality medical sentences)
- [ ] Implement data preprocessing pipeline
- [ ] Set up tokenization and data loading scripts
- [ ] Create corpus management scripts (CSV → JSON conversion)

#### Week 4: Pipeline Validation
- [ ] Implement LoRA configuration for NLLB-200
- [ ] Perform dry-run training on 100-200 examples
- [ ] Deploy test model to private HF Space
- [ ] Validate end-to-end pipeline functionality
- [ ] Document training procedures

#### Deliverables
- Functional training pipeline
- Initial curated dataset (500+ examples)
- Basic HF Space deployment
- Documented workflow processes

### Phase 2: WALK (Months 3-4) - Iteration & Evaluation
**Objective**: Full training runs with human evaluation feedback loops

#### Month 3: First Full Training
- [ ] Expand dataset to 1000+ examples
- [ ] Implement comprehensive LoRA training script
- [ ] Execute first full training run on rented GPU
- [ ] Deploy resulting model to HF Space with Gradio interface
- [ ] Set up evaluation metrics (BLEU, chrF, TER)

#### Month 4: Evaluation & Refinement
- [ ] Conduct structured human evaluation (100-200 translations)
- [ ] Implement feedback collection system
- [ ] Analyze translation errors and cultural issues
- [ ] Integrate corrections into "Hiccup Corpus"
- [ ] Execute second training iteration
- [ ] Document quality improvements

#### Deliverables
- Trained LoRA adapter with demonstrated improvements
- Human evaluation framework and results
- Refined dataset with expert corrections
- Performance benchmarks and analysis

### Phase 3: RUN (Month 5+) - Pilot & Scale
**Objective**: Production-ready pilot deployment

#### Month 5: Pilot Deployment
- [ ] Deploy refined model as stable API
- [ ] Set up production monitoring
- [ ] Onboard pilot partners
- [ ] Implement usage analytics
- [ ] Establish feedback collection from real users

#### Beyond Month 5: Scaling
- [ ] Continuous data collection from pilot usage
- [ ] Plan advanced features (idiom detection, cultural flags)
- [ ] Seek additional funding based on pilot success
- [ ] Scale infrastructure as needed

## Budget Allocation ($200/month)

| Category | Monthly Cost | Notes |
|----------|-------------|--------|
| GPU Training | $30-50 | 2-3 full LoRA runs on RTX 3090/4090 |
| Data Storage | ~$5 | Cloud storage for datasets/models |
| Hosting (Pilot) | $0-30 | Free HF Spaces → Small VPS |
| Buffer/Contingency | $115+ | Substantial buffer for iterations |

### Cost Optimization Strategies
- Use spot instances when available
- Batch multiple experiments in single GPU session
- Leverage free tiers maximally before upgrading
- Monitor usage closely to avoid overruns

## Data Management Strategy

### "Hiccup Corpus" Workflow
1. **Capture**: Google Sheet with structured schema
   - Columns: id, src_en, tgt_ht_literal, tgt_ht_localized, domain, cultural_note, flags, editor_notes, provenance
2. **Collection**: Daily logging of challenging translation cases
3. **Annotation**: Expert annotation with cultural context
4. **Integration**: Weekly export → JSON conversion → training data update
5. **Training**: Oversampling difficult cases for model attention

### Quality Assurance
- Expert review of all cultural annotations
- Cross-validation with native speakers
- Systematic tracking of improvement areas
- Version control for all datasets

## Evaluation Framework

### Quantitative Metrics
- **BLEU Score**: Overall translation quality
- **chrF Score**: Character-level accuracy
- **TER**: Translation edit rate
- **Custom Metrics**: Cultural appropriateness scoring

### Qualitative Assessment
- **Adequacy**: Meaning preservation
- **Fluency**: Natural language flow  
- **Cultural Safety**: Appropriate cultural context
- **Domain Accuracy**: Medical/technical term precision

### Human Evaluation Protocol
1. Batch evaluation sessions (100-200 samples)
2. Multi-rater agreement analysis
3. Error categorization and prioritization
4. Feedback integration into training data
5. Progress tracking over iterations

## Risk Management

### Technical Risks
- **GPU Availability**: Multiple provider accounts, flexible scheduling
- **Model Performance**: Baseline benchmarking, fallback strategies
- **Data Quality**: Expert validation, systematic review processes

### Budget Risks
- **Cost Overruns**: Conservative estimates, usage monitoring
- **GPU Price Fluctuations**: Multiple provider options, spot instances

### Timeline Risks
- **Scope Creep**: Strict phase boundaries, feature deferral
- **Technical Blockers**: Parallel development tracks, early validation

## Success Metrics

### Phase 1 (Foundation)
- [ ] Functional end-to-end pipeline
- [ ] 500+ curated training examples
- [ ] Baseline model performance established

### Phase 2 (Iteration)
- [ ] 20%+ improvement in BLEU score over baseline
- [ ] 90%+ human evaluation adequacy score
- [ ] 1000+ high-quality training examples

### Phase 3 (Pilot)
- [ ] Stable API with <2s response time
- [ ] Positive pilot partner feedback
- [ ] Clear scaling pathway identified
- [ ] ROI justification for continued funding

## Future Expansion Roadmap

### Advanced Features (Post-Pilot)
- **Layer E Implementation**: Idiom detection and high-risk flags
- **Multi-Domain Support**: Legal, educational, business contexts
- **Real-time Learning**: Continuous improvement from user feedback
- **Mobile Integration**: Offline model optimization
- **Voice Integration**: Speech-to-speech translation

### Scaling Considerations
- Infrastructure requirements for higher traffic
- Model size optimization for different use cases
- Partnership development for broader deployment
- Community contribution mechanisms

## Conclusion

This master plan provides a structured, budget-conscious approach to developing a high-quality Haitian Creole translation system. By leveraging NLLB-200's superior baseline performance, implementing cost-effective LoRA fine-tuning, and systematically integrating domain expertise, the project is positioned to deliver meaningful results within the 5-month timeline and $200/month budget constraint.

The phased approach ensures early wins while building toward a scalable, production-ready system that can serve as a foundation for more advanced features and broader community impact.

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-02  
**Next Review**: 2025-01-15