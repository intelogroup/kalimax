"""
Cultural Expression Batching System for Kalimax

This module implements regional batching of cultural expressions for domain expert validation,
organizing expressions by geographic regions and cultural contexts for efficient review.
"""

import sqlite3
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
import json
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HaitianRegion(Enum):
    """Haitian regions for cultural expression categorization"""
    OUEST = "ouest"           # West (Port-au-Prince area)
    NORD = "nord"             # North (Cap-Haïtien area)
    SUD = "sud"               # South (Les Cayes area)
    ARTIBONITE = "artibonite" # Artibonite (Gonaïves area)
    CENTRE = "centre"         # Central (Hinche area)
    GRAND_ANSE = "grand_anse" # Grand'Anse (Jérémie area)
    NIPPES = "nippes"         # Nippes (Miragoâne area)
    NORD_EST = "nord_est"     # Northeast (Fort-Liberté area)
    NORD_OUEST = "nord_ouest" # Northwest (Port-de-Paix area)
    SUD_EST = "sud_est"       # Southeast (Jacmel area)
    GENERAL = "general"       # Pan-Haitian expressions


class ExpressionType(Enum):
    """Types of cultural expressions"""
    IDIOM = "idiom"                    # Idiomatic expressions
    PROVERB = "proverb"               # Traditional proverbs
    MEDICAL_CULTURAL = "medical_cultural" # Medical terms with cultural context
    RELIGIOUS = "religious"           # Religious expressions
    SOCIAL = "social"                 # Social/community expressions
    FAMILY = "family"                 # Family-related expressions
    FOOD = "food"                     # Food and cooking expressions
    WEATHER = "weather"               # Weather and nature expressions
    WORK = "work"                     # Work and occupation expressions
    CELEBRATION = "celebration"       # Celebrations and festivals


@dataclass
class CulturalExpressionBatch:
    """Represents a batch of cultural expressions for validation"""
    batch_id: str
    region: HaitianRegion
    expression_type: ExpressionType
    expressions: List[Dict]
    expert_domain: str
    estimated_review_time: int
    priority_score: float
    cultural_notes: List[str]
    validation_criteria: List[str]


