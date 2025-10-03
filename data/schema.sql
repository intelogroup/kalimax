-- Kalimax Corpus Database Schema
-- Complete schema for culturally-aware Haitian Creole translation training data

-- Core parallel corpus table
CREATE TABLE IF NOT EXISTS corpus (
  id TEXT PRIMARY KEY,
  src_text TEXT NOT NULL,
  src_lang TEXT DEFAULT 'eng_Latn' CHECK (src_lang IN ('eng_Latn', 'hat_Latn')),
  tgt_text_literal TEXT,
  tgt_text_localized TEXT,
  tgt_lang TEXT DEFAULT 'hat_Latn' CHECK (tgt_lang IN ('eng_Latn', 'hat_Latn')),
  domain TEXT CHECK (domain IN ('medical','public_health','general','legal','other')) NOT NULL,
  is_idiom INTEGER DEFAULT 0 CHECK (is_idiom IN (0, 1)),
  idiom_id TEXT,
  aliases TEXT,              -- JSON list of raw variants
  contains_dosage INTEGER DEFAULT 0 CHECK (contains_dosage IN (0, 1)),
  context TEXT,              -- JSON: audience, speaker_role, register, region, formality, sensitivity
  cultural_note TEXT,
  provenance TEXT,           -- source dataset/file/line
  confidence REAL CHECK (confidence BETWEEN 0.0 AND 1.0),
  dataset_name TEXT,
  dataset_version TEXT,
  curation_status TEXT CHECK (curation_status IN ('draft','reviewed','approved')) DEFAULT 'draft',
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  -- Code-switching support
  is_code_switched INTEGER DEFAULT 0 CHECK (is_code_switched IN (0, 1)),
  lang_tags TEXT,            -- JSON: spans with language tags [{"start": 0, "end": 5, "lang": "hat_Latn"}, ...]
  code_switch_note TEXT,     -- Explanation of code-switching elements
  FOREIGN KEY (idiom_id) REFERENCES expressions(id)
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_corpus_src_tgt_domain
  ON corpus(src_text, tgt_text_localized, domain);

CREATE INDEX IF NOT EXISTS idx_corpus_domain ON corpus(domain);
CREATE INDEX IF NOT EXISTS idx_corpus_dosage ON corpus(contains_dosage);
CREATE INDEX IF NOT EXISTS idx_corpus_idiom ON corpus(is_idiom);
CREATE INDEX IF NOT EXISTS idx_corpus_status ON corpus(curation_status);
CREATE INDEX IF NOT EXISTS idx_corpus_updated ON corpus(updated_at);
-- New index for code-switching
CREATE INDEX IF NOT EXISTS idx_corpus_code_switch ON corpus(is_code_switched);

-- Glossary / Difficult Dictionary
CREATE TABLE IF NOT EXISTS glossary (
  id TEXT PRIMARY KEY,
  creole_canonical TEXT NOT NULL,
  english_equivalents TEXT,   -- JSON list
  aliases TEXT,               -- JSON list of variants
  domain TEXT CHECK (domain IN ('medical','general','legal','other')) NOT NULL,
  cultural_weight TEXT CHECK (cultural_weight IN ('neutral','negative','positive','taboo')) DEFAULT 'neutral',
  preferred_for_patients INTEGER DEFAULT 1 CHECK (preferred_for_patients IN (0, 1)),
  recommended_alternative TEXT,
  examples_bad TEXT,
  examples_good TEXT,
  notes TEXT,
  provenance TEXT,
  created_by TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  -- Code-switching enhancements
  english_slang TEXT,         -- Direct English slang equivalent if applicable
  mixed_usage_context TEXT,   -- JSON: contexts where code-switching is common
  code_switch_examples TEXT   -- JSON list of code-switched examples
);

CREATE INDEX IF NOT EXISTS idx_glossary_domain ON glossary(domain);
CREATE INDEX IF NOT EXISTS idx_glossary_weight ON glossary(cultural_weight);

-- Expressions / Idioms
CREATE TABLE IF NOT EXISTS expressions (
  id TEXT PRIMARY KEY,
  creole TEXT NOT NULL,
  literal_gloss_en TEXT,
  idiomatic_en TEXT,
  localized_ht TEXT,
  register TEXT CHECK (register IN ('formal','neutral','informal','slang')) DEFAULT 'neutral',
  region TEXT,
  cultural_note TEXT,
  examples TEXT,            -- JSON list of usage examples
  provenance TEXT,
  created_by TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_expressions_register ON expressions(register);
CREATE INDEX IF NOT EXISTS idx_expressions_region ON expressions(region);

-- High-risk medical translations
CREATE TABLE IF NOT EXISTS high_risk (
  id TEXT PRIMARY KEY,
  src_en TEXT NOT NULL,
  tgt_ht_literal TEXT,
  tgt_ht_localized TEXT,
  contains_dosage INTEGER DEFAULT 1 CHECK (contains_dosage IN (0, 1)),
  dosage_json TEXT,         -- JSON: {drug, dose_qty, dose_unit, frequency_hours, max_daily_dose, duration_days}
  instruction_type TEXT CHECK (instruction_type IN ('dosage','triage','symptom','procedure')) NOT NULL,
  risk_level TEXT CHECK (risk_level IN ('high','medium','low')) DEFAULT 'high',
  safety_flags TEXT,        -- JSON list: ["requires_disclaimer","block_if_uncertain","human_review_required"]
  require_human_review INTEGER DEFAULT 1 CHECK (require_human_review IN (0, 1)),
  provenance TEXT,
  notes TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_high_risk_type ON high_risk(instruction_type);
CREATE INDEX IF NOT EXISTS idx_high_risk_level ON high_risk(risk_level);
CREATE INDEX IF NOT EXISTS idx_high_risk_dosage ON high_risk(contains_dosage);

-- Normalization rules (slang, contractions, variants)
CREATE TABLE IF NOT EXISTS normalization_rules (
  id TEXT PRIMARY KEY,
  variant TEXT NOT NULL,
  canonical TEXT NOT NULL,
  english_equivalent TEXT,
  register TEXT CHECK (register IN ('sms','chat','spoken','general')) DEFAULT 'general',
  region TEXT,
  examples TEXT,            -- JSON list
  provenance TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  -- Code-switching support
  code_switch_type TEXT CHECK (code_switch_type IN ('creole_to_english','english_to_creole','mixed','slang_injection')) DEFAULT NULL,
  language_origin TEXT,     -- source language of the borrowed element
  mixed_context_notes TEXT  -- usage context for code-switched forms
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_normalization_variant ON normalization_rules(variant);
CREATE INDEX IF NOT EXISTS idx_normalization_register ON normalization_rules(register);
-- New index for code-switching
CREATE INDEX IF NOT EXISTS idx_normalization_code_switch ON normalization_rules(code_switch_type);

-- Profanity / harsh language corpus
CREATE TABLE IF NOT EXISTS profanity (
  id TEXT PRIMARY KEY,
  term_creole TEXT NOT NULL,
  term_english TEXT,
  severity TEXT CHECK (severity IN ('mild','moderate','severe','extreme')) NOT NULL,
  category TEXT CHECK (category IN ('profanity','slur','sexual','violence','religious','body','illness','other')) NOT NULL,
  context TEXT,             -- JSON: when usage might be acceptable (medical, educational)
  safe_alternatives_ht TEXT, -- JSON list of alternatives
  safe_alternatives_en TEXT, -- JSON list
  cultural_note TEXT,
  should_flag INTEGER DEFAULT 1 CHECK (should_flag IN (0, 1)),
  should_block INTEGER DEFAULT 0 CHECK (should_block IN (0, 1)),
  region TEXT,
  provenance TEXT,
  notes TEXT,
  created_by TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_profanity_severity ON profanity(severity);
CREATE INDEX IF NOT EXISTS idx_profanity_category ON profanity(category);
CREATE INDEX IF NOT EXISTS idx_profanity_flag ON profanity(should_flag);

-- Human corrections log
CREATE TABLE IF NOT EXISTS corrections (
  id TEXT PRIMARY KEY,
  input_text TEXT NOT NULL,
  model_output TEXT NOT NULL,
  human_correction TEXT NOT NULL,
  correction_type TEXT CHECK (correction_type IN ('tone','accuracy','dosage','term','profanity','cultural','other','code_switch')) NOT NULL,
  severity TEXT CHECK (severity IN ('low','medium','high')) DEFAULT 'medium',
  editor_id TEXT,
  reason TEXT,
  timestamp TEXT DEFAULT (datetime('now')),
  used_for_retraining INTEGER DEFAULT 0 CHECK (used_for_retraining IN (0, 1)),
  applied_in_export_version TEXT
);

CREATE INDEX IF NOT EXISTS idx_corrections_type ON corrections(correction_type);
CREATE INDEX IF NOT EXISTS idx_corrections_severity ON corrections(severity);
CREATE INDEX IF NOT EXISTS idx_corrections_retraining ON corrections(used_for_retraining);
CREATE INDEX IF NOT EXISTS idx_corrections_timestamp ON corrections(timestamp);

-- Challenge sets (held-out evaluation data, never for training)
CREATE TABLE IF NOT EXISTS challenge (
  id TEXT PRIMARY KEY,
  src_text TEXT NOT NULL,
  src_lang TEXT DEFAULT 'eng_Latn',
  tgt_text TEXT NOT NULL,
  tgt_lang TEXT DEFAULT 'hat_Latn',
  challenge_type TEXT CHECK (challenge_type IN ('idioms','high_risk','regional','profanity','medical','cultural','code_switch')) NOT NULL,
  domain TEXT,
  difficulty TEXT CHECK (difficulty IN ('easy','medium','hard','expert')) DEFAULT 'medium',
  expected_behavior TEXT, -- what model should do (e.g., "flag as harsh", "use localized term")
  evaluation_notes TEXT,
  provenance TEXT,
  never_for_training INTEGER DEFAULT 1 CHECK (never_for_training IN (0, 1)),
  created_at TEXT DEFAULT (datetime('now')),
  -- Code-switching challenge support
  code_switch_pattern TEXT,  -- Description of code-switched elements
  mixed_lang_context TEXT    -- Context where this mixing occurs
);

CREATE INDEX IF NOT EXISTS idx_challenge_type ON challenge(challenge_type);
CREATE INDEX IF NOT EXISTS idx_challenge_difficulty ON challenge(difficulty);
CREATE INDEX IF NOT EXISTS idx_challenge_training ON challenge(never_for_training);

-- Monolingual Haitian Creole (for DAPT, back-translation)
CREATE TABLE IF NOT EXISTS monolingual_ht (
  id TEXT PRIMARY KEY,
  text TEXT NOT NULL,
  domain TEXT,
  register TEXT CHECK (register IN ('formal','neutral','informal','slang')),
  region TEXT,
  provenance TEXT,
  dataset_name TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_mono_ht_domain ON monolingual_ht(domain);

-- Haitian Creole Language Patterns (grammar, syntax, phonology for better HT understanding)
CREATE TABLE IF NOT EXISTS haitian_creole_patterns (
  id TEXT PRIMARY KEY,
  pattern_type TEXT CHECK (pattern_type IN ('grammar','syntax','phonology','morphology','tense','aspect','verb_conjugation','noun_phrase','question_formation','negation','serial_verbs','creole_features')) NOT NULL,
  haitian_example TEXT NOT NULL,
  english_gloss TEXT,
  grammatical_description TEXT,
  linguistic_notes TEXT,
  frequency TEXT CHECK (frequency IN ('very_common','common','uncommon','rare')) DEFAULT 'common',
  difficulty TEXT CHECK (difficulty IN ('basic','intermediate','advanced')) DEFAULT 'basic',
  domain TEXT,
  provenance TEXT,
  dataset_name TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_ht_patterns_type ON haitian_creole_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_ht_patterns_frequency ON haitian_creole_patterns(frequency);
CREATE INDEX IF NOT EXISTS idx_ht_patterns_difficulty ON haitian_creole_patterns(difficulty);

-- Code-switching training data
CREATE TABLE IF NOT EXISTS code_switch_examples (
  id TEXT PRIMARY KEY,
  src_text_mixed TEXT NOT NULL,     -- Original mixed-language text
  src_lang_primary TEXT DEFAULT 'hat_Latn',
  tgt_lang_primary TEXT DEFAULT 'eng_Latn',
  clean_translation TEXT,           -- Neutral/clinical translation
  annotated_translation TEXT,       -- Translation with preserved/cited slang
  src_lang_tags TEXT,              -- JSON: span-based language annotations
  tgt_lang_tags TEXT,              -- JSON: target language tags
  code_switch_type TEXT CHECK (code_switch_type IN ('english_injection','french_injection','spanish_injection','slang_borrowing','mixed_systemic')) DEFAULT 'english_injection',
  domain TEXT,
  context TEXT,                    -- Usage context
  provenance TEXT,
  confidence REAL DEFAULT 0.5,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_code_switch_type ON code_switch_examples(code_switch_type);
CREATE INDEX IF NOT EXISTS idx_code_switch_domain ON code_switch_examples(domain);

-- Metadata / versioning table
CREATE TABLE IF NOT EXISTS metadata (
  key TEXT PRIMARY KEY,
  value TEXT,
  description TEXT,
  updated_at TEXT DEFAULT (datetime('now'))
);

-- Insert initial metadata
INSERT OR IGNORE INTO metadata (key, value, description) VALUES
  ('schema_version', '1.1.0', 'Current database schema version with code-switching support'),
  ('created_at', datetime('now'), 'Database creation timestamp'),
  ('last_export_version', NULL, 'Last training export version'),
  ('corpus_count', '0', 'Total corpus entries'),
  ('glossary_count', '0', 'Total glossary entries'),
  ('code_switch_count', '0', 'Total code-switching examples');
