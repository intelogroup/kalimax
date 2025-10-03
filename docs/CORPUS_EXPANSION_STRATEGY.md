# Corpus Expansion Strategy: 5,656 → 15,000+ Sentences

**Status:** In Progress  
**Current Size:** 5,656 parallel sentences  
**Target Size:** 15,000+ parallel sentences  
**Gap:** 9,344+ sentences needed

---

## Executive Summary

Expanding a medical translation corpus by 3x requires a **multi-pronged approach** combining:
1. **Template-based generation** (provides ~1,000-2,000 sentences)
2. **Paraphrasing & variation** of existing sentences (adds ~2,000-3,000)
3. **Human translation** of new medical content (critical for quality)
4. **Back-translation** augmentation (scalable but needs review)
5. **Data collection** from Haitian medical sources

**Timeline:** 2-6 months depending on resources

---

## Phase 1: Template-Based Generation (Complete)

### ✅ Completed
- Created `corpus_expansion_generator.py`
- Generated **138 initial sentences** from 42 templates
- Domains covered:
  - Chronic disease (82 sentences)
  - Mental health (10 sentences)
  - Preventive care (30 sentences)
  - Patient questions (16 sentences)

### 📈 Potential
With current approach: **~500-1,000 sentences maximum**
- Templates are finite
- Need to avoid repetitive/unnatural combinations
- Quality decreases with over-generation

**Contribution to goal:** ~1,000 sentences (11% of gap)

---

## Phase 2: Paraphrasing Existing Corpus (Recommended Next Step)

### Strategy
Take existing 5,656 sentences and create **1-2 paraphrases** each focusing on:
- Different registers (formal ↔ informal)
- Different phrasings (doctor-speak ↔ patient-speak)
- Synonyms and cultural variants

### Example Paraphrasing
**Original:**
- EN: "Take your medication every day"
- HT: "Pran renmèd ou chak jou"

**Paraphrase 1 (more formal):**
- EN: "You must take your medication daily"
- HT: "Ou dwe pran medikaman ou chak jou"

**Paraphrase 2 (emphatic):**
- EN: "Don't forget to take your medication every single day"
- HT: "Pa bliye pran renmèd ou chak jou san eksepsyon"

**Paraphrase 3 (patient-friendly):**
- EN: "Remember to take your medicine each day"
- HT: "Sonje pran renmèd ou tout jou"

### Implementation
```python
# Tool: scripts/generate_paraphrases.py
# Input: 02_corpus.csv (5,656 sentences)
# Process: Generate 1-2 paraphrases per sentence
# Output: 5,000-10,000 additional sentences
# Review required: Yes - human validation essential
```

### Potential Yield
- Conservative (1 paraphrase/sentence): **+5,656 sentences**
- Moderate (1.5 paraphrases/sentence): **+8,484 sentences**  
- Aggressive (2 paraphrases/sentence): **+11,312 sentences**

**⚠️ Caution:** Paraphrases must maintain:
- Cultural appropriateness
- Medical accuracy
- Natural Kreyol phrasing

**Contribution to goal:** ~5,000-8,000 sentences (55-85% of gap)

---

## Phase 3: Targeted Medical Content Translation

### High-Priority Gaps (from analysis)
1. **Chronic Disease Management** (need: 2,000 sentences)
   - Diabetes daily management
   - Hypertension medication adherence
   - Diet and lifestyle counseling

2. **Mental Health** (need: 1,500 sentences)
   - Depression screening (PHQ-9 style questions)
   - Anxiety assessment (GAD-7 style questions)
   - PTSD/trauma-informed care
   - Substance abuse counseling

3. **Women's Health** (need: 1,000 sentences)
   - Family planning
   - Prenatal care dialogues
   - Menstrual health
   - Menopause

4. **Pediatric Care** (need: 800 sentences)
   - Vaccination schedules
   - Growth & development
   - Common childhood illnesses
   - Parental instructions

5. **Patient Education** (need: 800 sentences)
   - Medication instructions
   - Post-operative care
   - Chronic disease self-management
   - When to seek emergency care

