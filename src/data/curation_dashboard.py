"""
Kalimax Curation Management Dashboard

This module provides a comprehensive interface for managing the curation workflow,
integrating confidence-based prioritization, medical risk flagging, and cultural
expression batching into a unified management system.
"""

import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime, timedelta
import logging

# Import our custom modules
from curation_prioritizer import CurationPrioritizer, PriorityLevel
from medical_risk_flagging import MedicalRiskFlagger, RiskLevel
from cultural_expression_batcher import CulturalExpressionBatcher, HaitianRegion, ExpressionType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CurationDashboard:
    """
    Unified dashboard for managing all curation workflows
    """
    
    def __init__(self, db_path: str = "data/kalimax.db"):
        """Initialize the curation dashboard"""
        self.db_path = Path(db_path)
        self.prioritizer = CurationPrioritizer(str(db_path))
        self.risk_flagger = MedicalRiskFlagger(str(db_path))
        self.expression_batcher = CulturalExpressionBatcher(str(db_path))
        
    def get_curation_overview(self) -> Dict:
        """Get overview statistics for the curation dashboard"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get overall statistics
                stats = {}
                
                # Total entries by status
                cursor.execute("""
                    SELECT curation_status, COUNT(*) as count
                    FROM corpus 
                    GROUP BY curation_status
                """)
                stats['corpus_status'] = dict(cursor.fetchall())
                
                # Priority distribution
                cursor.execute("""
                    SELECT priority_level, COUNT(*) as count
                    FROM corpus 
                    WHERE priority_level IS NOT NULL
                    GROUP BY priority_level
                """)
                stats['priority_distribution'] = dict(cursor.fetchall())
                
                # Medical risk flags
                cursor.execute("""
                    SELECT medical_risk_level, COUNT(*) as count
                    FROM corpus 
                    WHERE medical_risk_level IS NOT NULL
                    GROUP BY medical_risk_level
                """)
                stats['medical_risk_distribution'] = dict(cursor.fetchall())
                
                # Expressions by region
                cursor.execute("""
                    SELECT region, COUNT(*) as count
                    FROM expressions 
                    WHERE region IS NOT NULL
                    GROUP BY region
                """)
                stats['expression_regions'] = dict(cursor.fetchall())
                
                # Recent activity
                cursor.execute("""
                    SELECT DATE(updated_at) as date, COUNT(*) as count
                    FROM corpus 
                    WHERE updated_at >= date('now', '-7 days')
                    GROUP BY DATE(updated_at)
                    ORDER BY date DESC
                """)
                stats['recent_activity'] = dict(cursor.fetchall())
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting curation overview: {e}")
            return {}
    
    def get_priority_queue(self, limit: int = 50) -> List[Dict]:
        """Get prioritized curation queue"""
        return self.prioritizer.get_prioritized_tasks(limit=limit)
    
    def get_medical_risk_items(self, risk_level: Optional[RiskLevel] = None) -> List[Dict]:
        """Get medical risk flagged items"""
        return self.risk_flagger.get_flagged_entries(risk_level=risk_level)
    
    def get_cultural_batches(self, region: Optional[HaitianRegion] = None) -> List:
        """Get cultural expression batches"""
        return self.expression_batcher.create_batches(
            batch_size=20, 
            region_filter=region
        )
    
    def update_curation_status(self, entry_id: int, table: str, 
                              new_status: str, curator_notes: str = "") -> bool:
        """Update curation status for an entry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                update_query = f"""
                    UPDATE {table} 
                    SET curation_status = ?, 
                        curator_notes = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """
                
                cursor.execute(update_query, (new_status, curator_notes, entry_id))
                conn.commit()
                
                logger.info(f"Updated {table} entry {entry_id} to status: {new_status}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating curation status: {e}")
            return False
    
    def export_curation_report(self, output_path: str = "data/curation_report.json") -> str:
        """Export comprehensive curation report"""
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'overview': self.get_curation_overview(),
                'priority_queue_summary': {
                    'total_items': len(self.get_priority_queue(limit=1000)),
                    'critical_items': len([t for t in self.get_priority_queue(limit=1000) 
                                         if t.get('priority_level') == 'CRITICAL']),
                    'high_items': len([t for t in self.get_priority_queue(limit=1000) 
                                     if t.get('priority_level') == 'HIGH'])
                },
                'medical_risk_summary': {
                    'total_flagged': len(self.get_medical_risk_items()),
                    'critical_risk': len(self.get_medical_risk_items(RiskLevel.CRITICAL)),
                    'high_risk': len(self.get_medical_risk_items(RiskLevel.HIGH))
                },
                'cultural_batch_summary': {
                    'total_batches': len(self.get_cultural_batches()),
                    'regions_covered': len(set(b.region for b in self.get_cultural_batches())),
                    'expression_types': len(set(b.expression_type for b in self.get_cultural_batches()))
                }
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Exported curation report to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting curation report: {e}")
            return ""