class CulturalExpressionBatcher:
    """
    Manages regional batching of cultural expressions for domain expert validation
    """
    
    def __init__(self, db_path: str = "data/kalimax.db"):
        """
        Initialize the cultural expression batcher
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = Path(db_path)
        self.regional_patterns = self._initialize_regional_patterns()
        self.expression_classifiers = self._initialize_expression_classifiers()
        
    def _initialize_regional_patterns(self) -> Dict[HaitianRegion, List[str]]:
        """Initialize patterns to identify regional expressions"""
        return {
            HaitianRegion.OUEST: [
                r"\bpòtoprens\b", r"\bkapital\b", r"\blavil\b",
                r"\bpetyonvil\b", r"\bdelma\b", r"\bkenskòf\b"
            ],
            HaitianRegion.NORD: [
                r"\bkapayisyen\b", r"\bokap\b", r"\bmilò\b",
                r"\bdondon\b", r"\bplèndino\b"
            ],
            HaitianRegion.SUD: [
                r"\blekay\b", r"\bsud\b", r"\bakayè\b",
                r"\bpòsalè\b", r"\bchantal\b"
            ],
            HaitianRegion.ARTIBONITE: [
                r"\bgonayiv\b", r"\bdesalin\b", r"\bverrèt\b",
                r"\bpetitgwav\b", r"\bmarebalè\b"
            ],
            HaitianRegion.CENTRE: [
                r"\binch\b", r"\bmayisad\b", r"\btomaso\b",
                r"\bboukankarè\b"
            ],
            HaitianRegion.GRAND_ANSE: [
                r"\bjeremi\b", r"\bkorbay\b", r"\bdame mari\b",
                r"\bmoron\b", r"\bpestel\b"
            ],
            HaitianRegion.NIPPES: [
                r"\bmiragwàn\b", r"\bbaradè\b", r"\bfon verrèt\b",
                r"\bpetit trou\b"
            ],
            HaitianRegion.NORD_EST: [
                r"\bfòlibète\b", r"\bwanament\b", r"\bkaraktè\b",
                r"\bmombin kwòch\b"
            ],
            HaitianRegion.NORD_OUEST: [
                r"\bpòdepè\b", r"\bjanrabel\b", r"\bmòlsenmikèl\b",
                r"\bbombadil\b"
            ],
            HaitianRegion.SUD_EST: [
                r"\bjakmèl\b", r"\bmarigò\b", r"\bkayè\b",
                r"\bbèlans\b", r"\bkòtdefe\b"
            ]
        }
    
    def _initialize_expression_classifiers(self) -> Dict[ExpressionType, List[str]]:
        """Initialize patterns to classify expression types"""
        return {
            ExpressionType.IDIOM: [
                r"\bkou\b.*\bkout\b", r"\bsi\b.*\bsi\b", r"\btan\b.*\btan\b",
                r"\bkòm\b.*\bkòm\b", r"\bdepi\b.*\brive\b"
            ],
            ExpressionType.PROVERB: [
                r"^[A-Z].*\.$", r"\bprèvèb\b", r"\bditou\b",
                r"\bgen yon mo ki di\b", r"\bkòm yo di\b"
            ],
            ExpressionType.MEDICAL_CULTURAL: [
                r"\bfèy\b", r"\btizann\b", r"\bremèd\b", r"\bmedsen fèy\b",
                r"\bdoktè fèy\b", r"\bmanbo\b", r"\bwanga\b"
            ],
            ExpressionType.RELIGIOUS: [
                r"\bbondye\b", r"\bjezu\b", r"\bsèn\b", r"\blwa\b",
                r"\bvèvè\b", r"\bpriyè\b", r"\bkanzo\b"
            ],
            ExpressionType.SOCIAL: [
                r"\bkominote\b", r"\bvwazinaj\b", r"\bkonbit\b",
                r"\bsosyete\b", r"\bfamn\b"
            ],
            ExpressionType.FAMILY: [
                r"\bfanmi\b", r"\bmanman\b", r"\bpapa\b", r"\btonton\b",
                r"\bmatant\b", r"\bkouzen\b", r"\btifi\b", r"\btigason\b"
            ],
            ExpressionType.FOOD: [
                r"\bmanje\b", r"\bkuizin\b", r"\bdiri\b", r"\bpwa\b",
                r"\bbanann\b", r"\bkalalou\b", r"\bgriyò\b"
            ],
            ExpressionType.WEATHER: [
                r"\blapli\b", r"\bsèl\b", r"\bvan\b", r"\bsiklòn\b",
                r"\bsezon\b", r"\bfrechè\b", r"\bcho\b"
            ],
            ExpressionType.WORK: [
                r"\btravay\b", r"\bjòb\b", r"\bkòmès\b", r"\bkiltè\b",
                r"\bpeyizan\b", r"\bmachann\b"
            ],
            ExpressionType.CELEBRATION: [
                r"\bfèt\b", r"\bkanaval\b", r"\bnoèl\b", r"\bpak\b",
                r"\bmuzik\b", r"\bdanse\b", r"\bkonpa\b"
            ]
        }
    
    def classify_expression(self, creole_text: str, english_text: str, 
                          cultural_note: str = "") -> Tuple[HaitianRegion, ExpressionType]:
        """
        Classify an expression by region and type
        
        Args:
            creole_text: Haitian Creole text
            english_text: English translation
            cultural_note: Cultural context note
            
        Returns:
            Tuple of (region, expression_type)
        """
        # Combine all text for analysis
        full_text = f"{creole_text} {english_text} {cultural_note}".lower()
        
        # Determine region
        region = HaitianRegion.GENERAL  # Default
        for reg, patterns in self.regional_patterns.items():
            for pattern in patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    region = reg
                    break
            if region != HaitianRegion.GENERAL:
                break
        
        # Determine expression type
        expression_type = ExpressionType.IDIOM  # Default
        max_matches = 0
        
        for exp_type, patterns in self.expression_classifiers.items():
            matches = sum(1 for pattern in patterns 
                         if re.search(pattern, full_text, re.IGNORECASE))
            if matches > max_matches:
                max_matches = matches
                expression_type = exp_type
        
        return region, expression_type
    
    def create_batches(self, batch_size: int = 20, 
                      region_filter: Optional[HaitianRegion] = None,
                      type_filter: Optional[ExpressionType] = None) -> List[CulturalExpressionBatch]:
        """
        Create batches of cultural expressions for validation
        
        Args:
            batch_size: Number of expressions per batch
            region_filter: Filter by specific region
            type_filter: Filter by specific expression type
            
        Returns:
            List of CulturalExpressionBatch objects
        """
        batches = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get expressions that need cultural validation
                query = """
                SELECT id, creole, idiomatic_en, localized_ht, register, region, 
                       cultural_note, confidence, curation_status
                FROM expressions 
                WHERE curation_status = 'draft'
                ORDER BY confidence ASC, id ASC
                """
                
                cursor.execute(query)
                expressions = cursor.fetchall()
                
                # Group expressions by region and type
                grouped_expressions = defaultdict(lambda: defaultdict(list))
                
                for expr in expressions:
                    region, expr_type = self.classify_expression(
                        expr['creole'] or '',
                        expr['idiomatic_en'] or '',
                        expr['cultural_note'] or ''
                    )
                    
                    # Apply filters
                    if region_filter and region != region_filter:
                        continue
                    if type_filter and expr_type != type_filter:
                        continue
                    
                    grouped_expressions[region][expr_type].append(dict(expr))
                
                # Create batches from grouped expressions
                batch_counter = 1
                for region, type_groups in grouped_expressions.items():
                    for expr_type, expressions_list in type_groups.items():
                        # Split into batches of specified size
                        for i in range(0, len(expressions_list), batch_size):
                            batch_expressions = expressions_list[i:i + batch_size]
                            
                            batch = CulturalExpressionBatch(
                                batch_id=f"CULT_{region.value.upper()}_{expr_type.value.upper()}_{batch_counter:03d}",
                                region=region,
                                expression_type=expr_type,
                                expressions=batch_expressions,
                                expert_domain=self._get_expert_domain(region, expr_type),
                                estimated_review_time=self._estimate_batch_time(batch_expressions),
                                priority_score=self._calculate_priority_score(batch_expressions, region, expr_type),
                                cultural_notes=self._extract_cultural_notes(batch_expressions),
                                validation_criteria=self._get_validation_criteria(expr_type)
                            )
                            
                            batches.append(batch)
                            batch_counter += 1
                
        except Exception as e:
            logger.error(f"Error creating cultural expression batches: {e}")
        
        # Sort batches by priority score (highest first)
        batches.sort(key=lambda b: b.priority_score, reverse=True)
        
        return batches
    
    def _get_expert_domain(self, region: HaitianRegion, expr_type: ExpressionType) -> str:
        """Determine the appropriate expert domain for validation"""
        domain_mapping = {
            ExpressionType.MEDICAL_CULTURAL: "medical_anthropologist",
            ExpressionType.RELIGIOUS: "religious_studies",
            ExpressionType.PROVERB: "cultural_linguist",
            ExpressionType.FOOD: "culinary_anthropologist",
            ExpressionType.FAMILY: "social_anthropologist",
            ExpressionType.CELEBRATION: "cultural_historian"
        }
        
        base_domain = domain_mapping.get(expr_type, "cultural_linguist")
        
        # Add regional specialization if not general
        if region != HaitianRegion.GENERAL:
            return f"{base_domain}_{region.value}"
        
        return base_domain
    
    def _estimate_batch_time(self, expressions: List[Dict]) -> int:
        """Estimate review time for a batch in minutes"""
        base_time_per_expression = 8  # Base 8 minutes per expression
        
        total_time = 0
        for expr in expressions:
            time_for_expr = base_time_per_expression
            
            # Add time for complexity
            creole_text = expr.get('creole', '')
            if len(creole_text.split()) > 10:
                time_for_expr += 3
            
            # Add time for low confidence
            confidence = expr.get('confidence', 0.5)
            if confidence < 0.4:
                time_for_expr += 5
            elif confidence < 0.6:
                time_for_expr += 2
            
            # Add time if cultural note exists
            if expr.get('cultural_note'):
                time_for_expr += 2
            
            total_time += time_for_expr
        
        return total_time
    
    def _calculate_priority_score(self, expressions: List[Dict], 
                                 region: HaitianRegion, 
                                 expr_type: ExpressionType) -> float:
        """Calculate priority score for batch ordering"""
        base_score = 50.0
        
        # Type-based priority
        type_priorities = {
            ExpressionType.MEDICAL_CULTURAL: 20,
            ExpressionType.RELIGIOUS: 15,
            ExpressionType.PROVERB: 10,
            ExpressionType.FAMILY: 8,
            ExpressionType.SOCIAL: 8,
            ExpressionType.FOOD: 5,
            ExpressionType.CELEBRATION: 5,
            ExpressionType.WEATHER: 3,
            ExpressionType.WORK: 3,
            ExpressionType.IDIOM: 2
        }
        
        base_score += type_priorities.get(expr_type, 0)
        
        # Region-based priority (major regions get higher priority)
        major_regions = {HaitianRegion.OUEST, HaitianRegion.NORD, HaitianRegion.SUD}
        if region in major_regions:
            base_score += 10
        elif region != HaitianRegion.GENERAL:
            base_score += 5
        
        # Confidence-based priority (lower confidence = higher priority)
        avg_confidence = sum(expr.get('confidence', 0.5) for expr in expressions) / len(expressions)
        confidence_bonus = (1.0 - avg_confidence) * 20
        base_score += confidence_bonus
        
        # Batch size bonus (larger batches are more efficient)
        if len(expressions) >= 15:
            base_score += 5
        elif len(expressions) >= 10:
            base_score += 3
        
        return round(base_score, 2)
    
    def _extract_cultural_notes(self, expressions: List[Dict]) -> List[str]:
        """Extract unique cultural notes from expressions"""
        notes = set()
        for expr in expressions:
            if expr.get('cultural_note'):
                notes.add(expr['cultural_note'])
        return list(notes)
    
    def _get_validation_criteria(self, expr_type: ExpressionType) -> List[str]:
        """Get validation criteria for expression type"""
        criteria_mapping = {
            ExpressionType.IDIOM: [
                "Verify idiomatic meaning accuracy",
                "Check cultural appropriateness",
                "Confirm regional usage",
                "Validate register level"
            ],
            ExpressionType.PROVERB: [
                "Verify traditional accuracy",
                "Check cultural significance",
                "Confirm widespread usage",
                "Validate moral/lesson content"
            ],
            ExpressionType.MEDICAL_CULTURAL: [
                "Verify medical accuracy",
                "Check cultural sensitivity",
                "Confirm traditional usage",
                "Validate safety implications"
            ],
            ExpressionType.RELIGIOUS: [
                "Verify religious accuracy",
                "Check cultural sensitivity",
                "Confirm denominational appropriateness",
                "Validate spiritual context"
            ],
            ExpressionType.FAMILY: [
                "Verify family relationship accuracy",
                "Check cultural appropriateness",
                "Confirm social context",
                "Validate generational usage"
            ]
        }
        
        return criteria_mapping.get(expr_type, [
            "Verify translation accuracy",
            "Check cultural appropriateness",
            "Confirm regional usage",
            "Validate context suitability"
        ])
    
    def export_batch_for_validation(self, batch: CulturalExpressionBatch, 
                                   output_dir: str = "data/validation_batches") -> str:
        """
        Export a batch to CSV for expert validation
        
        Args:
            batch: CulturalExpressionBatch to export
            output_dir: Directory to save the batch file
            
        Returns:
            Path to the exported file
        """
        import csv
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        filename = f"{batch.batch_id}.csv"
        filepath = output_path / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'id', 'creole', 'idiomatic_en', 'localized_ht', 'register',
                    'region', 'cultural_note', 'confidence', 'validation_status',
                    'expert_notes', 'approved', 'needs_revision'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for expr in batch.expressions:
                    row = {
                        'id': expr['id'],
                        'creole': expr.get('creole', ''),
                        'idiomatic_en': expr.get('idiomatic_en', ''),
                        'localized_ht': expr.get('localized_ht', ''),
                        'register': expr.get('register', ''),
                        'region': expr.get('region', ''),
                        'cultural_note': expr.get('cultural_note', ''),
                        'confidence': expr.get('confidence', ''),
                        'validation_status': 'pending',
                        'expert_notes': '',
                        'approved': '',
                        'needs_revision': ''
                    }
                    writer.writerow(row)
            
            # Create batch metadata file
            metadata = {
                'batch_id': batch.batch_id,
                'region': batch.region.value,
                'expression_type': batch.expression_type.value,
                'expert_domain': batch.expert_domain,
                'estimated_review_time': batch.estimated_review_time,
                'priority_score': batch.priority_score,
                'validation_criteria': batch.validation_criteria,
                'cultural_notes': batch.cultural_notes,
                'expression_count': len(batch.expressions)
            }
            
            metadata_file = output_path / f"{batch.batch_id}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported batch {batch.batch_id} to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error exporting batch {batch.batch_id}: {e}")
            return ""


def main():
    """Demo function showing cultural expression batching usage"""
    batcher = CulturalExpressionBatcher()
    
    # Create batches
    print("Creating cultural expression batches...")
    batches = batcher.create_batches(batch_size=15)
    
    print(f"\nCreated {len(batches)} batches:")
    for batch in batches[:5]:  # Show first 5 batches
        print(f"\n📦 {batch.batch_id}")
        print(f"   Region: {batch.region.value}")
        print(f"   Type: {batch.expression_type.value}")
        print(f"   Expert: {batch.expert_domain}")
        print(f"   Expressions: {len(batch.expressions)}")
        print(f"   Est. time: {batch.estimated_review_time} min")
        print(f"   Priority: {batch.priority_score}")
    
    # Export first batch as example
    if batches:
        export_path = batcher.export_batch_for_validation(batches[0])
        print(f"\n📄 Exported first batch to: {export_path}")


if __name__ == "__main__":
    import re
    main()