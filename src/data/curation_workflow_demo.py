#!/usr/bin/env python3
"""
Kalimax Curation Workflow Demo

Demonstrates the integrated curation workflow improvements:
1. Confidence-based prioritization
2. Medical risk flagging
3. Cultural expression batching
"""

import sys
from pathlib import Path
import logging

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from curation_prioritizer import CurationPrioritizer, PriorityLevel
from medical_risk_flagging import MedicalRiskFlagger, RiskLevel
from cultural_expression_batcher import CulturalExpressionBatcher, HaitianRegion, ExpressionType

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_confidence_prioritization():
    """Demonstrate confidence-based prioritization"""
    print("\n" + "="*60)
    print("🎯 CONFIDENCE-BASED PRIORITIZATION DEMO")
    print("="*60)
    
    prioritizer = CurationPrioritizer()
    
    # Get prioritized tasks
    print("\n📋 Getting prioritized curation tasks...")
    tasks = prioritizer.get_prioritized_tasks(limit=10)
    
    if not tasks:
        print("ℹ️  No tasks found in database")
        return
    
    print(f"\n✅ Found {len(tasks)} prioritized tasks:")
    
    for i, task in enumerate(tasks[:5], 1):
        priority = task.get('priority_level', 'UNKNOWN')
        confidence = task.get('confidence', 0.0)
        domain = task.get('domain', 'general')
        
        # Priority emoji
        priority_emoji = {
            'CRITICAL': '🔴',
            'HIGH': '🟠', 
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }.get(priority, '⚪')
        
        print(f"\n{i}. {priority_emoji} {priority} Priority")
        print(f"   📊 Confidence: {confidence:.2f}")
        print(f"   🏥 Domain: {domain}")
        print(f"   📝 Source: {task.get('src_text', 'N/A')[:50]}...")
        
        if task.get('cultural_note'):
            print(f"   🎭 Cultural Note: {task['cultural_note'][:50]}...")
    
    # Get priority summary
    print("\n📈 Priority Summary:")
    summary = prioritizer.get_priority_summary()
    for priority, count in summary.items():
        emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(priority, '⚪')
        print(f"   {emoji} {priority}: {count} items")


def demo_medical_risk_flagging():
    """Demonstrate medical risk flagging"""
    print("\n" + "="*60)
    print("🚨 MEDICAL RISK FLAGGING DEMO")
    print("="*60)
    
    flagger = MedicalRiskFlagger()
    
    # Flag database entries
    print("\n🔍 Scanning database for medical risks...")
    flagged_count = flagger.flag_database_entries()
    print(f"✅ Flagged {flagged_count} entries with medical risks")
    
    # Get flagged entries by risk level
    for risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
        print(f"\n🚨 {risk_level.value} Risk Items:")
        flagged_items = flagger.get_flagged_entries(risk_level=risk_level)
        
        if not flagged_items:
            print(f"   ✅ No {risk_level.value.lower()} risk items found")
            continue
        
        for i, item in enumerate(flagged_items[:3], 1):  # Show first 3
            risk_flags = item.get('medical_risk_flags', '')
            
            print(f"\n   {i}. ID: {item.get('id')}")
            print(f"      📝 Text: {item.get('src_text', 'N/A')[:50]}...")
            print(f"      🏥 Translation: {item.get('tgt_text_localized', 'N/A')[:50]}...")
            print(f"      🚩 Risk Flags: {risk_flags}")
            print(f"      📊 Confidence: {item.get('confidence', 'N/A')}")
    
    # Show risk distribution
    print("\n📊 Risk Distribution:")
    all_flagged = flagger.get_flagged_entries()
    risk_counts = {}
    for item in all_flagged:
        risk_level = item.get('medical_risk_level', 'UNKNOWN')
        risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
    
    for risk, count in risk_counts.items():
        emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MODERATE': '🟡', 'LOW': '🟢'}.get(risk, '⚪')
        print(f"   {emoji} {risk}: {count} items")


