#!/usr/bin/env python3
"""
Command-line interface for Kalimax translation

Usage:
    python -m src.translate_cli "Hello, how are you?" --tgt ht
python -m src.translate_cli "Bonjou" --src ht --tgt en
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.translator import KalimaxTranslator


def main():
    parser = argparse.ArgumentParser(
        description="Kalimax: Culturally-aware Haitian Creole translation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # English to Haitian Creole
  python -m src.translate_cli "The patient needs medical attention"
  
  # Haitian Creole to English
  python -m src.translate_cli "Malad la bezwen èd medikal" --src ht --tgt en
  
  # Specify audience
  python -m src.translate_cli "Take this medication" --audience patient
  
  # Use custom model
  python -m src.translate_cli "Hello" --model facebook/nllb-200-1.3B
        """
    )
    
    parser.add_argument(
        'text',
        type=str,
        help='Text to translate'
    )
    
    parser.add_argument(
        '--src', '--source',
        dest='source_lang',
        default='en',
        help='Source language code (ISO format, default: en)'
    )
    
    parser.add_argument(
        '--tgt', '--target',
        dest='target_lang',
        default='ht',
        help='Target language code (ISO format, default: ht)'
    )
    
    parser.add_argument(
        '--audience',
        choices=['patient', 'clinician', 'general'],
        default='patient',
        help='Target audience (default: patient)'
    )
    
    parser.add_argument(
        '--model',
        default='facebook/nllb-200-distilled-600M',
        help='Model name or path (default: facebook/nllb-200-distilled-600M)'
    )
    
    parser.add_argument(
        '--lora',
        dest='lora_adapter',
        help='Path to LoRA adapter (optional)'
    )
    
    parser.add_argument(
        '--beams',
        type=int,
        default=5,
        help='Number of beams for beam search (default: 5)'
    )
    
    parser.add_argument(
        '--max-length',
        type=int,
        default=512,
        help='Maximum output length (default: 512)'
    )
    
    parser.add_argument(
        '--device',
        choices=['auto', 'cpu', 'cuda'],
        default='auto',
        help='Device to use (default: auto)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output with metadata'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize translator
        print(f"\n🌐 Kalimax Translator")
        print("=" * 50)
        
        translator = KalimaxTranslator(
            model_name=args.model,
            lora_adapter_path=args.lora_adapter,
            device=args.device
        )
        
        # Translate
        print(f"\n📝 Input ({args.source_lang}):")
        print(f"   {args.text}")
        print()
        
        result = translator.translate(
            text=args.text,
            source_lang=args.source_lang,
            target_lang=args.target_lang,
            max_length=args.max_length,
            num_beams=args.beams,
            audience=args.audience
        )
        
        # Output
        print(f"✨ Translation ({args.target_lang}):")
        print(f"   {result.translation}")
        
        if args.verbose:
            print(f"\n📊 Metadata:")
            print(f"   Confidence:      {result.confidence:.2%}")
            print(f"   Processing time: {result.processing_time:.3f}s")
            if result.domain:
                print(f"   Domain:          {result.domain}")
            if result.cultural_notes:
                print(f"   Cultural notes:  {result.cultural_notes}")
        
        print()
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Translation cancelled by user")
        return 130
    
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
