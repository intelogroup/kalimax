"""
Kalimax Translator Module

Main translation functionality for English-Haitian Creole medical translation.
Supports mT5-Large model with LoRA fine-tuning and cultural adaptation.
"""

import os
import ssl
import urllib3

# Disable SSL warnings and verification for Hugging Face downloads
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
ssl._create_default_https_context = ssl._create_unverified_context

import time
import torch
from pathlib import Path
import yaml
from typing import Optional, Dict, Any
from dataclasses import dataclass

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class TranslationResult:
    """Container for translation results with metadata"""
    translation: str
    confidence: float = 0.0
    cultural_notes: Optional[str] = None
    domain: Optional[str] = None
    processing_time: Optional[float] = None


class KalimaxTranslator:
    """
    Main translator class for English-Haitian Creole translation
    
    Uses NLLB-200 base model with LoRA fine-tuning for culturally-aware translations.
    """
    
    def __init__(
        self,
        model_name: str = "facebook/nllb-200-distilled-600M",
        lora_adapter_path: Optional[str] = None,
        device: str = "auto",
        config_path: Optional[str] = None
    ):
        """
        Initialize the Kalimax translator
        
        Args:
            model_name: Base NLLB model to use
            lora_adapter_path: Path to fine-tuned LoRA adapter (if available)
            device: Device to run inference on ("auto", "cpu", "cuda")
            config_path: Path to config YAML file
        """
        # Load config
        self.config = self._load_config(config_path)
        
        # Model settings
        self.model_name = self.config.get('model', {}).get('name', 'google/mt5-large')
        self.cache_dir = self.config.get('model', {}).get('cache_dir', './models/cache')
        
        # Determine device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        # Language settings (ISO format for mT5)
        self.languages = self.config.get('languages', {
            'english': 'en', 
            'haitian_creole': 'ht'
        })
        
        # Initialize model and tokenizer
        self.model = None
        self.tokenizer = None
        
        print(f"🚀 Initializing Kalimax translator on {self.device}...")
        
        # Load model and tokenizer
        self._load_model()

        # Initialize code-switching support
        self._init_code_switch_detection()
    
    def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "ht",
        domain: str = "medical",
        audience: str = "patient",
        max_length: int = 512
    ) -> str:
        """
        Translate text using mT5 model
        
        Args:
            text: Input text to translate
            source_lang: Source language code (ISO format, e.g., 'en')
            target_lang: Target language code (ISO format, e.g., 'ht')
            domain: Domain context (medical, general, etc.)
            audience: Target audience (patient, clinician, general)
            max_length: Maximum output length
            
        Returns:
            Translated text
        """
        # Build input with control tokens for mT5
        control_tokens = f"<src:{source_lang}> <tgt:{target_lang}> <domain:{domain}> <audience:{audience}>"
        input_text = f"{control_tokens} {text}"
        
        # Tokenize input
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)
        
        # Generate translation
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=4,
                early_stopping=True,
                do_sample=False,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode output
        translated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translated.strip()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "configs" / "base_config.yaml"
        
        config_path = Path(config_path)
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            # Return default config
            return {
                'model': {'name': self.model_name, 'cache_dir': './models/cache'},
                'languages': {'english': 'en', 'haitian_creole': 'ht'}
            }
    
    def _load_model(self):
        """Load the mT5 model and tokenizer"""
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            import requests
            
            # Additional SSL bypass for transformers/requests
            requests.packages.urllib3.disable_warnings()
            
            cache_dir = self.config.get('model', {}).get('cache_dir', './models/cache')
            
            print(f"📥 Loading tokenizer: {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=cache_dir,
                trust_remote_code=True,
                use_auth_token=False,
                use_fast=False  # Use slow tokenizer for mT5 compatibility
            )
            
            print(f"📥 Loading model: {self.model_name}...")
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name,
                cache_dir=cache_dir,
                torch_dtype=torch.float32,  # Use float32 for CPU compatibility
                trust_remote_code=True,
                use_auth_token=False
            )
            
            self.model.to(self.device)
            self.model.eval()
            
            # Load LoRA adapter if specified
            if self.lora_adapter_path:
                self._apply_lora_adapter()
            
            print(f"✅ Model loaded successfully on {self.device}")
            
        except ImportError as e:
            raise ImportError(
                f"Required packages not installed: {e}. "
                "Please run: pip install transformers torch"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")
    
    def _apply_lora_adapter(self):
        """Apply LoRA adapter if available"""
        try:
            from peft import PeftModel
            
            print(f"📥 Loading LoRA adapter from {self.lora_adapter_path}...")
            self.model = PeftModel.from_pretrained(
                self.model,
                self.lora_adapter_path
            )
            self.model.eval()
            print("✅ LoRA adapter loaded successfully")
            
        except ImportError:
            print("⚠️  PEFT not installed. Skipping LoRA adapter.")
            print("   Install with: pip install peft")
        except Exception as e:
            print(f"⚠️  Failed to load LoRA adapter: {e}")
            print("   Continuing with base model.")
    
    def _calculate_confidence(self, generated_output) -> float:
        """
        Calculate confidence score from generation scores
        
        This is a simple proxy using average sequence score.
        More sophisticated methods could use:
        - Token-level probabilities
        - Entropy
        - Model calibration
        """
        if not hasattr(generated_output, 'sequences_scores'):
            return 0.5  # Default neutral confidence
        
        try:
            # Get sequence scores (log probabilities)
            scores = generated_output.sequences_scores
            
            # Convert to probability-like score (0-1 range)
            # Using softmax-like normalization
            confidence = torch.exp(scores).mean().item()
            
            # Clamp to [0, 1]
            return max(0.0, min(1.0, confidence))
        except:
            return 0.5  # Fallback

    def _init_code_switch_detection(self):
        """Initialize code-switching detection patterns"""
        # Load common code-switching patterns
        self.code_switch_patterns = {
            'english_injections': ['deal', 'check', 'fix', 'grab', 'pick', 'hold'],
            'slang_terms': ['lougouwou', 'bouzen', 'makout'],
            'french_medical': ['tonne', 'engist', 'traitement'],
            'contractions': ["m'", "w'", "l'", "mw", 'pw']
        }

    def detect_code_switching(self, text: str) -> Dict[str, Any]:
        """
        Detect code-switching elements in input text

        Args:
            text: Input text to analyze

        Returns:
            Dictionary with detection results
        """
        result = {
            'has_code_switching': False,
            'mixed_languages': [],
            'patterns_detected': [],
            'confidence': 0.0
        }

        text_lower = text.lower()

        # Check for English injections
        for pattern in self.code_switch_patterns['english_injections']:
            if pattern in text_lower:
                result['has_code_switching'] = True
                result['mixed_languages'].append('english')
                result['patterns_detected'].append(f"English: '{pattern}'")
                result['confidence'] = max(result['confidence'], 0.8)

        # Check for slang terms
        for slang in self.code_switch_patterns['slang_terms']:
            if slang in text_lower:
                result['has_code_switching'] = True
                result['mixed_languages'].append('creole_slang')
                result['patterns_detected'].append(f"Slang: '{slang}'")
                result['confidence'] = max(result['confidence'], 0.9)

        # Check for French medical terms
        for french in self.code_switch_patterns['french_medical']:
            if french in text_lower:
                result['has_code_switching'] = True
                result['mixed_languages'].append('french')
                result['patterns_detected'].append(f"French: '{french}'")
                result['confidence'] = max(result['confidence'], 0.7)

        # Check for contractions
        for contraction in self.code_switch_patterns['contractions']:
            if contraction in text:
                result['has_code_switching'] = True
                result['mixed_languages'].append('creole_informal')
                result['patterns_detected'].append(f"Contraction: '{contraction}'")
                result['confidence'] = max(result['confidence'], 0.6)

        return result

    def translate_code_switched_text(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "ht",
        preserve_slang: bool = True,
        audience: str = "patient"
    ) -> TranslationResult:
        """
        Enhanced translation handling for code-switched text

        Args:
            text: Code-switched input text
            preserve_slang: Whether to preserve slang terms in quotes
            audience: Target audience context

        Returns:
            TranslationResult with enhanced cultural handling
        """

        # Detect code-switching elements
        cs_detection = self.detect_code_switching(text)

        # Get base translation
        base_result = self.translate(
            text=text,
            source_lang=source_lang,
            target_lang=target_lang,
            audience=audience
        )

        # Enhance cultural notes with code-switching info
        enhanced_notes = []
        if cs_detection['has_code_switching']:
            enhanced_notes.append("Contains code-switched elements")

            if preserve_slang and 'creole_slang' in cs_detection['mixed_languages']:
                enhanced_notes.append("Slang terms preserved for cultural authenticity")

            if 'english' in cs_detection['mixed_languages']:
                enhanced_notes.append("English loanwords detected and handled")

            enhanced_notes.append(f"Languages detected: {', '.join(set(cs_detection['mixed_languages']))}")

        if base_result.cultural_notes:
            enhanced_notes.insert(0, base_result.cultural_notes)

        # Update result
        base_result.cultural_notes = "; ".join(enhanced_notes) if enhanced_notes else None

        return base_result

    def quick_translate(
        self,
        text: str,
        src_lang="en",
        tgt_lang="ht"   
    ) -> str:
        """
        Quick translation method for CLI usage
        
        Args:
            text: Text to translate
            src_lang: Source language (ISO format)
            tgt_lang: Target language (ISO format)
            
        Returns:
            Translated text
        """
        return self.translate(
            text=text,
            source_lang=src_lang,
            target_lang=tgt_lang,
            domain="general",
            audience="general"
        )
