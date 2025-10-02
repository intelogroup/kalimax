#!/usr/bin/env python3
"""
Export training data from Kalimax corpus database to JSONL format

Generates training-ready JSONL with:
- Language/domain/audience tokens
- Weight assignments for oversampling
- Tags for filtering and analysis
- Two-row format (literal vs localized) or mode-token format
"""

import sqlite3
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import uuid


class TrainingExporter:
    """Export corpus data to training-ready JSONL format"""
    
    # Default sampling weights by domain and mode
    WEIGHT_CONFIG = {
        'medical': {
            'literal': 1.0,
            'localized': 3.0,  # Oversample patient-friendly
        },
        'public_health': {
            'literal': 1.0,
            'localized': 2.0,
        },
        'general': {
            'literal': 1.0,
            'localized': 1.0,
        },
        'idiom': 4.0,  # Heavily oversample idioms
        'high_risk': 1.0,  # Include but don't oversample (needs strict QA)
        'profanity': 2.0,  # Ensure model learns these
        'synthetic': 0.5,  # Lower weight for back-translation
    }
    
    def __init__(self, db_path: str = "data/kalimax_corpus.db"):
        """
        Initialize exporter
        
        Args:
            db_path: Path to SQLite database
        """
        project_root = Path(__file__).parent.parent.parent
        self.db_file = project_root / db_path
        
        if not self.db_file.exists():
            raise FileNotFoundError(f"Database not found: {self.db_file}")
        
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row  # Access columns by name
    
    def _build_input_text(
        self,
        src_text: str,
        src_lang: str = 'eng_Latn',
        tgt_lang: str = 'hat_Latn',
        domain: str = 'general',
        audience: str = 'patient',
        mode: Optional[str] = None
    ) -> str:
        """
        Build input text with control tokens
        
        Format: <src:LANG> <tgt:LANG> <domain:DOMAIN> <audience:AUDIENCE> [<mode:MODE>] TEXT
        """
        tokens = [
            f"<src:{src_lang}>",
            f"<tgt:{tgt_lang}>",
            f"<domain:{domain}>",
            f"<audience:{audience}>",
        ]
        
        if mode:
            tokens.append(f"<mode:{mode}>")
        
        return ' '.join(tokens) + ' ' + src_text
    
    def _calculate_weight(
        self,
        domain: str,
        mode: str,
        is_idiom: bool = False,
        is_synthetic: bool = False,
        contains_dosage: bool = False
    ) -> float:
        """Calculate sampling weight for a training example"""
        
        # Base weight from domain and mode
        if is_idiom:
            weight = self.WEIGHT_CONFIG['idiom']
        elif is_synthetic:
            weight = self.WEIGHT_CONFIG['synthetic']
        elif domain in self.WEIGHT_CONFIG and mode in self.WEIGHT_CONFIG[domain]:
            weight = self.WEIGHT_CONFIG[domain][mode]
        else:
            weight = 1.0
        
        # Reduce weight for high-risk dosage examples (need strict QA, less training emphasis)
        if contains_dosage:
            weight *= 0.7
        
        return weight
    
    def _build_tags(
        self,
        mode: str,
        domain: str,
        is_idiom: bool = False,
        contains_dosage: bool = False,
        curation_status: str = 'draft',
        provenance: str = ''
    ) -> List[str]:
        """Build tags list for filtering"""
        tags = [
            f"mode:{mode}",
            f"domain:{domain}",
            f"status:{curation_status}",
        ]
        
        if is_idiom:
            tags.append("is_idiom")
        if contains_dosage:
            tags.append("contains_dosage")
            tags.append("risk:high")
        
        if 'seed' in provenance.lower():
            tags.append("set:seed")
        elif 'synthetic' in provenance.lower():
            tags.append("source:synthetic")
        
        return tags
    
    def export_corpus(
        self,
        output_path: str = "data/training_export.jsonl",
        mode_format: str = "two_row",  # "two_row" or "mode_token"
        min_status: str = "draft",  # "draft", "reviewed", or "approved"
        limit: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Export corpus table to JSONL
        
        Args:
            output_path: Output JSONL file path
            mode_format: "two_row" (separate rows for literal/localized) or 
                        "mode_token" (single row with mode token)
            min_status: Minimum curation status to include
            limit: Maximum number of rows (for testing)
            
        Returns:
            Statistics dictionary
        """
        project_root = Path(__file__).parent.parent.parent
        output_file = project_root / output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Build query based on status
        status_filter = {
            'draft': "('draft', 'reviewed', 'approved')",
            'reviewed': "('reviewed', 'approved')",
            'approved': "('approved')",
        }
        
        query = f"""
            SELECT * FROM corpus
            WHERE curation_status IN {status_filter[min_status]}
            ORDER BY is_idiom DESC, contains_dosage DESC, domain, created_at
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor = self.conn.cursor()
        cursor.execute(query)
        
        stats = {
            'total_rows': 0,
            'literal_rows': 0,
            'localized_rows': 0,
            'idiom_rows': 0,
            'dosage_rows': 0,
            'skipped_rows': 0,
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for row in cursor.fetchall():
                row_dict = dict(row)
                stats['total_rows'] += 1
                
                # Parse context if available
                context = {}
                if row_dict['context']:
                    try:
                        context = json.loads(row_dict['context'])
                    except json.JSONDecodeError:
                        pass
                
                audience = context.get('audience', 'patient')
                
                # Export literal translation
                if row_dict['tgt_text_literal']:
                    entry = self._export_row(
                        row_dict=row_dict,
                        mode='literal',
                        target_text=row_dict['tgt_text_literal'],
                        audience=audience,
                        mode_format=mode_format
                    )
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                    stats['literal_rows'] += 1
                
                # Export localized translation
                if row_dict['tgt_text_localized']:
                    entry = self._export_row(
                        row_dict=row_dict,
                        mode='localized',
                        target_text=row_dict['tgt_text_localized'],
                        audience=audience,
                        mode_format=mode_format
                    )
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                    stats['localized_rows'] += 1
                
                if row_dict['is_idiom']:
                    stats['idiom_rows'] += 1
                if row_dict['contains_dosage']:
                    stats['dosage_rows'] += 1
        
        cursor.close()
        
        print(f"✅ Exported {stats['total_rows']} corpus entries")
        print(f"   Literal rows:    {stats['literal_rows']}")
        print(f"   Localized rows:  {stats['localized_rows']}")
        print(f"   Idiom examples:  {stats['idiom_rows']}")
        print(f"   Dosage examples: {stats['dosage_rows']}")
        print(f"📁 Output: {output_file}")
        
        return stats
    
    def _export_row(
        self,
        row_dict: Dict,
        mode: str,
        target_text: str,
        audience: str,
        mode_format: str
    ) -> Dict:
        """Export a single training row"""
        
        # Build input text
        if mode_format == "mode_token":
            input_text = self._build_input_text(
                src_text=row_dict['src_text'],
                src_lang=row_dict['src_lang'],
                tgt_lang=row_dict['tgt_lang'],
                domain=row_dict['domain'],
                audience=audience,
                mode=mode
            )
        else:  # two_row format
            input_text = self._build_input_text(
                src_text=row_dict['src_text'],
                src_lang=row_dict['src_lang'],
                tgt_lang=row_dict['tgt_lang'],
                domain=row_dict['domain'],
                audience=audience
            )
        
        # Calculate weight
        weight = self._calculate_weight(
            domain=row_dict['domain'],
            mode=mode,
            is_idiom=bool(row_dict['is_idiom']),
            contains_dosage=bool(row_dict['contains_dosage'])
        )
        
        # Build tags
        tags = self._build_tags(
            mode=mode,
            domain=row_dict['domain'],
            is_idiom=bool(row_dict['is_idiom']),
            contains_dosage=bool(row_dict['contains_dosage']),
            curation_status=row_dict['curation_status'],
            provenance=row_dict['provenance'] or ''
        )
        
        # Build metadata
        metadata = {
            'provenance': row_dict['provenance'],
            'confidence': row_dict['confidence'],
            'dataset_name': row_dict['dataset_name'],
            'dataset_version': row_dict['dataset_version'],
        }
        
        if row_dict['cultural_note']:
            metadata['cultural_note'] = row_dict['cultural_note']
        
        if row_dict['aliases']:
            try:
                metadata['aliases'] = json.loads(row_dict['aliases'])
            except json.JSONDecodeError:
                pass
        
        return {
            'id': f"{row_dict['id']}_{mode}",
            'input_text': input_text,
            'target_text': target_text,
            'weight': weight,
            'tags': tags,
            'metadata': metadata
        }
    
    def export_expressions(self, output_path: str = "data/expressions_export.jsonl") -> int:
        """Export expressions/idioms table"""
        project_root = Path(__file__).parent.parent.parent
        output_file = project_root / output_path
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM expressions")
        
        count = 0
        with open(output_file, 'w', encoding='utf-8') as f:
            for row in cursor.fetchall():
                row_dict = dict(row)
                
                # Export Creole → English (literal)
                entry_literal = {
                    'id': f"{row_dict['id']}_ht_en_lit",
                    'input_text': f"<src:hat_Latn> <tgt:eng_Latn> <domain:general> {row_dict['creole']}",
                    'target_text': row_dict['literal_gloss_en'],
                    'weight': self.WEIGHT_CONFIG['idiom'],
                    'tags': ['mode:literal', 'is_idiom', 'direction:ht_en'],
                    'metadata': {
                        'register': row_dict['register'],
                        'region': row_dict['region'],
                        'cultural_note': row_dict['cultural_note']
                    }
                }
                f.write(json.dumps(entry_literal, ensure_ascii=False) + '\n')
                count += 1
                
                # Export Creole → English (idiomatic)
                if row_dict['idiomatic_en']:
                    entry_idiom = {
                        'id': f"{row_dict['id']}_ht_en_idiom",
                        'input_text': f"<src:hat_Latn> <tgt:eng_Latn> <domain:general> <mode:idiomatic> {row_dict['creole']}",
                        'target_text': row_dict['idiomatic_en'],
                        'weight': self.WEIGHT_CONFIG['idiom'],
                        'tags': ['mode:idiomatic', 'is_idiom', 'direction:ht_en'],
                        'metadata': {
                            'register': row_dict['register'],
                            'region': row_dict['region'],
                            'cultural_note': row_dict['cultural_note']
                        }
                    }
                    f.write(json.dumps(entry_idiom, ensure_ascii=False) + '\n')
                    count += 1
        
        cursor.close()
        print(f"✅ Exported {count} expression rows to {output_file}")
        return count
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Export Kalimax training data")
    parser.add_argument('--output', default='data/training_export.jsonl',
                       help='Output JSONL path')
    parser.add_argument('--format', choices=['two_row', 'mode_token'], default='two_row',
                       help='Export format')
    parser.add_argument('--status', choices=['draft', 'reviewed', 'approved'], default='reviewed',
                       help='Minimum curation status')
    parser.add_argument('--limit', type=int, help='Limit number of rows (for testing)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Small export for dry-run training (200 rows)')
    
    args = parser.parse_args()
    
    if args.dry_run:
        args.limit = 200
        args.output = 'data/training_export_dryrun.jsonl'
        args.status = 'draft'  # Include all for testing
        print("🧪 Dry-run mode: exporting 200 rows for testing\n")
    
    try:
        exporter = TrainingExporter()
        stats = exporter.export_corpus(
            output_path=args.output,
            mode_format=args.format,
            min_status=args.status,
            limit=args.limit
        )
        exporter.export_expressions()
        exporter.close()
        
        print("\n✅ Export complete!")
        return 0
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
