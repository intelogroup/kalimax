"""
Curation Prioritization System for Kalimax

This module implements confidence-based prioritization for the human curation workflow,
helping curators focus on the most critical translations first.
"""

import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PriorityLevel(Enum):
    """Priority levels for curation tasks"""
    CRITICAL = 1    # Confidence < 0.3 or high-risk medical
    HIGH = 2        # Confidence 0.3-0.5 or medical domain
    MEDIUM = 3      # Confidence 0.5-0.7 or cultural expressions
    LOW = 4         # Confidence > 0.7 and general domain


@dataclass
class CurationTask:
    """Represents a single curation task with priority metadata"""
    id: int
    table_name: str
    src_text: str
    tgt_text: str
    confidence: float
    domain: str
    priority: PriorityLevel
    risk_flags: List[str]
    cultural_notes: Optional[str] = None
    region: Optional[str] = None
    estimated_time_minutes: int = 5


class CurationPrioritizer:
    """
    Manages confidence-based prioritization for curation workflow
    """
    
    def __init__(self, db_path: str = "data/kalimax.db"):
        """
        Initialize the curation prioritizer
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = Path(db_path)
        self.high_risk_terms = self._load_high_risk_terms()
        
    def _load_high_risk_terms(self) -> set:
        """Load high-risk medical terms from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT creole_term FROM high_risk WHERE risk_level = 'critical'")
                return {row[0].lower() for row in cursor.fetchall()}
        except Exception as e:
            logger.warning(f"Could not load high-risk terms: {e}")
            return set()
    
    def calculate_priority(self, 
                          confidence: float, 
                          domain: str, 
                          text: str,
                          table_name: str) -> Tuple[PriorityLevel, List[str]]:
        """
        Calculate priority level and risk flags for a curation task
        
        Args:
            confidence: Translation confidence score (0.0-1.0)
            domain: Domain category (medical, cultural, general)
            text: Source or target text to analyze
            table_name: Database table name
            
        Returns:
            Tuple of (priority_level, risk_flags)
        """
        risk_flags = []
        
        # Check for high-risk medical terms
        text_lower = text.lower()
        if any(term in text_lower for term in self.high_risk_terms):
            risk_flags.append("high_risk_medical")
            return PriorityLevel.CRITICAL, risk_flags
        
        # Critical priority: Very low confidence
        if confidence < 0.3:
            risk_flags.append("very_low_confidence")
            return PriorityLevel.CRITICAL, risk_flags
        
        # High priority: Medical domain or low confidence
        if domain == "medical" or confidence < 0.5:
            if domain == "medical":
                risk_flags.append("medical_domain")
            if confidence < 0.5:
                risk_flags.append("low_confidence")
            return PriorityLevel.HIGH, risk_flags
        
        # Medium priority: Cultural expressions or moderate confidence
        if table_name == "expressions" or domain == "cultural" or confidence < 0.7:
            if table_name == "expressions":
                risk_flags.append("cultural_expression")
            if confidence < 0.7:
                risk_flags.append("moderate_confidence")
            return PriorityLevel.MEDIUM, risk_flags
        
        # Low priority: High confidence general content
        return PriorityLevel.LOW, risk_flags
    
    def get_prioritized_tasks(self, 
                             limit: int = 50,
                             priority_filter: Optional[PriorityLevel] = None,
                             domain_filter: Optional[str] = None) -> List[CurationTask]:
        """
        Get prioritized list of curation tasks
        
        Args:
            limit: Maximum number of tasks to return
            priority_filter: Filter by specific priority level
            domain_filter: Filter by domain (medical, cultural, general)
            
        Returns:
            List of CurationTask objects ordered by priority
        """
        tasks = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Query all tables with curation_status = 'draft'
                tables_to_check = [
                    ("corpus", "src_text", "tgt_text_localized", "confidence", "domain"),
                    ("glossary", "creole_canonical", "english_equivalents", "confidence", "domain"),
                    ("expressions", "creole", "idiomatic_en", "confidence", "register")
                ]
                
                for table_name, src_col, tgt_col, conf_col, domain_col in tables_to_check:
                    query = f"""
                    SELECT id, {src_col} as src_text, {tgt_col} as tgt_text, 
                           {conf_col} as confidence, {domain_col} as domain,
                           cultural_note, region
                    FROM {table_name} 
                    WHERE curation_status = 'draft'
                    """
                    
                    if domain_filter:
                        query += f" AND {domain_col} = ?"
                        cursor.execute(query, (domain_filter,))
                    else:
                        cursor.execute(query)
                    
                    for row in cursor.fetchall():
                        confidence = row['confidence'] or 0.5
                        domain = row['domain'] or 'general'
                        
                        priority, risk_flags = self.calculate_priority(
                            confidence, domain, row['src_text'], table_name
                        )
                        
                        # Apply priority filter if specified
                        if priority_filter and priority != priority_filter:
                            continue
                        
                        task = CurationTask(
                            id=row['id'],
                            table_name=table_name,
                            src_text=row['src_text'],
                            tgt_text=row['tgt_text'],
                            confidence=confidence,
                            domain=domain,
                            priority=priority,
                            risk_flags=risk_flags,
                            cultural_notes=row.get('cultural_note'),
                            region=row.get('region'),
                            estimated_time_minutes=self._estimate_curation_time(
                                row['src_text'], risk_flags
                            )
                        )
                        tasks.append(task)
        
        except Exception as e:
            logger.error(f"Error retrieving curation tasks: {e}")
            return []
        
        # Sort by priority (critical first) and then by confidence (lowest first)
        tasks.sort(key=lambda t: (t.priority.value, t.confidence))
        
        return tasks[:limit]
    
    def _estimate_curation_time(self, text: str, risk_flags: List[str]) -> int:
        """
        Estimate curation time in minutes based on text complexity and risk flags
        
        Args:
            text: Text to be curated
            risk_flags: List of risk flags
            
        Returns:
            Estimated time in minutes
        """
        base_time = 5  # Base 5 minutes per task
        
        # Add time for complexity
        word_count = len(text.split())
        if word_count > 20:
            base_time += 3
        elif word_count > 10:
            base_time += 2
        
        # Add time for risk factors
        if "high_risk_medical" in risk_flags:
            base_time += 10
        elif "medical_domain" in risk_flags:
            base_time += 5
        
        if "cultural_expression" in risk_flags:
            base_time += 3
        
        if "very_low_confidence" in risk_flags:
            base_time += 5
        
        return min(base_time, 30)  # Cap at 30 minutes
    
    def get_priority_summary(self) -> Dict[str, int]:
        """
        Get summary of tasks by priority level
        
        Returns:
            Dictionary with priority levels and task counts
        """
        summary = {level.name: 0 for level in PriorityLevel}
        
        tasks = self.get_prioritized_tasks(limit=1000)  # Get all tasks
        
        for task in tasks:
            summary[task.priority.name] += 1
        
        return summary
    
    def mark_task_completed(self, table_name: str, task_id: int, curator_notes: str = ""):
        """
        Mark a curation task as completed
        
        Args:
            table_name: Database table name
            task_id: Task ID
            curator_notes: Optional notes from curator
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    UPDATE {table_name} 
                    SET curation_status = 'reviewed',
                        curator_notes = ?,
                        curation_date = datetime('now')
                    WHERE id = ?
                """, (curator_notes, task_id))
                conn.commit()
                logger.info(f"Marked task {task_id} in {table_name} as completed")
        except Exception as e:
            logger.error(f"Error marking task completed: {e}")


def main():
    """Demo function showing prioritizer usage"""
    prioritizer = CurationPrioritizer()
    
    # Get priority summary
    summary = prioritizer.get_priority_summary()
    print("Curation Priority Summary:")
    for level, count in summary.items():
        print(f"  {level}: {count} tasks")
    
    # Get critical priority tasks
    critical_tasks = prioritizer.get_prioritized_tasks(
        limit=10, 
        priority_filter=PriorityLevel.CRITICAL
    )
    
    print(f"\nTop {len(critical_tasks)} Critical Tasks:")
    for i, task in enumerate(critical_tasks, 1):
        print(f"{i}. [{task.table_name}] {task.src_text[:50]}...")
        print(f"   Confidence: {task.confidence:.2f}, Flags: {task.risk_flags}")
        print(f"   Est. time: {task.estimated_time_minutes} min\n")


if __name__ == "__main__":
    main()