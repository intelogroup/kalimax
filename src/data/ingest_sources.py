#!/usr/bin/env python3
"""
Ingest data sources into Kalimax corpus database

Supports CSV imports for:
- Glossary (difficult dictionary)
- Corpus (parallel translations)
- Expressions (idioms)
- Profanity (harsh language)
- Normalization rules
"""

import sqlite3
import csv
import json
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))
from normalize_text import TextNormalizer


class CorpusIngester:
    """Ingest CSV data into SQLite corpus database"""
    
    def __init__(self, db_path: str = "data/kalimax_corpus.db"):
        """Initialize ingester with database connection"""
        project_root = Path(__file__).parent.parent.parent
        self.db_file = project_root / db_path
        
        if not self.db_file.exists():
            raise FileNotFoundError(
                f"Database not found: {self.db_file}\n"
                "Run 'python src/data/init_db.py' first."
            )
        
        self.conn = sqlite3.connect(self.db_file)
        self.normalizer = TextNormalizer(db_path=str(self.db_file))
        
        print(f"📂 Connected to database: {self.db_file}")
    
    def ingest_glossary_csv(self, csv_path: str, dataset_name: str = "seed") -> int:
        """
        Ingest glossary CSV
        
        Expected columns:
        - creole_canonical, english_equivalents (JSON list), domain,
          cultural_weight, preferred_for_patients, examples_good, notes
        """
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV not found: {csv_file}")
        
        cursor = self.conn.cursor()
        count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                entry_id = f"gloss_{uuid.uuid4().hex[:8]}"
                
                cursor.execute("""
                    INSERT INTO glossary (
                        id, creole_canonical, english_equivalents, aliases,
                        domain, cultural_weight, preferred_for_patients,
                        examples_bad, examples_good, notes, provenance, created_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry_id,
                    row.get('creole_canonical', ''),
                    row.get('english_equivalents', '[]'),
                    row.get('aliases', '[]'),
                    row.get('domain', 'general'),
                    row.get('cultural_weight', 'neutral'),
                    int(row.get('preferred_for_patients', '1')),
                    row.get('examples_bad', ''),
                    row.get('examples_good', ''),
                    row.get('notes', ''),
                    f"{dataset_name}:{csv_file.name}",
                    row.get('created_by', 'import')
                ))
                count += 1
        
        self.conn.commit()
        cursor.close()
        print(f"✅ Imported {count} glossary entries from {csv_file.name}")
        return count
    
    def ingest_corpus_csv(
        self,
        csv_path: str,
        dataset_name: str = "seed",
        dataset_version: str = "1.0"
    ) -> int:
        """
        Ingest corpus CSV
        
        Expected columns:
        - src_text, src_lang, tgt_text_literal, tgt_text_localized, tgt_lang,
          domain, cultural_note, contains_dosage
        """
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV not found: {csv_file}")
        
        cursor = self.conn.cursor()
        count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                entry_id = f"c_{uuid.uuid4().hex[:8]}"
                
                # Normalize texts
                src_normalized = self.normalizer.normalize(row.get('src_text', ''))
                tgt_lit_normalized = self.normalizer.normalize(row.get('tgt_text_literal', '')) if row.get('tgt_text_literal') else None
                tgt_loc_normalized = self.normalizer.normalize(row.get('tgt_text_localized', ''))
                
                # Detect dosage
                contains_dosage = int(
                    self.normalizer.detect_dosage_pattern(src_normalized) or
                    (tgt_loc_normalized and self.normalizer.detect_dosage_pattern(tgt_loc_normalized))
                )
                
                # Build context JSON
                context = {}
                if row.get('audience'):
                    context['audience'] = row['audience']
                if row.get('register'):
                    context['register'] = row['register']
                context_json = json.dumps(context) if context else None
                
                cursor.execute("""
                    INSERT INTO corpus (
                        id, src_text, src_lang, tgt_text_literal, tgt_text_localized, tgt_lang,
                        domain, is_idiom, contains_dosage, context, cultural_note,
                        provenance, confidence, dataset_name, dataset_version, curation_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry_id,
                    src_normalized,
                    row.get('src_lang', 'eng_Latn'),
                    tgt_lit_normalized,
                    tgt_loc_normalized,
                    row.get('tgt_lang', 'hat_Latn'),
                    row.get('domain', 'general'),
                    int(row.get('is_idiom', '0')),
                    contains_dosage,
                    context_json,
                    row.get('cultural_note', ''),
                    f"{dataset_name}:{csv_file.name}",
                    float(row.get('confidence', '0.8')),
                    dataset_name,
                    dataset_version,
                    row.get('curation_status', 'draft')
                ))
                count += 1
        
        self.conn.commit()
        cursor.close()
        print(f"✅ Imported {count} corpus entries from {csv_file.name}")
        return count
    
    def ingest_expressions_csv(self, csv_path: str) -> int:
        """
        Ingest expressions CSV
        
        Expected columns:
        - creole, literal_gloss_en, idiomatic_en, localized_ht,
          register, cultural_note
        """
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV not found: {csv_file}")
        
        cursor = self.conn.cursor()
        count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                entry_id = f"expr_{uuid.uuid4().hex[:8]}"
                
                cursor.execute("""
                    INSERT INTO expressions (
                        id, creole, literal_gloss_en, idiomatic_en, localized_ht,
                        register, region, cultural_note, provenance
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry_id,
                    row.get('creole', ''),
                    row.get('literal_gloss_en', ''),
                    row.get('idiomatic_en', ''),
                    row.get('localized_ht', ''),
                    row.get('register', 'neutral'),
                    row.get('region', ''),
                    row.get('cultural_note', ''),
                    f"import:{csv_file.name}"
                ))
                count += 1
        
        self.conn.commit()
        cursor.close()
        print(f"✅ Imported {count} expression entries from {csv_file.name}")
        return count
    
    def ingest_profanity_csv(self, csv_path: str) -> int:
        """
        Ingest profanity CSV

        Expected columns:
        - term_creole, term_english, severity, category,
          safe_alternatives_ht (JSON), safe_alternatives_en (JSON),
          cultural_note
        """
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV not found: {csv_file}")
        
        cursor = self.conn.cursor()
        count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            allowed_categories = {'profanity','slur','sexual','violence','religious','body','illness','other'}
            severity_map = {'mild':'mild','moderate':'moderate','strong':'severe','severe':'severe','extreme':'extreme'}
            
            for row in reader:
                entry_id = f"prof_{uuid.uuid4().hex[:8]}"
                # Normalize category and severity to match schema constraints
                category = (row.get('category', 'profanity') or 'profanity').lower()
                if category not in allowed_categories:
                    category = 'other'
                severity_raw = (row.get('severity', 'moderate') or 'moderate').lower()
                severity = severity_map.get(severity_raw, 'moderate')
                
                # Ensure safe alternatives are JSON lists
                ht_alt = row.get('safe_alternatives_ht', '') or ''
                en_alt = row.get('safe_alternatives_en', '') or ''
                if not ht_alt.strip().startswith('['):
                    ht_alt = json.dumps([s.strip() for s in ht_alt.split(',') if s.strip()])
                if not en_alt.strip().startswith('['):
                    en_alt = json.dumps([s.strip() for s in en_alt.split(',') if s.strip()])
                
                cursor.execute("""
                    INSERT INTO profanity (
                        id, term_creole, term_english, severity, category,
                        safe_alternatives_ht, safe_alternatives_en, cultural_note,
                        should_flag, should_block, provenance
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry_id,
                    row.get('term_creole', ''),
                    row.get('term_english', ''),
                    severity,
                    category,
                    ht_alt or '[]',
                    en_alt or '[]',
                    row.get('cultural_note', ''),
                    int(row.get('should_flag', '1') or 1),
                    int(row.get('should_block', '0') or 0),
                    f"import:{csv_file.name}"
                ))
                count += 1
        
        self.conn.commit()
        cursor.close()
        print(f"✅ Imported {count} profanity entries from {csv_file.name}")
        return count

    def ingest_normalization_csv(self, csv_path: str, dataset_name: str = "seed") -> int:
        """
        Ingest normalization rules CSV

        Expected columns:
        - variant, canonical, english_equivalent, register, notes
        """
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV not found: {csv_file}")
        cursor = self.conn.cursor()
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entry_id = f"norm_{uuid.uuid4().hex[:8]}"
                cursor.execute("""
                    INSERT OR IGNORE INTO normalization_rules (
                        id, variant, canonical, english_equivalent, register, provenance
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entry_id,
                    row.get('variant', ''),
                    row.get('canonical', ''),
                    row.get('english_equivalent', ''),
                    row.get('register', 'general'),
                    f"{dataset_name}:{csv_file.name}"
                ))
                count += 1
        self.conn.commit()
        cursor.close()
        print(f"✅ Imported {count} normalization rules from {csv_file.name}")
        return count

    def ingest_challenge_csv(self, csv_path: str, dataset_name: str = "seed") -> int:
        """
        Ingest challenge set CSV.

        Expected columns (from generator):
        - id, category, src_en, src_ht, phenomenon, expected_behavior, notes
        Mapped to schema:
        - src_text=src_en, src_lang=eng_Latn, tgt_text=src_ht, tgt_lang=hat_Latn,
          challenge_type=category, expected_behavior, evaluation_notes=notes,
          provenance, never_for_training=1
        """
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV not found: {csv_file}")
        cursor = self.conn.cursor()
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            cat_map = {
                'idiom': 'idioms',
                'dosage': 'high_risk',
                'negation': 'cultural',
                'ambiguity': 'cultural',
                'numbers': 'cultural',
                'polysemy': 'cultural',
            }
            for row in reader:
                entry_id = f"chal_{uuid.uuid4().hex[:8]}"
                raw_cat = (row.get('category', 'cultural') or 'cultural').lower()
                challenge_type = cat_map.get(raw_cat, 'cultural')
                cursor.execute("""
                    INSERT INTO challenge (
                        id, src_text, src_lang, tgt_text, tgt_lang, challenge_type,
                        domain, difficulty, expected_behavior, evaluation_notes,
                        provenance, never_for_training
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry_id,
                    row.get('src_en', ''),
                    'eng_Latn',
                    row.get('src_ht', ''),
                    'hat_Latn',
                    challenge_type,
                    None,
                    'medium',
                    row.get('expected_behavior', ''),
                    row.get('notes', ''),
                    f"{dataset_name}:{csv_file.name}",
                    1
                ))
                count += 1
        self.conn.commit()
        cursor.close()
        print(f"✅ Imported {count} challenge items from {csv_file.name}")
        return count

    def ingest_monolingual_ht_csv(self, csv_path: str, dataset_name: str = "seed") -> int:
        """
        Ingest monolingual Haitian Creole CSV.

        Expected columns: id, text, domain, topic, complexity
        """
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV not found: {csv_file}")
        cursor = self.conn.cursor()
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entry_id = f"mht_{uuid.uuid4().hex[:8]}"
                cursor.execute("""
                    INSERT INTO monolingual_ht (
                        id, text, domain, provenance, dataset_name
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    entry_id,
                    row.get('text', ''),
                    row.get('domain', None),
                    f"{dataset_name}:{csv_file.name}",
                    dataset_name
                ))
                count += 1
        self.conn.commit()
        cursor.close()
        print(f"✅ Imported {count} monolingual HT rows from {csv_file.name}")
        return count

    def ingest_haitian_patterns_csv(self, csv_path: str, dataset_name: str = "seed") -> int:
        """
        Ingest Haitian Creole language patterns CSV.

        Expected columns: pattern_type, haitian_example, english_gloss, 
                         grammatical_description, linguistic_notes, frequency, difficulty, domain
        """
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV not found: {csv_file}")
        cursor = self.conn.cursor()
        count = 0
        
        allowed_patterns = {'grammar','syntax','phonology','morphology','tense','aspect',
                           'verb_conjugation','noun_phrase','question_formation','negation',
                           'serial_verbs','creole_features'}
        allowed_freq = {'very_common','common','uncommon','rare'}
        allowed_diff = {'basic','intermediate','advanced'}
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entry_id = f"htp_{uuid.uuid4().hex[:8]}"
                
                # Validate pattern_type
                pattern_type = (row.get('pattern_type', 'grammar') or 'grammar').lower()
                if pattern_type not in allowed_patterns:
                    pattern_type = 'grammar'
                
                # Validate frequency and difficulty
                freq = (row.get('frequency', 'common') or 'common').lower()
                if freq not in allowed_freq:
                    freq = 'common'
                    
                diff = (row.get('difficulty', 'basic') or 'basic').lower()
                if diff not in allowed_diff:
                    diff = 'basic'
                
                cursor.execute("""
                    INSERT INTO haitian_creole_patterns (
                        id, pattern_type, haitian_example, english_gloss, 
                        grammatical_description, linguistic_notes, frequency, 
                        difficulty, domain, provenance, dataset_name
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry_id,
                    pattern_type,
                    row.get('haitian_example', ''),
                    row.get('english_gloss', ''),
                    row.get('grammatical_description', ''),
                    row.get('linguistic_notes', ''),
                    freq,
                    diff,
                    row.get('domain', None),
                    f"{dataset_name}:{csv_file.name}",
                    dataset_name
                ))
                count += 1
        self.conn.commit()
        cursor.close()
        print(f"✅ Imported {count} Haitian Creole pattern rows from {csv_file.name}")
        return count
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    """CLI for ingestion"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest CSV data into Kalimax corpus")
    parser.add_argument('csv_file', help='CSV file to ingest')
    parser.add_argument('--type', choices=['glossary', 'corpus', 'expressions', 'profanity', 'normalization', 'challenge', 'mono_ht', 'ht_patterns'],
                       required=True, help='Type of data')
    parser.add_argument('--dataset', default='seed', help='Dataset name (default: seed)')
    parser.add_argument('--version', default='1.0', help='Dataset version (default: 1.0)')
    
    args = parser.parse_args()
    
    try:
        ingester = CorpusIngester()
        
        if args.type == 'glossary':
            count = ingester.ingest_glossary_csv(args.csv_file, args.dataset)
        elif args.type == 'corpus':
            count = ingester.ingest_corpus_csv(args.csv_file, args.dataset, args.version)
        elif args.type == 'expressions':
            count = ingester.ingest_expressions_csv(args.csv_file)
        elif args.type == 'profanity':
            count = ingester.ingest_profanity_csv(args.csv_file)
        elif args.type == 'normalization':
            count = ingester.ingest_normalization_csv(args.csv_file, args.dataset)
        elif args.type == 'challenge':
            count = ingester.ingest_challenge_csv(args.csv_file, args.dataset)
        elif args.type == 'mono_ht':
            count = ingester.ingest_monolingual_ht_csv(args.csv_file, args.dataset)
        elif args.type == 'ht_patterns':
            count = ingester.ingest_haitian_patterns_csv(args.csv_file, args.dataset)
        
        ingester.close()
        
        print(f"\n🎉 Successfully ingested {count} entries!")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