### Sources for Translation
1. **Public health materials**
   - WHO Haiti resources
   - MSPP (Haiti Ministry of Health) documents
   - PIH (Partners In Health) patient education

2. **Standard medical questionnaires**
   - PHQ-9 (depression)
   - GAD-7 (anxiety)
   - AUDIT (alcohol use)
   - Common clinical assessment tools

3. **Medical textbooks/guides**
   - Primary care protocols
   - Emergency medicine guidelines
   - Common chief complaints

### Implementation Approach
```bash
# 1. Collect English source material
# 2. Create translation batches (100-200 sentences)
# 3. Translate with cultural notes
# 4. Native speaker review
# 5. Add to corpus

# Timeline: 2-4 months with dedicated translator
# Cost: Varies (volunteer vs. paid translation)
```

**Contribution to goal:** ~6,000 sentences (65% of gap)

---

## Phase 4: Back-Translation Augmentation

### Concept
Use existing model to translate English medical text → Haitian Kreyol, then have human reviewers correct.

### Process
1. Collect 10,000 English medical sentences (easily available)
2. Machine translate EN→HT
3. Human review and correction (faster than translation from scratch)
4. Add corrected pairs to corpus

### Advantages
- **Scalable:** Can generate thousands quickly
- **Cost-effective:** Review faster than full translation
- **Diverse:** Can target specific domains easily

### Disadvantages
- **Quality variable:** MT errors need careful review
- **Cultural gaps:** MT may miss cultural nuances
- **Review burden:** Still needs substantial human time

### Realistic Yield
- With good MT model: **+5,000-10,000 sentences** after review
- Timeline: 3-6 months

**Contribution to goal:** ~5,000-10,000 sentences (55-110% of gap)

---

## Phase 5: Data Collection from Haitian Sources

### Natural Kreyol Medical Data
Sources:
1. **Radio transcripts** - Medical call-in shows
2. **Social media** - Health education posts in Kreyol
3. **Clinic notes** - (anonymized, with permission)
4. **Patient forums** - Health questions in Kreyol

### Implementation
```python
# Collect monolingual Kreyol medical text
# Use for:
# 1. Monolingual pre-training (DAPT)
# 2. Back-translate HT→EN→HT for validation
# 3. Extract common patient phrasings
```

### Ethical Considerations
- ✅ Anonymization required
- ✅ Permission/consent needed
- ✅ Cultural sensitivity paramount

**Contribution to goal:** Improves model quality more than quantity

---

## Recommended Roadmap

### 🎯 Goal: 15,000 sentences in 3-6 months

| Phase | Method | Sentences | Timeline | Priority | Status |
|-------|--------|-----------|----------|----------|--------|
| **Current** | Existing corpus | 5,656 | Complete | - | ✅ Done |
| **1** | Template generation | +1,000 | 1 week | High | ✅ In Progress |
| **2** | Paraphrasing existing | +5,000 | 4-6 weeks | **CRITICAL** | 🔄 Next |
| **3** | Targeted translation | +3,000 | 6-8 weeks | High | ⏳ Planned |
| **4** | Back-translation | +3,000 | 4-6 weeks | Medium | ⏳ Planned |
| **5** | Quality refinement | Review all | 2-4 weeks | High | ⏳ Final |
| **TOTAL** | | **17,656** | **3-6 months** | | |

### Monthly Milestones

**Month 1:**
- ✅ Complete template generation (+1,000)
- 🔄 Create paraphrasing system
- 🔄 Generate 2,500 paraphrases
- **Target:** 9,156 sentences

**Month 2:**
- Generate remaining paraphrases (+2,500)
- Begin targeted translation (high-priority domains)
- **Target:** 11,656 sentences

**Month 3:**
- Complete targeted translation (+1,500)
- Begin back-translation pipeline
- **Target:** 13,156 sentences

**Month 4-6:**
- Complete back-translation review
- Quality control and validation
- Native speaker final review
- **Target:** 15,000-18,000 sentences

---

## Quality Control Framework

### Every New Sentence Must Have:
1. ✅ Both literal AND localized Kreyol translations
2. ✅ Cultural note explaining translation choices
3. ✅ Domain tag
4. ✅ Provenance tracking
5. ✅ Curation status flag