def demo_cultural_expression_batching():
    """Demonstrate cultural expression batching"""
    print("\n" + "="*60)
    print("🎭 CULTURAL EXPRESSION BATCHING DEMO")
    print("="*60)
    
    batcher = CulturalExpressionBatcher()
    
    # Create batches
    print("\n📦 Creating cultural expression batches...")
    batches = batcher.create_batches(batch_size=15)
    
    if not batches:
        print("ℹ️  No cultural expressions found for batching")
        return
    
    print(f"✅ Created {len(batches)} batches")
    
    # Show top batches
    print(f"\n🏆 Top Priority Batches:")
    for i, batch in enumerate(batches[:5], 1):
        region_emoji = {
            'ouest': '🏙️', 'nord': '🏔️', 'sud': '🏖️', 
            'artibonite': '🌾', 'centre': '🏞️'
        }.get(batch.region.value, '🗺️')
        
        type_emoji = {
            'medical_cultural': '🏥', 'religious': '⛪', 'proverb': '📜',
            'family': '👨‍👩‍👧‍👦', 'food': '🍽️', 'idiom': '💬'
        }.get(batch.expression_type.value, '🎭')
        
        print(f"\n{i}. {batch.batch_id}")
        print(f"   {region_emoji} Region: {batch.region.value.title()}")
        print(f"   {type_emoji} Type: {batch.expression_type.value.replace('_', ' ').title()}")
        print(f"   👨‍🏫 Expert: {batch.expert_domain}")
        print(f"   📊 Priority: {batch.priority_score}")
        print(f"   📝 Expressions: {len(batch.expressions)}")
        print(f"   ⏱️  Est. Time: {batch.estimated_review_time} min")
    
    # Export first batch as example
    if batches:
        print(f"\n📄 Exporting sample batch...")
        export_path = batcher.export_batch_for_validation(batches[0])
        if export_path:
            print(f"✅ Exported to: {export_path}")
        else:
            print("❌ Export failed")
    
    # Show regional distribution
    print(f"\n🗺️  Regional Distribution:")
    region_counts = {}
    for batch in batches:
        region = batch.region.value
        region_counts[region] = region_counts.get(region, 0) + 1
    
    for region, count in sorted(region_counts.items()):
        emoji = {
            'ouest': '🏙️', 'nord': '🏔️', 'sud': '🏖️', 
            'artibonite': '🌾', 'centre': '🏞️', 'general': '🌍'
        }.get(region, '🗺️')
        print(f"   {emoji} {region.title()}: {count} batches")


def demo_integrated_workflow():
    """Demonstrate how all components work together"""
    print("\n" + "="*60)
    print("🔄 INTEGRATED WORKFLOW DEMO")
    print("="*60)
    
    print("\n🎯 Integrated Curation Workflow:")
    print("1. 📊 Confidence-based prioritization identifies urgent items")
    print("2. 🚨 Medical risk flagging ensures safety-critical review")
    print("3. 🎭 Cultural batching organizes domain-specific validation")
    print("4. 📋 Dashboard coordinates all workflows in one interface")
    
    # Show workflow statistics
    prioritizer = CurationPrioritizer()
    flagger = MedicalRiskFlagger()
    batcher = CulturalExpressionBatcher()
    
    # Get counts
    priority_tasks = prioritizer.get_prioritized_tasks(limit=1000)
    medical_risks = flagger.get_flagged_entries()
    cultural_batches = batcher.create_batches()
    
    print(f"\n📈 Workflow Coverage:")
    print(f"   🎯 Priority Queue: {len(priority_tasks)} items")
    print(f"   🚨 Medical Risks: {len(medical_risks)} flagged")
    print(f"   🎭 Cultural Batches: {len(cultural_batches)} batches")
    
    # Calculate overlap
    priority_ids = {task.get('id') for task in priority_tasks}
    medical_ids = {item.get('id') for item in medical_risks}
    overlap = len(priority_ids & medical_ids)
    
    print(f"   🔄 Priority-Medical Overlap: {overlap} items")
    
    print(f"\n✅ All workflow components are operational!")
    print(f"🚀 Ready to launch curation dashboard with:")
    print(f"   python run_curation_dashboard.py")


def main():
    """Run all demonstrations"""
    print("🏥 KALIMAX CURATION WORKFLOW DEMONSTRATION")
    print("=" * 60)
    print("This demo shows the three integrated curation improvements:")
    print("1. 🎯 Confidence-based prioritization")
    print("2. 🚨 Medical risk flagging") 
    print("3. 🎭 Cultural expression batching")
    
    try:
        # Run individual demos
        demo_confidence_prioritization()
        demo_medical_risk_flagging()
        demo_cultural_expression_batching()
        demo_integrated_workflow()
        
        print("\n" + "="*60)
        print("✅ DEMONSTRATION COMPLETE")
        print("="*60)
        print("🚀 Next steps:")
        print("1. Launch dashboard: python run_curation_dashboard.py")
        print("2. Review priority queue for urgent items")
        print("3. Address medical risk flags immediately")
        print("4. Export cultural batches for expert review")
        print("5. Monitor curation progress through dashboard")
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())