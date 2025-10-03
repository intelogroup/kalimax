#!/usr/bin/env python3
"""
Generate normalization rules for Kalimax

Creates rules for contractions, slang, code-switched terms, and variants.
"""

import sqlite3
from pathlib import Path


def create_normalization_rules():
    """Create normalization rules for Creole slang and code-switching"""

    rules = [
        # Code-switching English injections (most common)
        {
            'id': 'norm_cs_001',
            'variant': 'deal',
            'canonical': 'fè kontra',
            'english_equivalent': 'associate',
            'register': 'spoken',
            'region': 'general',
            'examples': '["pw pa deal ak mwen", "li renmen deal ak move moun"]',
            'code_switch_type': 'english_to_creole',
            'language_origin': 'english',
            'mixed_context_notes': 'Common in informal speech, means to associate or deal with someone/something'
        },
        {
            'id': 'norm_cs_002',
            'variant': 'check',
            'canonical': 'tcheke',
            'english_equivalent': 'examine/check',
            'register': 'general',
            'region': 'general',
            'examples': '["doktè check li", "check si li move"]',
            'code_switch_type': 'english_to_creole',
            'language_origin': 'english',
            'mixed_context_notes': 'Medical/industrial term, widely adopted in Creole'
        },
        {
            'id': 'norm_cs_003',
            'variant': 'fix',
            'canonical': 'ranje',
            'english_equivalent': 'repair',
            'register': 'general',
            'region': 'general',
            'examples': '["fix machin nan", "nou fix pwoblèm nan"]',
            'code_switch_type': 'english_to_creole',
            'language_origin': 'english',
            'mixed_context_notes': 'Technical/repair contexts, gradually being replaced by "ranje"'
        },
        {
            'id': 'norm_cs_004',
            'variant': 'grab',
            'canonical': 'pran',
            'english_equivalent': 'take/get',
            'register': 'informal',
            'region': 'general',
            'examples': '["grab bagay la", "grab renmèd ou"]',
            'code_switch_type': 'english_to_creole',
            'language_origin': 'english',
            'mixed_context_notes': 'Casual speech, keep informal register'
        },

        # Slang terms (lougouwou and others)
        {
            'id': 'norm_slang_001',
            'variant': 'lougouwou',
            'canonical': 'vòlè',
            'english_equivalent': 'thug/criminal',
            'register': 'slang',
            'region': 'urban',
            'examples': '["lougouwou yo", "pa asosye ak lougouwou"]',
            'code_switch_type': 'slang_borrowing',
            'language_origin': 'creole_slang',
            'mixed_context_notes': 'Regional cowork/thug term, cultural flavor should be preserved in quotes when translating'
        },
        {
            'id': 'norm_slang_002',
            'variant': 'bouzen',
            'canonical': 'fi',
            'english_equivalent': 'girl/woman',
            'register': 'slang',
            'region': 'general',
            'examples': '["bouzen yo bei", "li se yon bouzen"]',
            'code_switch_type': 'slang_borrowing',
            'language_origin': 'creole_slang',
            'mixed_context_notes': 'Informal address for girls/women, may be inappropriate in formal contexts'
        },
        {
            'id': 'norm_slang_003',
            'variant': 'makout',
            'canonical': 'diktatè',
            'english_equivalent': 'dictator',
            'register': 'slang',
            'region': 'political',
            'examples': '["gouvènman makout", "li makout"]',
            'code_switch_type': 'slang_borrowing',
            'language_origin': 'creole_slang',
            'mixed_context_notes': 'Political slang for Duvalier regime, historical context'
        },

        # French borrowings common in medical contexts
        {
            'id': 'norm_french_001',
            'variant': 'tonne',
            'canonical': 'trete',
            'english_equivalent': 'treat',
            'register': 'general',
            'region': 'medical',
            'examples': '["tonne maladi", "doktè tonne li"]',
            'code_switch_type': 'creole_to_english',
            'language_origin': 'french',
            'mixed_context_notes': 'Medical context, related to traitement(treatment)'
        },
        {
            'id': 'norm_french_002',
            'variant': 'engist',
            'canonical': 'anxiety/anxiety',
            'english_equivalent': 'anxiety',
            'register': 'general',
            'region': 'medical',
            'examples': '["engist li", "li gen engist"]',
            'code_switch_type': 'creole_to_english',
            'language_origin': 'french',
            'mixed_context_notes': 'From angoisse, psychiatric/psychological term'
        },

        # Contraction variants (existing plus new)
        {
            'id': 'norm_contraction_001',
            'variant': "m'",
            'canonical': 'mwen',
            'english_equivalent': 'I/me',
            'register': 'spoken',
            'region': 'general',
            'examples': '["m\' bezwen èd", "m\' pa konnen"]',
            'code_switch_type': None,
            'language_origin': 'creole',
            'mixed_context_notes': 'Apostrophe contraction common in informal writing'
        },
        {
            'id': 'norm_contraction_002',
            'variant': "w'",
            'canonical': 'ou',
            'english_equivalent': 'you',
            'register': 'spoken',
            'region': 'general',
            'examples': '["w\' ap fè sa", "w\' di m\'"]',
            'code_switch_type': None,
            'language_origin': 'creole',
            'mixed_context_notes': 'You familiar form contraction'
        },
        {
            'id': 'norm_contraction_003',
            'variant': "l'",
            'canonical': 'li',
            'english_equivalent': 'he/she/it',
            'register': 'spoken',
            'region': 'general',
            'examples': '["l\' ap vini", "l\' gen pwoblèm"]',
            'code_switch_type': None,
            'language_origin': 'creole',
            'mixed_context_notes': 'Third person singular contraction'
        },
        {
            'id': 'norm_contraction_004',
            'variant': 'mw',
            'canonical': 'mwen',
            'english_equivalent': 'I/me',
            'register': 'chat',
            'region': 'general',
            'examples': '["mw pa deal", "mw bezwen"]',
            'code_switch_type': None,
            'language_origin': 'creole',
            'mixed_context_notes': 'SMS/informal abbreviation, user example contains this'
        }
    ]

    return rules


