#!/usr/bin/env python3
"""
Generate seed corpus using NLLB base model

This creates a large initial corpus for your team to review, correct, and expand.
The base NLLB translations provide a starting point that's better than blank.

Strategy:
1. Use common medical/general English phrases
2. Translate with NLLB base model (no fine-tuning)
3. Mark as 'draft' status requiring human review
4. Export to CSV for team correction
5. Re-import corrected versions

Usage:
    python scripts/generate_seed_corpus.py --count 500 --domain medical
    python scripts/generate_seed_corpus.py --count 300 --domain general
"""

import sys
import csv
import argparse
from pathlib import Path
from typing import List, Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.translator import KalimaxTranslator


# Medical phrases (common patient-facing)
MEDICAL_PHRASES = [
    "The patient needs immediate medical attention",
    "Take this medication twice daily",
    "Do you have any allergies?",
    "Where does it hurt?",
    "How long have you had this pain?",
    "We need to run some tests",
    "Your blood pressure is high",
    "You have a fever",
    "Take this medicine with food",
    "Come back if symptoms worsen",
    "You need to see a specialist",
    "The emergency room is down the hall",
    "Please sit in the waiting room",
    "We will call you when ready",
    "Do you take any medications?",
    "Are you pregnant or breastfeeding?",
    "When was your last meal?",
    "Do you have chest pain?",
    "Can you breathe normally?",
    "We need to check your temperature",
    "Roll up your sleeve please",
    "This might hurt a little",
    "Try to relax",
    "Take a deep breath",
    "Hold still for a moment",
    "You can get dressed now",
    "Wait here for the doctor",
    "The doctor will be right with you",
    "Do you understand these instructions?",
    "Call us if you have questions",
    "Your appointment is next week",
    "Bring your insurance card",
    "Fill out this form please",
    "Sign here",
    "We accept cash or card",
    "Your medication is ready",
    "Take one pill every morning",
    "Do not drive after taking this",
    "Store in a cool dry place",
    "Keep out of reach of children",
    "Side effects may include nausea",
    "Stop taking if rash appears",
    "Drink plenty of water",
    "Get plenty of rest",
    "Avoid alcohol",
    "Come back in two weeks",
    "Your test results are normal",
    "We found an infection",
    "You need antibiotics",
    "This condition is treatable",
]

# General conversation phrases
GENERAL_PHRASES = [
    "Hello, how are you?",
    "Good morning",
    "Good afternoon",
    "Good evening",
    "Thank you",
    "You're welcome",
    "Please",
    "Excuse me",
    "I'm sorry",
    "I don't understand",
    "Can you help me?",
    "Where is the bathroom?",
    "How much does this cost?",
    "What time is it?",
    "I need help",
    "Call the police",
    "Call an ambulance",
    "Where do you live?",
    "What is your name?",
    "Nice to meet you",
    "See you later",
    "Goodbye",
    "Have a good day",
    "Take care",
    "Be careful",
    "I am hungry",
    "I am thirsty",
    "I am tired",
    "I am cold",
    "I am hot",
    "Can I have water?",
    "Where is the hospital?",
    "Where is the pharmacy?",
    "I feel sick",
    "I have a headache",
    "I have a toothache",
    "I have a stomachache",
    "I need a doctor",
    "Can you speak slower?",
    "Can you repeat that?",
    "I speak a little",
    "Do you speak English?",
    "What does this mean?",
    "How do you say this?",
    "Wait a moment",
    "Come here",
    "Go there",
    "Turn left",
    "Turn right",
]

# Public health phrases
PUBLIC_HEALTH_PHRASES = [
    "Wash your hands frequently",
    "Cover your mouth when coughing",
    "Stay home if you feel sick",
    "Wear a mask in crowded places",
    "Get vaccinated",
    "Drink clean water",
    "Cook food thoroughly",
    "Avoid mosquito bites",
    "Use insect repellent",
    "Sleep under a mosquito net",
    "Boil water before drinking",
    "Wash fruits and vegetables",
    "Keep food covered",
    "Dispose of trash properly",
    "Use the toilet, not outside",
    "Keep your home clean",
    "Protect yourself from the sun",
    "Get regular checkups",
    "Exercise regularly",
    "Eat healthy foods",
]


