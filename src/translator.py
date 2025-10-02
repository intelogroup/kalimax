"""

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
        self.model_name = model_name
        self.lora_adapter_path = lora_adapter_path
        self.model = None
        self.tokenizer = None
        
        # Load config
        self.config = self._load_config(config_path)
        
        # Determine device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        print(f"🚀 Initializing Kalimax translator on {self.device}...")
        
        # Load model and tokenizer
        self._load_model()
    
    def translate(
        self,
        text: str,
        source_lang: str = "eng_Latn",
        target_lang: str = "hat_Latn",
        max_length: int = 512,
        num_beams: int = 5,
        audience: str = "patient"
    ) -> TranslationResult:
        """
        Translate text from source to target language
        
        Args:
            text: Text to translate
            source_lang: Source language code (NLLB format)
            target_lang: Target language code (NLLB format)
            max_length: Maximum length for generated translation
            num_beams: Number of beams for beam search
            audience: Target audience (patient|clinician|general)
            
        Returns:
            TranslationResult containing translation and metadata
        """
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model not loaded. Call _load_model() first.")
        
        start_time = time.time()
        
        # Set source language for tokenizer
        self.tokenizer.src_lang = source_lang
        
        # Tokenize input
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            padding=True, 
            truncation=True,
            max_length=max_length
        ).to(self.device)
        
        # Get target language token ID for forced BOS
        forced_bos_token_id = self.tokenizer.lang_code_to_id.get(
            target_lang,
            self.tokenizer.lang_code_to_id["hat_Latn"]  # Fallback to Haitian Creole
        )
        
        # Generate translation
        with torch.no_grad():
            generated_tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                max_length=max_length,
                num_beams=num_beams,
                early_stopping=True,
                return_dict_in_generate=True,
                output_scores=True
            )
        
        # Decode translation
        translation = self.tokenizer.batch_decode(
            generated_tokens.sequences, 
            skip_special_tokens=True
        )[0]
        
        # Calculate confidence (average log probability)
        # This is a proxy; more sophisticated methods exist
        confidence = self._calculate_confidence(generated_tokens)
        
        processing_time = time.time() - start_time
        
        # Add cultural notes if medical domain
        cultural_notes = None
        if "medical" in text.lower() or audience == "patient":
            cultural_notes = "Patient-facing medical translation"
        
        return TranslationResult(
            translation=translation,
            confidence=confidence,
            cultural_notes=cultural_notes,
            domain="medical" if audience == "patient" else "general",
            processing_time=processing_time
        )
    
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
                'languages': {'english': 'eng_Latn', 'haitian_creole': 'hat_Latn'}
            }
    
    def _load_model(self):
        """Load the NLLB model and tokenizer"""
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            
            cache_dir = self.config.get('model', {}).get('cache_dir', './models/cache')
            
            print(f"📥 Loading tokenizer: {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=cache_dir,
                src_lang="eng_Latn",  # Default source
                tgt_lang="hat_Latn"   # Default target
            )
            
            print(f"📥 Loading model: {self.model_name}...")
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name,
                cache_dir=cache_dir,
                torch_dtype=torch.float32  # Use float32 for CPU compatibility
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