def insert_normalization_rules(db_path: str):
    """Insert normalization rules into database"""

    rules = create_normalization_rules()

    # Ensure database directory exists
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Insert rules
        for rule in rules:
            cursor.execute("""
                INSERT OR REPLACE INTO normalization_rules (
                    id, variant, canonical, english_equivalent, register,
                    region, examples, code_switch_type, language_origin,
                    mixed_context_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rule['id'], rule['variant'], rule['canonical'],
                rule['english_equivalent'], rule['register'], rule['region'],
                rule['examples'], rule['code_switch_type'],
                rule['language_origin'], rule['mixed_context_notes']
            ))

        conn.commit()
        print("2"✅ Added {len(rules)} normalization rules"
    except sqlite3.Error as e:
        print(f"❌ Failed to insert rules: {e}")
        conn.rollback()

    finally:
        conn.close()


def main():
    """Main execution function"""

    # Database paths
    primary_db = Path("data/kalimax_corpus.db")
    seed_db = Path("data/kalimax_ht_seed.db")

    print("📝 Generating Normalization Rules")
    print("=" * 40)

    # Insert into seed database first (for development)
    print("💾 Inserting into seed database...")
    insert_normalization_rules(str(seed_db))

    # Also insert into primary database if it exists
    if primary_db.exists():
        print("💾 Also inserting into primary corpus database...")
        insert_normalization_rules(str(primary_db))

    print("\n✅ Normalization rules added successfully!")
    print("\nKey additions:")
    print("• Code-switching: 'deal', 'check', 'fix', 'grab'")
    print("• Slang preservation: 'lougouwou', 'bouzen', 'makout'")
    print("• French medical terms: 'tonne', 'engist'")
    print("• Contractions: 'mw', 'm'', 'w'', 'l''")


if __name__ == "__main__":
    main()