def generate_corpus(
    domain: str = "medical",
    count: int = 200,
    output_csv: str = "data/seed/generated_corpus.csv"
) -> int:
    """
    Generate seed corpus using NLLB base model
    
    Args:
        domain: Domain to generate (medical, general, public_health)
        count: Number of phrases to translate
        output_csv: Output CSV file path
    """
    
    # Select phrase list
    if domain == "medical":
        phrases = MEDICAL_PHRASES
    elif domain == "general":
        phrases = GENERAL_PHRASES
    elif domain == "public_health":
        phrases = PUBLIC_HEALTH_PHRASES
    else:
        phrases = MEDICAL_PHRASES + GENERAL_PHRASES
    
    # Limit to requested count
    phrases = phrases[:count]
    
    print(f"\n🤖 Generating {len(phrases)} {domain} translations...")
    print(f"📥 Loading NLLB model (this may take a while)...\n")
    
    # Initialize translator
    translator = KalimaxTranslator()
    
    # Prepare output
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for i, phrase in enumerate(phrases, 1):
        print(f"[{i}/{len(phrases)}] Translating: {phrase[:50]}...")
        
        try:
            result = translator.translate(
                text=phrase,
                source_lang="eng_Latn",
                target_lang="hat_Latn",
                audience="patient"
            )
            
            results.append({
                'src_text': phrase,
                'src_lang': 'eng_Latn',
                'tgt_text_literal': '',  # Leave blank for team to fill
                'tgt_text_localized': result.translation,
                'tgt_lang': 'hat_Latn',
                'domain': domain,
                'cultural_note': 'GENERATED: Needs human review and correction',
                'confidence': f"{result.confidence:.2f}",
                'curation_status': 'draft',
                'audience': 'patient'
            })
            
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            results.append({
                'src_text': phrase,
                'src_lang': 'eng_Latn',
                'tgt_text_literal': '',
                'tgt_text_localized': '[TRANSLATION_FAILED]',
                'tgt_lang': 'hat_Latn',
                'domain': domain,
                'cultural_note': f'ERROR: {str(e)}',
                'confidence': '0.0',
                'curation_status': 'draft',
                'audience': 'patient'
            })
    
    # Write CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✅ Generated {len(results)} translations")
    print(f"📁 Output: {output_path}")
    print(f"\n📝 Next steps:")
    print(f"1. Review and correct translations in: {output_path}")
    print(f"2. Add literal translations to 'tgt_text_literal' column")
    print(f"3. Fix any errors in 'tgt_text_localized' column")
    print(f"4. Add cultural notes where appropriate")
    print(f"5. Ingest corrected CSV:")
    print(f"   python src/data/ingest_sources.py {output_path} --type corpus")
    
    return len(results)


def main():
    parser = argparse.ArgumentParser(
        description="Generate seed corpus using NLLB base model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 200 medical phrases
  python scripts/generate_seed_corpus.py --domain medical --count 200
  
  # Generate 100 general phrases
  python scripts/generate_seed_corpus.py --domain general --count 100
  
  # Generate all available phrases
  python scripts/generate_seed_corpus.py --domain all --count 1000
        """
    )
    
    parser.add_argument(
        '--domain',
        choices=['medical', 'general', 'public_health', 'all'],
        default='medical',
        help='Domain to generate (default: medical)'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        default=200,
        help='Number of phrases to translate (default: 200)'
    )
    
    parser.add_argument(
        '--output',
        default='data/seed/generated_corpus.csv',
        help='Output CSV file (default: data/seed/generated_corpus.csv)'
    )
    
    args = parser.parse_args()
    
    try:
        count = generate_corpus(
            domain=args.domain,
            count=args.count,
            output_csv=args.output
        )
        
        print(f"\n🎉 Success! Generated {count} translations for review")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
