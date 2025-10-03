#!/usr/bin/env python3
"""
Data Validation Script for Kalimax CSV Files
Analyzes CSV data for missing values, incorrect values, and data integrity issues.
"""

import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Any, Optional

class DataValidator:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.stats = {}
        
        # Expected column schemas for different file types
        self.schemas = {
            'glossary': {
                'required_columns': [
                    'creole_canonical', 'english_equivalents', 'aliases', 'domain', 
                    'cultural_weight', 'preferred_for_patients', 'part_of_speech', 
                    'formality', 'frequency', 'region', 'polysemy', 'examples_good', 
                    'examples_bad', 'notes', 'created_by'
                ],
                'expected_values': {
                    'domain': {
                        'medical', 'general', 'anatomy', 'condition', 
                        'dental_derm', 'equipment', 'facility', 'medication',
                        'pharmacy', 'preventive', 'procedure', 'symptom', 'slang'
                    },
                    'cultural_weight': {'positive', 'negative', 'neutral', 'taboo'},
                    'preferred_for_patients': {'0', '1', 'true', 'false'},
                    'formality': {'formal', 'informal', 'neutral', 'unknown'},
                    'frequency': {'high', 'medium', 'low', 'common'},
                    'region': {'standard', 'north', 'south', 'west', 'port-au-prince'},
                    'polysemy': {'yes', 'no'},
                    'created_by': {
                        'seed_data', 'manual_curation', 'auto_generated', 
                        'bulk_generator', 'seed_script'
                    }
                },
                'id_pattern': None  # No specific ID pattern for glossary
            },
            'corpus': {
                'required_columns': [
                    'id', 'src_text', 'src_lang', 'tgt_text_literal', 
                    'tgt_text_localized', 'tgt_lang', 'domain', 'is_idiom', 
                    'contains_dosage', 'context', 'cultural_note', 'provenance', 
                    'curation_status'
                ],
                'expected_values': {
                    'src_lang': {'eng_Latn'},
                    'tgt_lang': {'hat_Latn'},
                    'domain': {
                        'medical', 'general', 'public_health', 'chronic_disease', 
                        'mental_health', 'preventive_care', 'patient_questions', 
                        'womens_health', 'pediatric', 'lab_results', 
                        'medication_instructions', 'post_operative',
                        'emergency_symptoms', 'diet_nutrition', 'follow_up',
                        'pain_assessment', 'patient_communication'
                    },
                    'is_idiom': {'0', '1'},
                    'contains_dosage': {'0', '1'},
                    'provenance': {'seed_data', 'bulk_generator', 'manual_curation', 'template_generation', 'auto_generated'},
                    'curation_status': {'draft', 'approved', 'validated', 'needs_review', 'rejected', 'pending'}
                },
                'id_pattern': r'^corp_[a-z_]+_\d{3,5}$'  # Flexible pattern to handle 3-5 digit numbers
            },
            'unpolite': {
                'required_columns': [
                    'id', 'src_text', 'src_lang', 'tgt_text_literal', 
                    'tgt_text_localized', 'tgt_lang', 'domain', 'is_idiom', 
                    'contains_dosage', 'context', 'cultural_note', 'provenance', 
                    'curation_status'
                ],
                'expected_values': {
                    'src_lang': {'eng_Latn'},
                    'tgt_lang': {'hat_Latn'},
                    'domain': {'patient_communication'},
                    'is_idiom': {'0', '1'},
                    'contains_dosage': {'0', '1'},
                    'provenance': {'manual_curation', 'template_generation', 'auto_generated'},
                    'curation_status': {'validated', 'needs_review', 'rejected', 'pending'}
                },
                'id_pattern': r'^unpol_\d{4}$'
            },
            'expressions': {
                'required_columns': [
                    'creole', 'literal_gloss_en', 'idiomatic_en', 
                    'localized_ht', 'register', 'region', 'cultural_note'
                ],
                'expected_values': {
                    'register': {'formal', 'informal', 'neutral'},
                    'region': {
                        'General', 'Haiti-North', 'Haiti-South', 'Haiti-West',
                        'Diaspora-US', 'Diaspora-Canada', 'Diaspora-France'
                    }
                },
                'id_pattern': None  # No specific ID pattern for expressions
            },
            'expansion': {
                'required_columns': [
                    'id', 'src_text', 'src_lang', 'tgt_text_literal', 
                    'tgt_text_localized', 'tgt_lang', 'domain', 'is_idiom', 
                    'contains_dosage', 'context', 'cultural_note', 'provenance', 
                    'curation_status'
                ],
                'expected_values': {
                    'src_lang': {'eng_Latn'},
                    'tgt_lang': {'hat_Latn'},
                    'domain': {
                        'chronic_disease', 'mental_health', 'preventive_care', 
                        'patient_questions', 'womens_health', 'pediatric',
                        'lab_results', 'medication_instructions', 'post_operative',
                        'emergency_symptoms', 'diet_nutrition', 'follow_up',
                        'pain_assessment', 'patient_communication'
                    },
                    'is_idiom': {'0', '1'},
                    'contains_dosage': {'0', '1'},
                    'provenance': {'manual_curation', 'template_generation', 'auto_generated'},
                    'curation_status': {'validated', 'needs_review', 'rejected', 'pending'}
                },
                'id_pattern': r'^exp_[a-z_]+_\d{5}$|^unpol_\d{4}$'
            },
            'high_risk': {
                'required_columns': [
                    'id', 'src_en', 'tgt_ht_literal', 'tgt_ht_localized', 
                    'contains_dosage', 'dosage_json', 'instruction_type', 
                    'risk_level', 'safety_flags', 'require_human_review', 
                    'provenance', 'notes'
                ],
                'expected_values': {
                    'contains_dosage': {'0', '1'},
                    'instruction_type': {'dosage', 'procedure', 'symptom', 'triage'},
                    'risk_level': {'high', 'medium'},
                    'require_human_review': {'0', '1'},
                    'provenance': {'seed_data', 'bulk_generator'}
                },
                'id_pattern': r'^hr_[a-z_]+_\d{3,5}$'
            }
        }

    def detect_file_type(self, filepath: Path) -> str:
        """Detect the type of CSV file based on filename and content."""
        filename = filepath.name.lower()
        
        if 'glossary' in filename:
            return 'glossary'
        elif 'corpus' in filename:
            return 'corpus'
        elif 'expressions' in filename:
            return 'expressions'
        elif 'unpolite' in filename:
            return 'unpolite'
        elif 'expansion' in filename:
            return 'expansion'
        elif 'high_risk' in filename or 'highrisk' in filename:
            return 'high_risk'
        else:
            return 'expansion'  # default assumption

    def validate_csv_structure(self, filepath: Path) -> bool:
        """Validate basic CSV structure and readability."""
        try:
            with open(filepath, 'r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f)
                headers = next(reader)
                
                # Check if we can read all rows
                row_count = 0
                for row in reader:
                    row_count += 1
                    
                self.stats['total_rows'] = row_count
                self.stats['headers'] = headers
                return True
                
        except Exception as e:
            self.issues.append(f"Failed to read CSV file: {e}")
            return False

    def validate_headers(self, headers: List[str], schema: Dict) -> bool:
        """Validate CSV headers against expected schema."""
        required_columns = set(schema['required_columns'])
        actual_columns = set(headers)
        
        missing_columns = required_columns - actual_columns
        extra_columns = actual_columns - required_columns
        
        if missing_columns:
            self.issues.append(f"Missing required columns: {missing_columns}")
            
        if extra_columns:
            self.warnings.append(f"Extra columns found: {extra_columns}")
            
        return len(missing_columns) == 0

    def _get_optional_fields(self, file_type: str, column: str) -> bool:
        """Check if a field is optional for a given file type."""
        optional_fields_by_type = {
            'glossary': {
                'examples_good', 'examples_bad', 'notes'
            },
            'corpus': {
                'context', 'cultural_note'
            },
            'expressions': set(),  # All fields required
            'unpolite': {
                'context', 'cultural_note'
            },
            'expansion': {
                'context', 'cultural_note'
            },
            'high_risk': {
                'dosage_json', 'safety_flags', 'notes'
            }
        }
        
        optional_fields = optional_fields_by_type.get(file_type, set())
        return column in optional_fields

    def validate_row_data(self, row_num: int, row_data: Dict[str, str], schema: Dict):
        """Validate individual row data against schema."""
        file_type = self.stats.get('file_type', '')
        
        # Check for missing values with file-type specific handling
        for col, value in row_data.items():
            if not value or value.strip() == '':
                # Define which fields are optional for each file type
                optional_fields = self._get_optional_fields(file_type, col)
                
                if not optional_fields:
                    self.issues.append(f"Row {row_num}: Empty value in column '{col}'")
        
        # Validate specific column values
        expected_values = schema.get('expected_values', {})
        
        for col, expected_set in expected_values.items():
            if col in row_data:
                actual_value = row_data[col].strip()
                if actual_value and actual_value not in expected_set:
                    self.issues.append(
                        f"Row {row_num}: Invalid value '{actual_value}' in column '{col}'. "
                        f"Expected one of: {expected_set}"
                    )
        
        # Validate ID format
        if 'id_pattern' in schema and schema['id_pattern'] and 'id' in row_data:
            id_value = row_data['id'].strip()
            if id_value and not re.match(schema['id_pattern'], id_value):
                self.issues.append(
                    f"Row {row_num}: ID '{id_value}' doesn't match expected pattern"
                )
        
        # Validate JSON fields (only if not empty)
        if 'context' in row_data and row_data['context'].strip():
            try:
                json.loads(row_data['context'])
            except json.JSONDecodeError as e:
                self.issues.append(f"Row {row_num}: Invalid JSON in context field: {e}")
        
        # Validate high_risk specific JSON fields
        if 'dosage_json' in row_data and row_data['dosage_json'].strip():
            try:
                json.loads(row_data['dosage_json'])
            except json.JSONDecodeError as e:
                self.issues.append(f"Row {row_num}: Invalid JSON in dosage_json field: {e}")
        
        if 'safety_flags' in row_data and row_data['safety_flags'].strip():
            try:
                parsed = json.loads(row_data['safety_flags'])
                if not isinstance(parsed, list):
                    self.issues.append(f"Row {row_num}: safety_flags must be a JSON array")
            except json.JSONDecodeError as e:
                self.issues.append(f"Row {row_num}: Invalid JSON in safety_flags field: {e}")
        
        # Validate glossary-specific JSON array fields
        json_array_fields = ['english_equivalents', 'aliases', 'examples_good', 'examples_bad']
        for field in json_array_fields:
            if field in row_data and row_data[field].strip():
                try:
                    parsed = json.loads(row_data[field])
                    if not isinstance(parsed, list):
                        self.issues.append(f"Row {row_num}: {field} must be a JSON array")
                except json.JSONDecodeError as e:
                    self.issues.append(f"Row {row_num}: Invalid JSON in {field}: {e}")
        
        # Validate text content
        self.validate_text_content(row_num, row_data)
        
        # Validate language consistency
        self.validate_language_consistency(row_num, row_data)

    def validate_text_content(self, row_num: int, row_data: Dict[str, str]):
        """Validate text content for basic quality checks."""
        # Check source text (different field names for different file types)
        src_field = 'src_en' if 'src_en' in row_data else 'src_text'
        if src_field in row_data:
            src_text = row_data[src_field].strip().strip('"')
            if len(src_text) < 3:
                self.warnings.append(f"Row {row_num}: Source text seems too short")
            if len(src_text) > 500:
                self.warnings.append(f"Row {row_num}: Source text seems too long")
        
        # Check target texts (different field names for different file types)
        tgt_fields = ['tgt_text_literal', 'tgt_text_localized', 'tgt_ht_literal', 'tgt_ht_localized']
        for field in tgt_fields:
            if field in row_data:
                tgt_text = row_data[field].strip()
                if len(tgt_text) < 2:
                    self.warnings.append(f"Row {row_num}: {field} seems too short")
                if len(tgt_text) > 500:
                    self.warnings.append(f"Row {row_num}: {field} seems too long")

    def validate_language_consistency(self, row_num: int, row_data: Dict[str, str]):
        """Check for language code consistency."""
        # For files with src_lang field
        if row_data.get('src_lang') == 'eng_Latn':
            src_text = row_data.get('src_text', '').strip().strip('"')
            # Basic check for non-English characters in English text
            if any(ord(char) > 127 for char in src_text if char.isalpha()):
                self.warnings.append(
                    f"Row {row_num}: Source text contains non-ASCII characters but marked as English"
                )
        
        # For high_risk files, check the src_en field (assumed English)
        if 'src_en' in row_data:
            src_text = row_data['src_en'].strip().strip('"')
            if any(ord(char) > 127 for char in src_text if char.isalpha()):
                self.warnings.append(
                    f"Row {row_num}: Source text contains non-ASCII characters but should be English"
                )
        
        # For files with tgt_lang field
        if row_data.get('tgt_lang') == 'hat_Latn':
            # Check for Haitian Kreyol specific characters/patterns
            for field in ['tgt_text_literal', 'tgt_text_localized']:
                if field in row_data:
                    tgt_text = row_data[field].strip()
                    # Look for Kreyol patterns (expanded for medical terminology)
                    kreyol_indicators = [
                        'pa ', 'nan ', 'ak ', 'pou ', 'ki ', 'se ', 'yo ', 'la ', 'an ',
                        'li ', 'ou ', 'moun ', 'gen ', 'fè ', 'ale ', 'vin ', 'sou ',
                        'ap ', 'ka ', 'si ', 'lè ', 'yon ', 'chak ', 'tout ', 'anvan ',
                        'apre', 'kote', 'tan ', 'jou ', 'minit', 'èdtan', 'doktè',
                        'rele', 'pran', 'bay', 'bezwen', 'dwe', 'mal', 'lopital'
                    ]
                    if len(tgt_text) > 15 and not any(pattern in tgt_text.lower() for pattern in kreyol_indicators):
                        self.warnings.append(
                            f"Row {row_num}: {field} might not be Haitian Kreyol"
                        )
        
        # For high_risk files, check Haitian Kreyol fields (assumed Haitian Kreyol)
        for field in ['tgt_ht_literal', 'tgt_ht_localized']:
            if field in row_data:
                tgt_text = row_data[field].strip()
                # Look for Kreyol patterns (expanded for medical terminology)
                kreyol_indicators = [
                    'pa ', 'nan ', 'ak ', 'pou ', 'ki ', 'se ', 'yo ', 'la ', 'an ',
                    'li ', 'ou ', 'moun ', 'gen ', 'fè ', 'ale ', 'vin ', 'sou ',
                    'ap ', 'ka ', 'si ', 'lè ', 'yon ', 'chak ', 'tout ', 'anvan ',
                    'apre', 'kote', 'tan ', 'jou ', 'minit', 'èdtan', 'doktè',
                    'rele', 'pran', 'bay', 'bezwen', 'dwe', 'mal', 'lopital'
                ]
                if len(tgt_text) > 15 and not any(pattern in tgt_text.lower() for pattern in kreyol_indicators):
                    self.warnings.append(
                        f"Row {row_num}: {field} might not be Haitian Kreyol"
                    )

    def check_duplicates(self, data: List[Dict[str, str]]):
        """Check for duplicate entries."""
        seen_ids = set()
        seen_src_texts = set()
        seen_canonical_terms = set()
        
        for i, row in enumerate(data, start=1):
            # Check duplicate IDs (for non-glossary files)
            row_id = row.get('id', '').strip()
            if row_id:
                if row_id in seen_ids:
                    self.issues.append(f"Row {i}: Duplicate ID '{row_id}'")
                else:
                    seen_ids.add(row_id)
            
            # Check duplicate source texts (for non-glossary files)
            src_text = row.get('src_text', row.get('src_en', '')).strip().strip('"').lower()
            if src_text:
                if src_text in seen_src_texts:
                    self.warnings.append(f"Row {i}: Duplicate source text")
                else:
                    seen_src_texts.add(src_text)
            
            # Check duplicate canonical terms (for glossary files)
            canonical_term = row.get('creole_canonical', '').strip().lower()
            if canonical_term:
                if canonical_term in seen_canonical_terms:
                    self.warnings.append(f"Row {i}: Duplicate canonical term '{canonical_term}'")
                else:
                    seen_canonical_terms.add(canonical_term)

    def validate_file(self, filepath: Path) -> Dict[str, Any]:
        """Main validation function for a CSV file."""
        self.issues = []
        self.warnings = []
        self.stats = {}
        
        print(f"Validating file: {filepath}")
        print("=" * 60)
        
        # Detect file type and get appropriate schema
        file_type = self.detect_file_type(filepath)
        schema = self.schemas[file_type]
        
        # Store file type in stats for use in validation
        self.stats['file_type'] = file_type
        
        # Basic structure validation
        if not self.validate_csv_structure(filepath):
            return {'success': False, 'issues': self.issues}
        
        # Read and validate data
        data = []
        try:
            with open(filepath, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                
                # Validate headers
                if not self.validate_headers(headers, schema):
                    return {'success': False, 'issues': self.issues}
                
                # Validate each row
                for row_num, row in enumerate(reader, start=2):  # start=2 because header is row 1
                    data.append(row)
                    self.validate_row_data(row_num, row, schema)
        
        except Exception as e:
            self.issues.append(f"Error reading data: {e}")
            return {'success': False, 'issues': self.issues}
        
        # Check for duplicates
        self.check_duplicates(data)
        
        # Generate statistics
        self.stats.update({
            'file_type': file_type,
            'total_data_rows': len(data),
            'total_issues': len(self.issues),
            'total_warnings': len(self.warnings)
        })
        
        # Print results
        self.print_results()
        
        return {
            'success': len(self.issues) == 0,
            'issues': self.issues,
            'warnings': self.warnings,
            'stats': self.stats
        }

    def print_results(self):
        """Print validation results."""
        print(f"\nVALIDATION RESULTS")
        print(f"File type: {self.stats.get('file_type', 'unknown')}")
        print(f"Total data rows: {self.stats.get('total_data_rows', 0)}")
        print(f"Total issues: {len(self.issues)}")
        print(f"Total warnings: {len(self.warnings)}")
        
        if self.issues:
            print(f"\n❌ ISSUES FOUND ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i:2d}. {issue}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i:2d}. {warning}")
        
        if not self.issues and not self.warnings:
            print(f"\n✅ No issues or warnings found!")
        elif not self.issues:
            print(f"\n✅ No critical issues found (only warnings)")


def main():
    if len(sys.argv) < 2:
        print("Usage: python data_validator.py <csv_file_path>")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    
    if not filepath.exists():
        print(f"Error: File {filepath} does not exist")
        sys.exit(1)
    
    validator = DataValidator()
    result = validator.validate_file(filepath)
    
    if not result['success']:
        sys.exit(1)


if __name__ == "__main__":
    main()