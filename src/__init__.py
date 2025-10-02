"""
Kalimax - Haitian Creole Translation System

A culturally-aware English-Haitian Creole translation system built on NLLB-200 
with LoRA fine-tuning, optimized for medical and cultural contexts.
"""

__version__ = "0.1.0"
__author__ = "InteloGroup"
__email__ = "contact@intelogroup.com"

from .translator import KalimaxTranslator

__all__ = ["KalimaxTranslator"]