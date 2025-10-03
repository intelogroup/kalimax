#!/usr/bin/env python3
"""
Generate code-switching training examples for Kalimax

Creates examples of Haitian Creole mixed with English/French/Spanish,
with annotations for language spans and proper translations.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any


def create_code_switch_examples():
    """Create initial code-switching training examples"""

    examples = [
        # User's example with "lougouwou"
        {
            'id': 'code_switch_001',
            'src_text_mixed': "Mwe se yon mekanisyen mw pa deal ak avek malfekte lougouwou kap volè kob moun ti area sa la.",
            'src_lang_primary': 'hat_Latn',
            'tgt_lang_primary': 'eng_Latn',
            'clean_translation': "I'm a mechanic. I don't deal with the bad guys who steal people's money in this neighborhood.",
            'annotated_translation': "I'm a mechanic. I don't deal with the bad guys (lougouwou) who steal people's money in this neighborhood.",
            'src_lang_tags': json.dumps([
                {'start': 0, 'end': 59, 'lang': 'hat_Latn'},
                {'start': 23, 'end': 27, 'lang': 'eng_Latn'},  # "deal"
                {'start': 50, 'end': 59, 'lang': 'hat_Latn'}   # "lougouwou"
            ]),
            'tgt_lang_tags': json.dumps([
                {'start': 14, 'end': 18, 'lang': 'eng_Latn'},   # "deal"
                {'start': 45, 'end': 55, 'lang': 'eng_Latn'}    # "(lougouwou)"
            ]),
            'code_switch_type': 'english_injection',
            'domain': 'general',
            'context': 'Informal conversation, urban setting, describing social disapproval',
            'provenance': 'user_contributed_example',
            'confidence': 0.95
        },

        # English slang in medical context
        {
            'id': 'code_switch_002',
            'src_text_mixed': "Li bezwen tonne maladi a engist Ogmante tansyon li yon ti kras.",
            'src_lang_primary': 'hat_Latn',
            'tgt_lang_primary': 'eng_Latn',
            'clean_translation': "They need to treat the chest infection. Their blood pressure has risen a bit.",
            'annotated_translation': "They need to treat the chest infection. Their blood pressure has risen a bit.",
            'src_lang_tags': json.dumps([
                {'start': 0, 'end': 11, 'lang': 'hat_Latn'},
                {'start': 12, 'end': 17, 'lang': 'fra_Latn'},  # "tonne" (French)
                {'start': 18, 'end': 35, 'lang': 'hat_Latn'},
                {'start': 36, 'end': 43, 'lang': 'eng_Latn'}   # "engist" (angoisse - French)
            ]),
            'tgt_lang_tags': json.dumps([
                {'start': 0, 'end': 49, 'lang': 'eng_Latn'}
            ]),
            'code_switch_type': 'french_injection',
            'domain': 'medical',
            'context': 'Rural clinic, elderly patient, discussing infection treatment',
            'provenance': 'synthetic_medical_example',
            'confidence': 0.85
        },

        # Check/check it
        {
            'id': 'code_switch_003',
            'src_text_mixed': "Doktè pa bliye check li apre midi a.",
            'src_lang_primary': 'hat_Latn',
            'tgt_lang_primary': 'eng_Latn',
            'clean_translation': "Doctor, don't forget to check on them this afternoon.",
            'annotated_translation': "Doctor, don't forget to check (examine) them this afternoon.",
            'src_lang_tags': json.dumps([
                {'start': 0, 'end': 16, 'lang': 'hat_Latn'},
                {'start': 17, 'end': 22, 'lang': 'eng_Latn'}   # "check"
            ]),
            'tgt_lang_tags': json.dumps([
                {'start': 20, 'end': 25, 'lang': 'eng_Latn'},  # "check"
                {'start': 26, 'end': 35, 'lang': 'eng_Latn'}   # "(examine)"
            ]),
            'code_switch_type': 'english_injection',
            'domain': 'medical',
            'context': 'Hospital setting, nurse to doctor reminder',
            'provenance': 'synthetic_medical_example',
            'confidence': 0.9
        },

        # Grab/pick up medications
        {
            'id': 'code_switch_004',
            'src_text_mixed': "Tanpri ale grab renmèd yo nan famasi an pou ou rive lakay ou.",
            'src_lang_primary': 'hat_Latn',
            'tgt_lang_primary': 'eng_Latn',
            'clean_translation': "Please go pick up your medications from the pharmacy before you go home.",
            'annotated_translation': "Please go pick up (get/collect) your medications from the pharmacy before you go home.",
            'src_lang_tags': json.dumps([
                {'start': 0, 'end': 15, 'lang': 'hat_Latn'},
                {'start': 16, 'end': 20, 'lang': 'eng_Latn'},  # "grab"
                {'start': 21, 'end': 43, 'lang': 'hat_Latn'}
            ]),
            'tgt_lang_tags': json.dumps([
                {'start': 12, 'end': 17, 'lang': 'eng_Latn'},  # "pick"
                {'start': 18, 'end': 35, 'lang': 'eng_Latn'}   # "(get/collect)"
            ]),
            'code_switch_type': 'english_injection',
            'domain': 'medical',
            'context': 'Pharmacy discharge, medication pickup instructions',
            'provenance': 'synthetic_pharmacy_example',
            'confidence': 0.88
        },

        # Fix/repair wound dressing
        {
            'id': 'code_switch_005',
            'src_text_mixed': "Nou gen pou fix pansman an anvan ou pati.",
            'src_lang_primary': 'hat_Latn',
            'tgt_lang_primary': 'eng_Latn',
            'clean_translation': "We need to change the dressing before you leave.",
            'annotated_translation': "We need to change (fix/repair) the dressing before you leave.",
            'src_lang_tags': json.dumps([
                {'start': 0, 'end': 14, 'lang': 'hat_Latn'},
                {'start': 15, 'end': 19, 'lang': 'eng_Latn'},  # "fix"
                {'start': 20, 'end': 36, 'lang': 'hat_Latn'}
            ]),
            'tgt_lang_tags': json.dumps([
                {'start': 12, 'end': 19, 'lang': 'eng_Latn'},  # "change"
                {'start': 20, 'end': 37, 'lang': 'eng_Latn'}   # "(fix/repair)"
            ]),
            'code_switch_type': 'english_injection',
            'domain': 'medical',
            'context': 'Clinic, wound care, patient discharge',
            'provenance': 'synthetic_wound_care_example',
            'confidence': 0.87
        },

        # Mixed with Spanish (common in Haitian communities)
        {
            'id': 'code_switch_006',
            'src_text_mixed': "Mwen pa konnen but if si ou pa pran medikaman yo, ou ap malad.",
            'src_lang_primary': 'hat_Latn',
            'tgt_lang_primary': 'eng_Latn',
            'clean_translation': "I don't know but if you don't take your medications, you will get sick.",
            'annotated_translation': "I don't know but if you don't take your medications, you will get sick.",
            'src_lang_tags': json.dumps([
                {'start': 0, 'end': 14, 'lang': 'hat_Latn'},
                {'start': 15, 'end': 22, 'lang': 'eng_Latn'},  # "but if"
                {'start': 23, 'end': 25, 'lang': 'spa_Latn'},  # "si"
                {'start': 26, 'end': 58, 'lang': 'hat_Latn'}
            ]),
            'tgt_lang_tags': json.dumps([
                {'start': 0, 'end': 60, 'lang': 'eng_Latn'}
            ]),
            'code_switch_type': 'mixed_systemic',
            'domain': 'medical',
            'context': 'Community health worker, medication adherence conversation',
            'provenance': 'synthetic_multilingual_example',
            'confidence': 0.82
        },

        # Local slang terms (beyond lougouwou)
        {
            'id': 'code_switch_007',
            'src_text_mixed': "Bouzen yo pa mache byen nan mache sa.",
            'src_lang_primary': 'hat_Latn',
            'tgt_lang_primary': 'eng_Latn',
            'clean_translation': "The women don't walk well in that market.",
            'annotated_translation': "The women (bouzen = women/girls) don't walk well in that market.",
            'src_lang_tags': json.dumps([
                {'start': 0, 'end': 8, 'lang': 'hat_Latn'},
                {'start': 0, 'end': 6, 'lang': 'hat_Latn', 'slang': True},  # "bouzen"
                {'start': 7, 'end': 28, 'lang': 'hat_Latn'}
            ]),
            'tgt_lang_tags': json.dumps([
                {'start': 4, 'end': 9, 'lang': 'eng_Latn'},
                {'start': 10, 'end': 33, 'lang': 'eng_Latn'},  # "(bouzen = women/girls)"
                {'start': 34, 'end': 54, 'lang': 'eng_Latn'}
            ]),
            'code_switch_type': 'slang_borrowing',
            'domain': 'general',
            'context': 'Informal conversation, describing people',
            'provenance': 'synthetic_slang_example',
            'confidence': 0.8
        }
    ]

    return examples


def insert_code_switch_examples(db_path: str):
    """Insert code-switching examples into database"""

    examples = create_code_switch_examples()

    # Ensure database directory exists
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Insert examples
        for example in examples:
            cursor.execute("""
                INSERT OR REPLACE INTO code_switch_examples (
                    id, src_text_mixed, src_lang_primary, tgt_lang_primary,
                    clean_translation, annotated_translation, src_lang_tags,
                    tgt_lang_tags, code_switch_type, domain, context,
                    provenance, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                example['id'], example['src_text_mixed'], example['src_lang_primary'],
                example['tgt_lang_primary'], example['clean_translation'],
                example['annotated_translation'], example['src_lang_tags'],
                example['tgt_lang_tags'], example['code_switch_type'],
                example['domain'], example['context'], example['provenance'],
                example['confidence']
            ))

        # Update metadata
        cursor.execute("""
            INSERT OR REPLACE INTO metadata (key, value, description, updated_at)
            VALUES ('code_switch_count', ?, 'Total code-switching examples', datetime('now'))
        """, (len(examples),))

        conn.commit()
        print("8"✅ Added {len(examples)} code-switching training examples"
    except sqlite3.Error as e:
        print(f"❌ Failed to insert examples: {e}")
        conn.rollback()

    finally:
        conn.close()


def main():
    """Main execution function"""

    # Database paths
    primary_db = Path("data/kalimax_corpus.db")
    seed_db = Path("data/kalimax_ht_seed.db")

    print("🗣️ Generating Code-Switching Training Examples")
    print("=" * 50)

    # Create seed database if it doesn't exist
    if not seed_db.exists():
        print("📁 Creating seed database...")
        seed_db.parent.mkdir(parents=True, exist_ok=True)

    # Insert into seed database first (for development)
    print("💾 Inserting examples into seed database...")
    insert_code_switch_examples(str(seed_db))

    # Also insert into primary database if it exists
    if primary_db.exists():
        print("💾 Also inserting into primary corpus database...")
        insert_code_switch_examples(str(primary_db))

    print("\n✅ Code-switching examples generated successfully!")
    print("\nExamples include:")
    print("• 'Mwe se yon mekanisyen mw pa deal ak avek malfekte lougouwou...'")
    print("• Medical contexts with English injections: 'check', 'fix', 'grab'")
    print("• Multi-language mixing: Haitian + English + French/Spanish")
    print("• Cultural slang with proper annotations")


if __name__ == "__main__":
    main()
