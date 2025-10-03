"""
Medical Risk Flagging System for Kalimax

This module implements automatic flagging of high-risk medical terms that require
immediate human review to prevent potentially dangerous mistranslations.
"""

import sqlite3
import re
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels for medical terms"""
    CRITICAL = "critical"      # Life-threatening if mistranslated
    HIGH = "high"             # Serious medical consequences
    MODERATE = "moderate"     # Important but not life-threatening
    LOW = "low"              # General medical terms


@dataclass
class MedicalRiskFlag:
    """Represents a medical risk flag with context"""
    term: str
    risk_level: RiskLevel
    category: str
    reason: str
    haitian_variants: List[str]
    context_patterns: List[str]


class MedicalRiskFlagger:
    """
    Automatically flags high-risk medical terms for immediate human review
    """
    
    def __init__(self, db_path: str = "data/kalimax.db"):
        """
        Initialize the medical risk flagger
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = Path(db_path)
        self.risk_patterns = self._initialize_risk_patterns()
        self.medication_patterns = self._initialize_medication_patterns()
        self.dosage_patterns = self._initialize_dosage_patterns()
        
    def _initialize_risk_patterns(self) -> Dict[RiskLevel, List[MedicalRiskFlag]]:
        """Initialize patterns for different risk levels"""
        return {
            RiskLevel.CRITICAL: [
                MedicalRiskFlag(
                    term="cardiac arrest",
                    risk_level=RiskLevel.CRITICAL,
                    category="emergency",
                    reason="Life-threatening condition requiring immediate action",
                    haitian_variants=["kè a rete", "kè a kanpe"],
                    context_patterns=[r"\bcardiac\s+arrest\b", r"\bheart\s+stopped\b"]
                ),
                MedicalRiskFlag(
                    term="anaphylaxis",
                    risk_level=RiskLevel.CRITICAL,
                    category="allergy",
                    reason="Severe allergic reaction, potentially fatal",
                    haitian_variants=["gwo alèji", "alèji grav"],
                    context_patterns=[r"\banaphylaxis\b", r"\banaphylactic\s+shock\b"]
                ),
                MedicalRiskFlag(
                    term="stroke",
                    risk_level=RiskLevel.CRITICAL,
                    category="neurological",
                    reason="Brain emergency requiring immediate treatment",
                    haitian_variants=["atak serebral", "paralizi"],
                    context_patterns=[r"\bstroke\b", r"\bcerebral\s+infarction\b"]
                ),
                MedicalRiskFlag(
                    term="overdose",
                    risk_level=RiskLevel.CRITICAL,
                    category="toxicology",
                    reason="Drug overdose can be fatal",
                    haitian_variants=["twòp medikaman", "sèdòz"],
                    context_patterns=[r"\boverdose\b", r"\btoo\s+much\s+medication\b"]
                ),
                MedicalRiskFlag(
                    term="suicide",
                    risk_level=RiskLevel.CRITICAL,
                    category="mental_health",
                    reason="Suicide risk requires immediate intervention",
                    haitian_variants=["touye tèt", "komisuisid"],
                    context_patterns=[r"\bsuicide\b", r"\bkill\s+myself\b", r"\bend\s+my\s+life\b"]
                )
            ],
            RiskLevel.HIGH: [
                MedicalRiskFlag(
                    term="insulin",
                    risk_level=RiskLevel.HIGH,
                    category="medication",
                    reason="Incorrect insulin dosage can be dangerous",
                    haitian_variants=["ensilin", "medikaman diabet"],
                    context_patterns=[r"\binsulin\b", r"\bdiabetic\s+medication\b"]
                ),
                MedicalRiskFlag(
                    term="blood pressure",
                    risk_level=RiskLevel.HIGH,
                    category="cardiovascular",
                    reason="Blood pressure management is critical",
                    haitian_variants=["tansyon", "presyon san"],
                    context_patterns=[r"\bblood\s+pressure\b", r"\bhypertension\b"]
                ),
                MedicalRiskFlag(
                    term="pregnancy",
                    risk_level=RiskLevel.HIGH,
                    category="obstetrics",
                    reason="Pregnancy-related care requires precision",
                    haitian_variants=["gwosès", "ansent"],
                    context_patterns=[r"\bpregnant\b", r"\bpregnancy\b", r"\bexpecting\b"]
                ),
                MedicalRiskFlag(
                    term="chemotherapy",
                    risk_level=RiskLevel.HIGH,
                    category="oncology",
                    reason="Cancer treatment requires precise communication",
                    haitian_variants=["chimyoterapi", "tretman kansè"],
                    context_patterns=[r"\bchemotherapy\b", r"\bchemo\b", r"\bcancer\s+treatment\b"]
                )
            ],
            RiskLevel.MODERATE: [
                MedicalRiskFlag(
                    term="antibiotic",
                    risk_level=RiskLevel.MODERATE,
                    category="medication",
                    reason="Antibiotic resistance and allergies are concerns",
                    haitian_variants=["antibiyotik", "medikaman enfeksyon"],
                    context_patterns=[r"\bantibiotic\b", r"\bpenicillin\b"]
                ),
                MedicalRiskFlag(
                    term="surgery",
                    risk_level=RiskLevel.MODERATE,
                    category="procedure",
                    reason="Surgical procedures require clear communication",
                    haitian_variants=["operasyon", "chiri"],
                    context_patterns=[r"\bsurgery\b", r"\boperation\b", r"\bprocedure\b"]
                )
            ]
        }
    
    def _initialize_medication_patterns(self) -> List[str]:
        """Initialize patterns for medication-related terms"""
        return [
            r"\b\d+\s*mg\b",           # Dosage amounts
            r"\b\d+\s*ml\b",           # Volume measurements
            r"\btake\s+\d+\b",         # Take X pills
            r"\bevery\s+\d+\s+hours\b", # Frequency
            r"\btwice\s+daily\b",      # Frequency
            r"\bonce\s+daily\b",       # Frequency
            r"\bbefore\s+meals\b",     # Timing
            r"\bafter\s+meals\b",      # Timing
            r"\bwith\s+food\b",        # Instructions
            r"\bon\s+empty\s+stomach\b" # Instructions
        ]
    
    def _initialize_dosage_patterns(self) -> List[str]:
        """Initialize patterns for dosage-related terms"""
        return [
            r"\b\d+\s*tablets?\b",
            r"\b\d+\s*capsules?\b",
            r"\b\d+\s*drops?\b",
            r"\b\d+\s*teaspoons?\b",
            r"\b\d+\s*tablespoons?\b",
            r"\bhalf\s+tablet\b",
            r"\bquarter\s+tablet\b"
        ]
    
    def analyze_text_for_risks(self, text: str, context: str = "") -> List[Dict]:
        """
        Analyze text for medical risk factors
        
        Args:
            text: Text to analyze
            context: Additional context (domain, table, etc.)
            
        Returns:
            List of risk flags found
        """
        risks_found = []
        text_lower = text.lower()
        
        # Check against all risk patterns
        for risk_level, risk_flags in self.risk_patterns.items():
            for risk_flag in risk_flags:
                # Check if any pattern matches
                for pattern in risk_flag.context_patterns:
                    if re.search(pattern, text_lower, re.IGNORECASE):
                        risks_found.append({
                            "term": risk_flag.term,
                            "risk_level": risk_level.value,
                            "category": risk_flag.category,
                            "reason": risk_flag.reason,
                            "matched_pattern": pattern,
                            "haitian_variants": risk_flag.haitian_variants,
                            "requires_immediate_review": risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]
                        })
                        break  # Don't duplicate flags for same term
        
        # Check for medication dosage patterns
        medication_risks = self._check_medication_risks(text)
        risks_found.extend(medication_risks)
        
        return risks_found
    
    def _check_medication_risks(self, text: str) -> List[Dict]:
        """Check for medication and dosage-related risks"""
        risks = []
        
        # Check for medication patterns
        for pattern in self.medication_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                risks.append({
                    "term": "medication_dosage",
                    "risk_level": RiskLevel.HIGH.value,
                    "category": "medication",
                    "reason": "Medication dosage requires precise translation",
                    "matched_pattern": pattern,
                    "haitian_variants": ["dòz medikaman", "kantite medikaman"],
                    "requires_immediate_review": True
                })
                break
        
        # Check for dosage patterns
        for pattern in self.dosage_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                risks.append({
                    "term": "dosage_instruction",
                    "risk_level": RiskLevel.HIGH.value,
                    "category": "dosage",
                    "reason": "Dosage instructions must be translated accurately",
                    "matched_pattern": pattern,
                    "haitian_variants": ["enstriksyon dòz", "jan pou pran"],
                    "requires_immediate_review": True
                })
                break
        
        return risks
    
    def flag_database_entries(self, table_name: str = None) -> Dict[str, int]:
        """
        Flag entries in database that contain high-risk medical terms
        
        Args:
            table_name: Specific table to check, or None for all tables
            
        Returns:
            Dictionary with flagging statistics
        """
        stats = {"total_checked": 0, "flagged": 0, "critical": 0, "high": 0}
        
        tables_to_check = [table_name] if table_name else ["corpus", "glossary", "expressions"]
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for table in tables_to_check:
                    if table == "corpus":
                        query = "SELECT id, src_text, tgt_text_localized, domain FROM corpus WHERE curation_status = 'draft'"
                        text_cols = ["src_text", "tgt_text_localized"]
                    elif table == "glossary":
                        query = "SELECT id, creole_canonical, english_equivalents, domain FROM glossary WHERE curation_status = 'draft'"
                        text_cols = ["creole_canonical", "english_equivalents"]
                    elif table == "expressions":
                        query = "SELECT id, creole, idiomatic_en, register FROM expressions WHERE curation_status = 'draft'"
                        text_cols = ["creole", "idiomatic_en"]
                    else:
                        continue
                    
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        stats["total_checked"] += 1
                        row_id = row[0]
                        
                        # Analyze all text columns
                        all_risks = []
                        for i, col in enumerate(text_cols, 1):
                            if row[i]:  # Check if column has content
                                risks = self.analyze_text_for_risks(row[i], table)
                                all_risks.extend(risks)
                        
                        if all_risks:
                            stats["flagged"] += 1
                            
                            # Count by risk level
                            for risk in all_risks:
                                if risk["risk_level"] == "critical":
                                    stats["critical"] += 1
                                elif risk["risk_level"] == "high":
                                    stats["high"] += 1
                            
                            # Update database with risk flags
                            risk_json = json.dumps(all_risks)
                            cursor.execute(f"""
                                UPDATE {table} 
                                SET medical_risk_flags = ?,
                                    requires_immediate_review = 1,
                                    priority_level = CASE 
                                        WHEN ? LIKE '%critical%' THEN 1
                                        WHEN ? LIKE '%high%' THEN 2
                                        ELSE 3
                                    END
                                WHERE id = ?
                            """, (risk_json, risk_json, risk_json, row_id))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error flagging database entries: {e}")
        
        return stats
    
    def get_flagged_entries(self, risk_level: RiskLevel = None, limit: int = 50) -> List[Dict]:
        """
        Get entries that have been flagged for medical risks
        
        Args:
            risk_level: Filter by specific risk level
            limit: Maximum number of entries to return
            
        Returns:
            List of flagged entries with risk information
        """
        flagged_entries = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                tables_to_check = ["corpus", "glossary", "expressions"]
                
                for table in tables_to_check:
                    query = f"""
                    SELECT id, medical_risk_flags, priority_level, requires_immediate_review
                    FROM {table} 
                    WHERE medical_risk_flags IS NOT NULL
                    ORDER BY priority_level ASC, id ASC
                    """
                    
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        try:
                            risk_flags = json.loads(row['medical_risk_flags'])
                            
                            # Filter by risk level if specified
                            if risk_level:
                                risk_flags = [r for r in risk_flags if r['risk_level'] == risk_level.value]
                                if not risk_flags:
                                    continue
                            
                            flagged_entries.append({
                                "table": table,
                                "id": row['id'],
                                "risk_flags": risk_flags,
                                "priority_level": row['priority_level'],
                                "requires_immediate_review": bool(row['requires_immediate_review'])
                            })
                            
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in medical_risk_flags for {table} id {row['id']}")
                            continue
                
        except Exception as e:
            logger.error(f"Error retrieving flagged entries: {e}")
        
        # Sort by priority and limit results
        flagged_entries.sort(key=lambda x: x['priority_level'])
        return flagged_entries[:limit]
    
    def add_custom_risk_pattern(self, 
                               term: str, 
                               risk_level: RiskLevel, 
                               category: str, 
                               reason: str,
                               patterns: List[str],
                               haitian_variants: List[str] = None):
        """
        Add a custom risk pattern to the system
        
        Args:
            term: Medical term
            risk_level: Risk level
            category: Category (e.g., 'medication', 'emergency')
            reason: Reason for flagging
            patterns: Regex patterns to match
            haitian_variants: Haitian Creole variants
        """
        risk_flag = MedicalRiskFlag(
            term=term,
            risk_level=risk_level,
            category=category,
            reason=reason,
            haitian_variants=haitian_variants or [],
            context_patterns=patterns
        )
        
        if risk_level not in self.risk_patterns:
            self.risk_patterns[risk_level] = []
        
        self.risk_patterns[risk_level].append(risk_flag)
        logger.info(f"Added custom risk pattern for '{term}' at {risk_level.value} level")


def main():
    """Demo function showing medical risk flagging usage"""
    flagger = MedicalRiskFlagger()
    
    # Test text analysis
    test_texts = [
        "Patient is experiencing cardiac arrest",
        "Take 2 insulin injections daily",
        "Patient is pregnant and needs surgery",
        "Regular checkup for blood pressure"
    ]
    
    print("Medical Risk Analysis Demo:")
    for text in test_texts:
        risks = flagger.analyze_text_for_risks(text)
        print(f"\nText: '{text}'")
        if risks:
            for risk in risks:
                print(f"  🚨 {risk['term']} ({risk['risk_level']}): {risk['reason']}")
        else:
            print("  ✅ No high-risk terms detected")
    
    # Flag database entries
    print("\nFlagging database entries...")
    stats = flagger.flag_database_entries()
    print(f"Checked: {stats['total_checked']}, Flagged: {stats['flagged']}")
    print(f"Critical: {stats['critical']}, High: {stats['high']}")


if __name__ == "__main__":
    main()