def create_streamlit_dashboard():
    """Create Streamlit dashboard interface"""
    
    st.set_page_config(
        page_title="Kalimax Curation Dashboard",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("🏥 Kalimax Curation Management Dashboard")
    st.markdown("*Unified interface for managing translation curation workflows*")
    
    # Initialize dashboard
    dashboard = CurationDashboard()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["Overview", "Priority Queue", "Medical Risk", "Cultural Batches", "Reports"]
    )
    
    if page == "Overview":
        show_overview_page(dashboard)
    elif page == "Priority Queue":
        show_priority_queue_page(dashboard)
    elif page == "Medical Risk":
        show_medical_risk_page(dashboard)
    elif page == "Cultural Batches":
        show_cultural_batches_page(dashboard)
    elif page == "Reports":
        show_reports_page(dashboard)


def show_overview_page(dashboard: CurationDashboard):
    """Show overview page with key metrics"""
    st.header("📊 Curation Overview")
    
    # Get overview data
    overview = dashboard.get_curation_overview()
    
    if not overview:
        st.error("Unable to load overview data. Please check database connection.")
        return
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_corpus = sum(overview.get('corpus_status', {}).values())
        st.metric("Total Corpus Items", total_corpus)
    
    with col2:
        draft_items = overview.get('corpus_status', {}).get('draft', 0)
        st.metric("Items Pending Review", draft_items)
    
    with col3:
        approved_items = overview.get('corpus_status', {}).get('approved', 0)
        st.metric("Approved Items", approved_items)
    
    with col4:
        flagged_items = sum(overview.get('medical_risk_distribution', {}).values())
        st.metric("Medical Risk Flagged", flagged_items)
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Curation Status Distribution")
        if overview.get('corpus_status'):
            status_df = pd.DataFrame(
                list(overview['corpus_status'].items()),
                columns=['Status', 'Count']
            )
            fig = px.pie(status_df, values='Count', names='Status', 
                        title="Corpus Items by Status")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Priority Distribution")
        if overview.get('priority_distribution'):
            priority_df = pd.DataFrame(
                list(overview['priority_distribution'].items()),
                columns=['Priority', 'Count']
            )
            fig = px.bar(priority_df, x='Priority', y='Count',
                        title="Items by Priority Level")
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("Recent Activity (Last 7 Days)")
    if overview.get('recent_activity'):
        activity_df = pd.DataFrame(
            list(overview['recent_activity'].items()),
            columns=['Date', 'Updates']
        )
        fig = px.line(activity_df, x='Date', y='Updates',
                     title="Daily Curation Activity")
        st.plotly_chart(fig, use_container_width=True)