### Review Levels:
- **Level 1:** Automated validation (encoding, format, completeness)
- **Level 2:** Native speaker linguistic review
- **Level 3:** Medical professional accuracy check
- **Level 4:** Cultural appropriateness assessment

### Acceptance Criteria:
- Medical accuracy: 100% (no errors in clinical info)
- Linguistic quality: 95%+ natural Kreyol
- Cultural appropriateness: 100% (no offensive/insensitive content)

---

## Tools & Resources Needed

### Immediate (Month 1):
- ✅ Paraphrasing generator script
- 🔄 Quality validation script
- 🔄 Deduplication tool

### Medium-term (Months 2-3):
- Translation memory system (CAT tool)
- Native speaker reviewers (2-3 people)
- Medical advisor for accuracy

### Long-term (Months 4-6):
- Back-translation pipeline
- Inter-rater agreement metrics
- Corpus statistics dashboard

---

## Budget Considerations

### Volunteer/Low-Cost Approach:
- **Total time:** 200-400 hours human review
- **Timeline:** 4-6 months
- **Cost:** Minimal (compute only)
- **Challenge:** Finding qualified Kreyol-speaking medical professionals

### Professional Translation Approach:
- **Translation rate:** $0.08-0.15/word
- **Estimated words:** ~100,000 words
- **Cost:** $8,000-$15,000 USD
- **Timeline:** 2-3 months
- **Advantage:** Higher quality, faster completion

### Hybrid Approach (Recommended):
- **Templates + paraphrasing:** Free (automated)
- **Priority translations:** $3,000-5,000 (paid professional)
- **Review & validation:** Volunteer/low-cost
- **Timeline:** 3-4 months
- **Total cost:** $3,000-5,000 USD

---

## Next Immediate Actions

### This Week:
1. ✅ Complete template generator (DONE)
2. 🔄 Create paraphrasing system
3. 🔄 Generate first 1,000 paraphrases
4. 🔄 Set up review workflow

### Next Week:
1. Recruit 2-3 native Kreyol reviewers
2. Create review guidelines
3. Begin paraphrase validation
4. Identify priority translation domains

### This Month:
1. Complete paraphrasing phase (+5,000 sentences)
2. Begin targeted translation (500-1,000 sentences)
3. Establish quality metrics
4. **Reach 10,000+ sentences**

---

## Success Metrics

### Quantitative:
- ✅ Corpus size: 15,000+ parallel sentences
- ✅ Domain coverage: All 10 priority domains represented
- ✅ Quality score: 95%+ pass review
- ✅ Encoding: 100% clean UTF-8
- ✅ Metadata: 100% complete

### Qualitative:
- ✅ Cultural appropriateness validated
- ✅ Medical accuracy confirmed
- ✅ Natural Kreyol phrasing
- ✅ Representative of patient language
- ✅ Useful for MT5 training

---

## Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Insufficient reviewers** | High | Start recruitment early; engage Haitian diaspora |
| **Quality degradation** | High | Strict acceptance criteria; multiple review levels |
| **Timeline slippage** | Medium | Parallel work streams; automate where possible |
| **Budget constraints** | Medium | Prioritize free methods (paraphrasing, templates) |
| **Cultural insensitivity** | High | Native speaker review mandatory; cultural consultant |

---

## Conclusion

Reaching 15,000 sentences is **achievable** but requires a **systematic, multi-method approach**:

1. **Quick wins:** Templates +1,000 (Done this week)
2. **Major push:** Paraphrasing +5,000 (Months 1-2)
3. **Quality content:** Targeted translation +3,000 (Months 2-4)
4. **Scale:** Back-translation +3,000 (Months 3-5)

**Most realistic path:** Focus on **paraphrasing existing corpus** as primary expansion method, supplemented by targeted translation for gap domains.

**Timeline:** 3-6 months with consistent effort  
**Cost:** $0-5,000 depending on approach  
**Result:** High-quality, culturally appropriate Haitian Kreyol medical corpus ready for MT5 training

---

**Next Step:** Create paraphrasing generator and begin Phase 2.
