#!/usr/bin/env python3
"""
Text normalization utilities for Kalimax corpus

Handles Unicode normalization, punctuation, whitespace, and variant expansion
"""

import re
import unicodedata
from typing import Dict, List, Optional
import sqlite3
from pathlib import Path


class TextNormalizer:
    """
    Normalize text for consistent processing
    
    Handles:
    - Unicode NFC normalization
    - Punctuation and whitespace normalization
    - Haitian Creole orthography variants
    - Slang/contraction expansion using normalization rules
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize normalizer
        
        Args:
            db_path: Path to SQLite database with normalization_rules table
        """
        self.db_path = db_path
        self.normalization_cache = {}
        
        # Load normalization rules from database if available
        if db_path:
            self._load_normalization_rules()
        
        # Common Haitian Creole orthography variants
        self.orthography_map = {
            # Contractions
            "m'": "mwen ",
            "m'gen": "mwen gen",
            "mgen": "mwen gen",
            "w'": "ou ",
            "l'": "li ",
            
            # Common abbreviations
            "gen": "genyen",
            "pa": "pap",
            
            # Spelling variants
            "get": "gèt",
            "femal": "fè mal",
            "tèt fè mal": "tèt fè mal",
        }
    
    def _load_normalization_rules(self):
        """Load normalization rules from database"""
        if not self.db_path:
            return
        
        db_file = Path(self.db_path)
        if not db_file.exists():
            return
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT variant, canonical 
                FROM normalization_rules
            """)
            
            for variant, canonical in cursor.fetchall():
                self.normalization_cache[variant.lower()] = canonical
            
            conn.close()
            print(f"✅ Loaded {len(self.normalization_cache)} normalization rules")
            
        except sqlite3.Error as e:
            print(f"⚠️  Could not load normalization rules: {e}")
    
    def normalize_unicode(self, text: str) -> str:
        """Normalize Unicode to NFC form"""
        return unicodedata.normalize('NFC', text)
    
    def normalize_punctuation(self, text: str) -> str:
        """Normalize punctuation and quotes"""
        # Replace various quotes with standard ones
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Replace various dashes
        text = text.replace('–', '-').replace('—', '-')
        
        # Normalize ellipsis
        text = re.sub(r'\.\.\.+', '...', text)
        
        # Remove zero-width characters
        text = text.replace('\u200b', '').replace('\ufeff', '')
        
        return text
    
    def normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace"""
        # Replace tabs and multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([,.;:!?])', r'\1', text)
        text = re.sub(r'([,.;:!?])([^\s])', r'\1 \2', text)
        
        return text
    
    def expand_contractions(self, text: str, keep_original: bool = False) -> str:
        """
        Expand Haitian Creole contractions
        
        Args:
            text: Input text
            keep_original: If True, keeps original in parentheses
            
        Returns:
            Expanded text
        """
        expanded = text
        
        # Apply orthography map
        for variant, canonical in self.orthography_map.items():
            if variant in expanded.lower():
                if keep_original and variant != canonical:
                    expanded = re.sub(
                        re.escape(variant), 
                        f"{canonical} ({variant})", 
                        expanded, 
                        flags=re.IGNORECASE
                    )
                else:
                    expanded = re.sub(
                        re.escape(variant), 
                        canonical, 
                        expanded, 
                        flags=re.IGNORECASE
                    )
        
        # Apply database rules
        words = expanded.split()
        normalized_words = []
        
        for word in words:
            lower_word = word.lower()
            if lower_word in self.normalization_cache:
                normalized_words.append(self.normalization_cache[lower_word])
            else:
                normalized_words.append(word)
        
        return ' '.join(normalized_words)
    
    def detect_dosage_pattern(self, text: str) -> bool:
        """
        Detect if text contains dosage/medication instructions
        
        Returns:
            True if dosage pattern detected
        """
        dosage_patterns = [
            r'\d+\s*(mg|g|ml|tablet|tablèt|kapsul|capsule)',
            r'(pran|take|prendre)\s+\d+',
            r'chak\s+\d+\s*(èdtan|hour|heure)',
            r'every\s+\d+\s*hour',
            r'\d+\s*time[s]?\s+(daily|chak jou|per day)',
            r'\d+\s*fwa\s*chak jou',
        ]
        
        for pattern in dosage_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def normalize(
        self, 
        text: str, 
        expand_contractions: bool = True,
        normalize_punct: bool = True
    ) -> str:
        """
        Full normalization pipeline
        
        Args:
            text: Input text
            expand_contractions: Whether to expand contractions
            normalize_punct: Whether to normalize punctuation
            
        Returns:
            Normalized text
        """
        # Unicode normalization
        text = self.normalize_unicode(text)
        
        # Punctuation normalization
        if normalize_punct:
            text = self.normalize_punctuation(text)
        
        # Whitespace normalization
        text = self.normalize_whitespace(text)
        
        # Contraction expansion
        if expand_contractions:
            text = self.expand_contractions(text)
        
        return text
    
    def get_variants(self, text: str) -> List[str]:
        """
        Generate normalized variants of text
        
        Returns list of: [original, normalized, normalized_with_expansions]
        """
        variants = [text]
        
        # Add normalized version
        normalized = self.normalize(text, expand_contractions=False)
        if normalized != text:
            variants.append(normalized)
        
        # Add fully expanded version
        expanded = self.normalize(text, expand_contractions=True)
        if expanded not in variants:
            variants.append(expanded)
        
        return variants


def normalize_corpus_entry(
    src_text: str,
    tgt_text: str,
    normalizer: Optional[TextNormalizer] = None
) -> Dict[str, any]:
    """
    Normalize a corpus entry (source and target pair)
    
    Returns:
        Dictionary with normalized texts and metadata
    """
    if normalizer is None:
        normalizer = TextNormalizer()
    
    result = {
        'src_normalized': normalizer.normalize(src_text),
        'tgt_normalized': normalizer.normalize(tgt_text),
        'src_variants': normalizer.get_variants(src_text),
        'tgt_variants': normalizer.get_variants(tgt_text),
        'contains_dosage': normalizer.detect_dosage_pattern(src_text) or 
                          normalizer.detect_dosage_pattern(tgt_text),
    }
    
    return result


# Example usage and testing
if __name__ == "__main__":
    normalizer = TextNormalizer()
    
    # Test cases
    test_texts = [
        "M'gen yon tèt fè mal",
        "Pran 2  tablèt   chak  6  èdtan",
        "Li lajan li fèt sou do li",
        "The patient  has  chest   pain.",
    ]
    
    print("🧪 Text Normalization Tests\n")
    print("=" * 60)
    
    for text in test_texts:
        print(f"\nOriginal:   {text}")
        print(f"Normalized: {normalizer.normalize(text)}")
        print(f"Dosage:     {normalizer.detect_dosage_pattern(text)}")
        variants = normalizer.get_variants(text)
        if len(variants) > 1:
            print(f"Variants:   {variants}")