def show_priority_queue_page(dashboard: CurationDashboard):
    """Show priority queue management page"""
    st.header("⚡ Priority Curation Queue")
    
    # Controls
    col1, col2, col3 = st.columns(3)
    with col1:
        priority_filter = st.selectbox(
            "Filter by Priority:",
            ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"]
        )
    with col2:
        domain_filter = st.selectbox(
            "Filter by Domain:",
            ["All", "medical", "general", "public_health"]
        )
    with col3:
        limit = st.number_input("Items to show:", min_value=10, max_value=200, value=50)
    
    # Get priority queue
    queue = dashboard.get_priority_queue(limit=limit)
    
    if not queue:
        st.info("No items in priority queue.")
        return
    
    # Apply filters
    if priority_filter != "All":
        queue = [item for item in queue if item.get('priority_level') == priority_filter]
    
    if domain_filter != "All":
        queue = [item for item in queue if item.get('domain') == domain_filter]
    
    st.write(f"Showing {len(queue)} items")
    
    # Display queue items
    for i, item in enumerate(queue[:20]):  # Show first 20 items
        with st.expander(f"#{i+1} - {item.get('priority_level', 'UNKNOWN')} Priority"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Source:** {item.get('src_text', 'N/A')}")
                st.write(f"**Translation:** {item.get('tgt_text_localized', 'N/A')}")
                st.write(f"**Domain:** {item.get('domain', 'N/A')}")
                st.write(f"**Confidence:** {item.get('confidence', 'N/A')}")
                
                if item.get('cultural_note'):
                    st.write(f"**Cultural Note:** {item['cultural_note']}")
            
            with col2:
                st.write(f"**ID:** {item.get('id')}")
                st.write(f"**Status:** {item.get('curation_status', 'draft')}")
                
                # Quick action buttons
                if st.button(f"Approve #{item.get('id')}", key=f"approve_{item.get('id')}"):
                    if dashboard.update_curation_status(item['id'], 'corpus', 'approved'):
                        st.success("Approved!")
                        st.rerun()
                
                if st.button(f"Reject #{item.get('id')}", key=f"reject_{item.get('id')}"):
                    if dashboard.update_curation_status(item['id'], 'corpus', 'rejected'):
                        st.success("Rejected!")
                        st.rerun()


def show_medical_risk_page(dashboard: CurationDashboard):
    """Show medical risk management page"""
    st.header("🚨 Medical Risk Management")
    
    # Risk level filter
    risk_filter = st.selectbox(
        "Filter by Risk Level:",
        ["All", "CRITICAL", "HIGH", "MODERATE", "LOW"]
    )
    
    # Get risk items
    risk_level = None if risk_filter == "All" else RiskLevel[risk_filter]
    risk_items = dashboard.get_medical_risk_items(risk_level=risk_level)
    
    if not risk_items:
        st.info("No medical risk items found.")
        return
    
    st.write(f"Found {len(risk_items)} medical risk items")
    
    # Display risk items
    for item in risk_items[:10]:  # Show first 10 items
        risk_level = item.get('medical_risk_level', 'UNKNOWN')
        
        # Color code by risk level
        if risk_level == 'CRITICAL':
            st.error(f"🔴 **CRITICAL RISK** - ID: {item.get('id')}")
        elif risk_level == 'HIGH':
            st.warning(f"🟠 **HIGH RISK** - ID: {item.get('id')}")
        else:
            st.info(f"🟡 **{risk_level} RISK** - ID: {item.get('id')}")
        
        with st.expander(f"View Details - ID {item.get('id')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Source Text:** {item.get('src_text', 'N/A')}")
                st.write(f"**Translation:** {item.get('tgt_text_localized', 'N/A')}")
                st.write(f"**Domain:** {item.get('domain', 'N/A')}")
            
            with col2:
                st.write(f"**Risk Flags:** {item.get('medical_risk_flags', 'N/A')}")
                st.write(f"**Confidence:** {item.get('confidence', 'N/A')}")
                st.write(f"**Status:** {item.get('curation_status', 'draft')}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"Mark Safe #{item.get('id')}", key=f"safe_{item.get('id')}"):
                    if dashboard.update_curation_status(item['id'], 'corpus', 'approved', "Reviewed - Safe"):
                        st.success("Marked as safe!")
                        st.rerun()
            
            with col2:
                if st.button(f"Needs Review #{item.get('id')}", key=f"review_{item.get('id')}"):
                    if dashboard.update_curation_status(item['id'], 'corpus', 'needs_review', "Flagged for expert review"):
                        st.success("Flagged for review!")
                        st.rerun()
            
            with col3:
                if st.button(f"Reject #{item.get('id')}", key=f"reject_risk_{item.get('id')}"):
                    if dashboard.update_curation_status(item['id'], 'corpus', 'rejected', "Medical risk - rejected"):
                        st.success("Rejected!")
                        st.rerun()


def show_cultural_batches_page(dashboard: CurationDashboard):
    """Show cultural expression batches page"""
    st.header("🎭 Cultural Expression Batches")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        region_filter = st.selectbox(
            "Filter by Region:",
            ["All"] + [region.value for region in HaitianRegion]
        )
    with col2:
        type_filter = st.selectbox(
            "Filter by Expression Type:",
            ["All"] + [expr_type.value for expr_type in ExpressionType]
        )
    
    # Get batches
    region = None if region_filter == "All" else HaitianRegion(region_filter)
    batches = dashboard.get_cultural_batches(region=region)
    
    # Apply type filter
    if type_filter != "All":
        batches = [b for b in batches if b.expression_type.value == type_filter]
    
    if not batches:
        st.info("No cultural expression batches found.")
        return
    
    st.write(f"Found {len(batches)} batches")
    
    # Display batches
    for batch in batches[:5]:  # Show first 5 batches
        with st.expander(f"📦 {batch.batch_id} - {batch.region.value.title()} ({batch.expression_type.value})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Region:** {batch.region.value}")
                st.write(f"**Expression Type:** {batch.expression_type.value}")
                st.write(f"**Expert Domain:** {batch.expert_domain}")
                st.write(f"**Expression Count:** {len(batch.expressions)}")
            
            with col2:
                st.write(f"**Priority Score:** {batch.priority_score}")
                st.write(f"**Est. Review Time:** {batch.estimated_review_time} min")
                st.write(f"**Validation Criteria:** {len(batch.validation_criteria)} items")
            
            # Show validation criteria
            if batch.validation_criteria:
                st.write("**Validation Criteria:**")
                for criterion in batch.validation_criteria:
                    st.write(f"• {criterion}")
            
            # Export batch button
            if st.button(f"Export Batch {batch.batch_id}", key=f"export_{batch.batch_id}"):
                export_path = dashboard.expression_batcher.export_batch_for_validation(batch)
                if export_path:
                    st.success(f"Batch exported to: {export_path}")
                else:
                    st.error("Failed to export batch")


def show_reports_page(dashboard: CurationDashboard):
    """Show reports and analytics page"""
    st.header("📈 Reports & Analytics")
    
    # Export report button
    if st.button("Generate Comprehensive Report"):
        report_path = dashboard.export_curation_report()
        if report_path:
            st.success(f"Report generated: {report_path}")
            
            # Show report preview
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                st.subheader("Report Preview")
                st.json(report_data)
                
            except Exception as e:
                st.error(f"Error loading report: {e}")
        else:
            st.error("Failed to generate report")
    
    # Additional analytics could go here
    st.subheader("Quick Stats")
    
    overview = dashboard.get_curation_overview()
    if overview:
        # Create summary metrics
        total_items = sum(overview.get('corpus_status', {}).values())
        pending_items = overview.get('corpus_status', {}).get('draft', 0)
        completion_rate = ((total_items - pending_items) / total_items * 100) if total_items > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Items", total_items)
        with col2:
            st.metric("Pending Review", pending_items)
        with col3:
            st.metric("Completion Rate", f"{completion_rate:.1f}%")


def main():
    """Main function to run the dashboard"""
    try:
        create_streamlit_dashboard()
    except Exception as e:
        st.error(f"Dashboard error: {e}")
        logger.error(f"Dashboard error: {e}")


if __name__ == "__main__":
    main()