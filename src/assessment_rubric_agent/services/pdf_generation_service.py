"""
PDF Generation Service
Generates beautifully formatted PDF rubrics using WeasyPrint.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..core.schemas.contracts import TeacherRubricContent, StudentRubricContent

logger = logging.getLogger(__name__)


class PDFGenerationService:
    """
    Generates PDF rubrics using Jinja2 templates and WeasyPrint.
    """
    
    def __init__(self, output_dir: str = "outputs/pdfs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Template directory
        self.template_dir = Path(__file__).parent.parent.parent.parent / "templates" / "pdf"
    
    def generate_teacher_rubric(
        self,
        content: TeacherRubricContent,
        request_id: str
    ) -> str:
        """
        Generate Teacher Rubric PDF.
        
        Args:
            content: Teacher rubric content
            request_id: Request identifier for filename
            
        Returns:
            Path to generated PDF
        """
        logger.info(f"Generating teacher rubric PDF for: {request_id}")
        
        try:
            from weasyprint import HTML, CSS
            
            # Generate HTML content
            html_content = self._generate_teacher_html(content)
            
            # Define CSS for beautiful formatting
            css = self._get_teacher_css()
            
            # Generate PDF
            filename = f"teacher_rubric_{request_id}.pdf"
            output_path = self.output_dir / filename
            
            HTML(string=html_content).write_pdf(
                str(output_path),
                stylesheets=[CSS(string=css)]
            )
            
            logger.info(f"Teacher rubric PDF generated: {output_path}")
            return str(output_path)
            
        except ImportError:
            logger.warning("WeasyPrint not available, generating HTML instead")
            return self._generate_html_fallback(content, request_id, "teacher")
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
    
    def generate_student_rubric(
        self,
        content: StudentRubricContent,
        request_id: str
    ) -> str:
        """
        Generate Student Rubric PDF.
        
        Args:
            content: Student rubric content
            request_id: Request identifier for filename
            
        Returns:
            Path to generated PDF
        """
        logger.info(f"Generating student rubric PDF for: {request_id}")
        
        try:
            from weasyprint import HTML, CSS
            
            # Generate HTML content
            html_content = self._generate_student_html(content)
            
            # Define CSS for beautiful formatting
            css = self._get_student_css()
            
            # Generate PDF
            filename = f"student_rubric_{request_id}.pdf"
            output_path = self.output_dir / filename
            
            HTML(string=html_content).write_pdf(
                str(output_path),
                stylesheets=[CSS(string=css)]
            )
            
            logger.info(f"Student rubric PDF generated: {output_path}")
            return str(output_path)
            
        except ImportError:
            logger.warning("WeasyPrint not available, generating HTML instead")
            return self._generate_html_fallback(content, request_id, "student")
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
    
    def _get_teacher_css(self) -> str:
        """Get CSS for teacher rubric"""
        return """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 10pt;
            line-height: 1.5;
            color: #1a1a2e;
            background: #ffffff;
        }
        
        .container {
            max-width: 8.5in;
            margin: 0 auto;
            padding: 0.5in;
        }
        
        /* Header */
        .header {
            background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 24pt;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }
        
        .header .subtitle {
            font-size: 12pt;
            opacity: 0.9;
            font-weight: 300;
        }
        
        .meta-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-top: 20px;
        }
        
        .meta-item {
            background: rgba(255,255,255,0.15);
            padding: 12px;
            border-radius: 8px;
        }
        
        .meta-label {
            font-size: 8pt;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.8;
            margin-bottom: 4px;
        }
        
        .meta-value {
            font-size: 11pt;
            font-weight: 600;
        }
        
        /* Sections */
        .section {
            margin-bottom: 24px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            overflow: hidden;
        }
        
        .section-header {
            background: #f7fafc;
            padding: 16px 20px;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .section-icon {
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 14pt;
        }
        
        .section-title {
            font-size: 14pt;
            font-weight: 600;
            color: #1a365d;
        }
        
        .section-content {
            padding: 20px;
        }
        
        /* Learning Outcomes */
        .outcome-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .outcome-item {
            display: flex;
            gap: 12px;
            padding: 12px;
            background: #f7fafc;
            border-radius: 8px;
            border-left: 4px solid #3182ce;
        }
        
        .outcome-number {
            background: #3182ce;
            color: white;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 10pt;
            flex-shrink: 0;
        }
        
        .outcome-text {
            flex: 1;
            font-size: 10pt;
            line-height: 1.6;
        }
        
        .outcome-bloom {
            font-size: 8pt;
            color: #718096;
            margin-top: 4px;
        }
        
        /* Concept Cards */
        .concept-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
        }
        
        .concept-card {
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            padding: 16px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }
        
        .concept-name {
            font-weight: 600;
            font-size: 10pt;
            color: #1a365d;
            margin-bottom: 8px;
        }
        
        .concept-meta {
            display: flex;
            gap: 8px;
            font-size: 8pt;
        }
        
        .concept-badge {
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: 500;
        }
        
        .badge-core { background: #c6f6d5; color: #276749; }
        .badge-supporting { background: #bee3f8; color: #2b6cb0; }
        .badge-extended { background: #feebc8; color: #c05621; }
        
        /* Rubric Table */
        .rubric-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-size: 9pt;
        }
        
        .rubric-table th {
            background: #1a365d;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            font-size: 9pt;
        }
        
        .rubric-table th:first-child {
            border-radius: 8px 0 0 0;
        }
        
        .rubric-table th:last-child {
            border-radius: 0 8px 0 0;
        }
        
        .rubric-table td {
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
            vertical-align: top;
        }
        
        .rubric-table tr:nth-child(even) {
            background: #f7fafc;
        }
        
        .rubric-table tr:last-child td:first-child {
            border-radius: 0 0 0 8px;
        }
        
        .rubric-table tr:last-child td:last-child {
            border-radius: 0 0 8px 0;
        }
        
        .criterion-name {
            font-weight: 600;
            color: #1a365d;
            margin-bottom: 4px;
        }
        
        .criterion-desc {
            font-size: 8pt;
            color: #718096;
        }
        
        .marks-badge {
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 10pt;
        }
        
        .descriptor-cell {
            font-size: 8pt;
            line-height: 1.5;
        }
        
        /* Performance Levels */
        .levels-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
        }
        
        .level-card {
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }
        
        .level-exemplary { background: linear-gradient(135deg, #c6f6d5 0%, #9ae6b4 100%); }
        .level-proficient { background: linear-gradient(135deg, #bee3f8 0%, #90cdf4 100%); }
        .level-developing { background: linear-gradient(135deg, #feebc8 0%, #fbd38d 100%); }
        .level-beginning { background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%); }
        
        .level-name {
            font-weight: 700;
            font-size: 11pt;
            margin-bottom: 4px;
        }
        
        .level-range {
            font-size: 9pt;
            opacity: 0.8;
            margin-bottom: 8px;
        }
        
        .level-desc {
            font-size: 8pt;
        }
        
        /* Marks Summary */
        .marks-summary {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 12px;
        }
        
        .marks-item {
            background: #f7fafc;
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }
        
        .marks-label {
            font-size: 8pt;
            color: #718096;
            margin-bottom: 4px;
        }
        
        .marks-value {
            font-size: 16pt;
            font-weight: 700;
            color: #1a365d;
        }
        
        /* Teacher Notes */
        .notes-box {
            background: #fffbeb;
            border: 1px solid #fcd34d;
            border-radius: 8px;
            padding: 16px;
        }
        
        .notes-box h4 {
            color: #92400e;
            margin-bottom: 8px;
            font-size: 10pt;
        }
        
        .notes-list {
            font-size: 9pt;
            padding-left: 16px;
        }
        
        .notes-list li {
            margin-bottom: 4px;
            color: #78350f;
        }
        
        /* Misconceptions */
        .misconceptions {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .misconception-tag {
            background: #fed7d7;
            color: #c53030;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 8pt;
        }
        
        /* Footer */
        .footer {
            margin-top: 24px;
            padding-top: 16px;
            border-top: 2px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 8pt;
            color: #718096;
        }
        
        .footer-logo {
            font-weight: 600;
            color: #1a365d;
        }
        
        .page-break {
            page-break-after: always;
        }
        """
    
    def _get_student_css(self) -> str:
        """Get CSS for student rubric"""
        return """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 10pt;
            line-height: 1.5;
            color: #1a1a2e;
            background: #ffffff;
        }
        
        .container {
            max-width: 8.5in;
            margin: 0 auto;
            padding: 0.5in;
        }
        
        /* Header */
        .header {
            background: linear-gradient(135deg, #38a169 0%, #2f855a 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 24px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 22pt;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .header .subtitle {
            font-size: 11pt;
            opacity: 0.9;
        }
        
        .assignment-info {
            display: flex;
            justify-content: center;
            gap: 24px;
            margin-top: 16px;
            font-size: 10pt;
        }
        
        .assignment-info span {
            background: rgba(255,255,255,0.2);
            padding: 6px 16px;
            border-radius: 20px;
        }
        
        /* Section */
        .section {
            margin-bottom: 24px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            overflow: hidden;
            border: 1px solid #e2e8f0;
        }
        
        .section-header {
            background: #f0fff4;
            padding: 16px 20px;
            border-bottom: 1px solid #c6f6d5;
        }
        
        .section-title {
            font-size: 14pt;
            font-weight: 600;
            color: #276749;
        }
        
        .section-content {
            padding: 20px;
        }
        
        /* Criteria Cards */
        .criteria-cards {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .criterion-card {
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            overflow: hidden;
        }
        
        .criterion-header {
            background: linear-gradient(135deg, #edf2f7 0%, #e2e8f0 100%);
            padding: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .criterion-name {
            font-weight: 700;
            font-size: 12pt;
            color: #1a365d;
        }
        
        .criterion-marks {
            background: #38a169;
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 600;
        }
        
        .criterion-body {
            padding: 16px;
        }
        
        .level-row {
            display: flex;
            border-bottom: 1px solid #e2e8f0;
            padding: 12px 0;
        }
        
        .level-row:last-child {
            border-bottom: none;
        }
        
        .level-indicator {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 10pt;
            flex-shrink: 0;
            margin-right: 12px;
        }
        
        .level-excellent { background: #38a169; }
        .level-good { background: #3182ce; }
        .level-fair { background: #dd6b20; }
        .level-needs-work { background: #e53e3e; }
        
        .level-content {
            flex: 1;
        }
        
        .level-name {
            font-weight: 600;
            font-size: 10pt;
            color: #1a365d;
            margin-bottom: 2px;
        }
        
        .level-marks {
            font-size: 8pt;
            color: #718096;
        }
        
        .level-desc {
            font-size: 9pt;
            color: #4a5568;
            margin-top: 4px;
        }
        
        /* Checklist */
        .checklist {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .checklist-item {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 12px;
            background: #f7fafc;
            border-radius: 8px;
        }
        
        .check-box {
            width: 24px;
            height: 24px;
            border: 2px solid #38a169;
            border-radius: 4px;
            flex-shrink: 0;
        }
        
        .check-content {
            flex: 1;
        }
        
        .check-title {
            font-weight: 600;
            color: #1a365d;
            margin-bottom: 4px;
        }
        
        .check-items {
            font-size: 9pt;
            color: #4a5568;
            padding-left: 16px;
        }
        
        .check-items li {
            margin-bottom: 2px;
        }
        
        /* Success Criteria */
        .success-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .success-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 10pt;
            color: #276749;
        }
        
        .success-check {
            color: #38a169;
            font-weight: 700;
        }
        
        /* Footer */
        .footer {
            margin-top: 24px;
            padding-top: 16px;
            border-top: 2px solid #c6f6d5;
            text-align: center;
            font-size: 9pt;
            color: #718096;
        }
        
        .tip-box {
            background: #f0fff4;
            border: 1px solid #9ae6b4;
            border-radius: 8px;
            padding: 16px;
            margin-top: 16px;
            text-align: center;
        }
        
        .tip-box strong {
            color: #276749;
        }
        """
    
    def _generate_teacher_html(self, content: TeacherRubricContent) -> str:
        """Generate HTML for teacher rubric"""
        
        # Build learning outcomes HTML
        outcomes_html = ""
        for i, lo in enumerate(content.learning_outcomes[:5], 1):
            outcomes_html += f"""
            <div class="outcome-item">
                <div class="outcome-number">{i}</div>
                <div>
                    <div class="outcome-text">{lo['statement']}</div>
                    <div class="outcome-bloom">Bloom's Level: {lo.get('blooms_level', 'Understand')}</div>
                </div>
            </div>
            """
        
        # Build concepts HTML
        concepts_html = ""
        for concept in content.concepts_covered[:6]:
            badge_class = f"badge-{concept.get('importance', 'supporting').lower()}"
            concepts_html += f"""
            <div class="concept-card">
                <div class="concept-name">{concept['name']}</div>
                <div class="concept-meta">
                    <span class="concept-badge {badge_class}">{concept.get('importance', 'Core')}</span>
                    <span class="concept-badge">{concept.get('difficulty', 'Medium')}</span>
                </div>
            </div>
            """
        
        # Build rubric table HTML
        rubric_rows = ""
        for criterion in content.criteria:
            descriptors_by_level = {}
            for desc in criterion.performance_descriptors:
                descriptors_by_level[desc.level] = desc.description
            
            exemplary = descriptors_by_level.get('Exemplary', 'N/A')
            proficient = descriptors_by_level.get('Proficient', 'N/A')
            developing = descriptors_by_level.get('Developing', 'N/A')
            beginning = descriptors_by_level.get('Beginning', 'N/A')
            
            rubric_rows += f"""
            <tr>
                <td>
                    <div class="criterion-name">{criterion.criterion_name}</div>
                    <div class="criterion-desc">{criterion.description}</div>
                </td>
                <td class="descriptor-cell"><strong>4:</strong> {exemplary}</td>
                <td class="descriptor-cell"><strong>3:</strong> {proficient}</td>
                <td class="descriptor-cell"><strong>2:</strong> {developing}</td>
                <td class="descriptor-cell"><strong>1:</strong> {beginning}</td>
                <td><span class="marks-badge">{criterion.total_marks}</span></td>
            </tr>
            """
        
        # Build misconceptions HTML
        misconceptions_html = ""
        for misconception in content.common_misconceptions[:5]:
            misconceptions_html += f'<span class="misconception-tag">{misconception}</span>'
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Teacher Rubric - {content.assignment_name}</title>
        </head>
        <body>
            <div class="container">
                <!-- Header -->
                <div class="header">
                    <h1>📋 Assessment Rubric</h1>
                    <div class="subtitle">{content.assignment_name}</div>
                    <div class="meta-grid">
                        <div class="meta-item">
                            <div class="meta-label">Board</div>
                            <div class="meta-value">{content.board}</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">Grade</div>
                            <div class="meta-value">Class {content.grade}</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">Subject</div>
                            <div class="meta-value">{content.subject}</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">Chapter</div>
                            <div class="meta-value">{content.chapter}</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">Total Marks</div>
                            <div class="meta-value">{content.total_marks}</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">Type</div>
                            <div class="meta-value">{content.assessment_type}</div>
                        </div>
                    </div>
                </div>
                
                <!-- Learning Outcomes -->
                <div class="section">
                    <div class="section-header">
                        <div class="section-icon">🎯</div>
                        <div class="section-title">Learning Outcomes</div>
                    </div>
                    <div class="section-content">
                        <div class="outcome-list">
                            {outcomes_html or '<p>No learning outcomes defined</p>'}
                        </div>
                    </div>
                </div>
                
                <!-- Concepts Covered -->
                <div class="section">
                    <div class="section-header">
                        <div class="section-icon">💡</div>
                        <div class="section-title">Concepts Covered</div>
                    </div>
                    <div class="section-content">
                        <div class="concept-grid">
                            {concepts_html or '<p>No concepts defined</p>'}
                        </div>
                    </div>
                </div>
                
                <div class="page-break"></div>
                
                <!-- Rubric Criteria -->
                <div class="section">
                    <div class="section-header">
                        <div class="section-icon">📊</div>
                        <div class="section-title">Rubric Criteria & Performance Descriptors</div>
                    </div>
                    <div class="section-content">
                        <table class="rubric-table">
                            <thead>
                                <tr>
                                    <th style="width: 15%">Criterion</th>
                                    <th style="width: 22%">Exemplary (4)</th>
                                    <th style="width: 22%">Proficient (3)</th>
                                    <th style="width: 22%">Developing (2)</th>
                                    <th style="width: 14%">Beginning (1)</th>
                                    <th style="width: 5%">Marks</th>
                                </tr>
                            </thead>
                            <tbody>
                                {rubric_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Teacher Notes -->
                <div class="section">
                    <div class="section-header">
                        <div class="section-icon">📝</div>
                        <div class="section-title">Teacher Notes & Assessment Tips</div>
                    </div>
                    <div class="section-content">
                        <div class="notes-box">
                            {content.teacher_notes.replace(chr(10), '<br>') if content.teacher_notes else '<p>No additional notes</p>'}
                        </div>
                        
                        {f'''
                        <div style="margin-top: 20px;">
                            <h4 style="color: #c53030; margin-bottom: 8px;">⚠️ Common Misconceptions to Watch For:</h4>
                            <div class="misconceptions">
                                {misconceptions_html or '<span>None identified</span>'}
                            </div>
                        </div>
                        ''' if misconceptions_html else ''}
                    </div>
                </div>
                
                <!-- Footer -->
                <div class="footer">
                    <div class="footer-logo">Assessment Rubric Agent v0.1</div>
                    <div>Generated: {content.generated_date}</div>
                    <div>ID: {content.rubric_id}</div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_student_html(self, content: StudentRubricContent) -> str:
        """Generate HTML for student rubric"""
        
        # Build criteria cards
        criteria_cards = ""
        for criterion in content.criteria:
            levels_html = ""
            for level in criterion.get('levels', []):
                level_class = "level-excellent"
                if "Good" in level.get('level', '') or "Proficient" in level.get('level', ''):
                    level_class = "level-good"
                elif "Fair" in level.get('level', '') or "Developing" in level.get('level', ''):
                    level_class = "level-fair"
                elif "Needs" in level.get('level', '') or "Beginning" in level.get('level', ''):
                    level_class = "level-needs-work"
                
                levels_html += f"""
                <div class="level-row">
                    <div class="level-indicator {level_class}">
                        {'✓' if 'Exemplary' in level.get('level', '') or 'Excellent' in level.get('level', '') else 
                         '●' if 'Good' in level.get('level', '') or 'Proficient' in level.get('level', '') else
                         '○' if 'Fair' in level.get('level', '') or 'Developing' in level.get('level', '') else '✗'}
                    </div>
                    <div class="level-content">
                        <div class="level-name">{level.get('level', 'Level')}</div>
                        <div class="level-marks">Marks: {level.get('marks_range', '0')}</div>
                        <div class="level-desc">{level.get('description', '')}</div>
                    </div>
                </div>
                """
            
            criteria_cards += f"""
            <div class="criterion-card">
                <div class="criterion-header">
                    <div class="criterion-name">{criterion.get('name', 'Criterion')}</div>
                    <div class="criterion-marks">{criterion.get('total_marks', 0)} marks</div>
                </div>
                <div class="criterion-body">
                    <p style="font-size: 9pt; color: #718096; margin-bottom: 12px;">
                        {criterion.get('description', '')}
                    </p>
                    {levels_html}
                </div>
            </div>
            """
        
        # Build checklist
        checklist_items = ""
        for item in content.self_assessment_checklist:
            checklist_items += f"""
            <div class="checklist-item">
                <div class="check-box"></div>
                <div class="check-content">
                    <div class="check-title">{item['number']}. {item['criterion']}</div>
                    <ul class="check-items">
                        {''.join(f"<li>{check}</li>" for check in item['checklist_items'])}
                    </ul>
                </div>
            </div>
            """
        
        # Build success criteria
        success_html = ""
        for success in content.success_criteria:
            success_html += f'<div class="success-item"><span class="success-check">✓</span> {success}</div>'
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Student Rubric - {content.assignment_name}</title>
        </head>
        <body>
            <div class="container">
                <!-- Header -->
                <div class="header">
                    <h1>✨ Your Assessment Rubric</h1>
                    <div class="subtitle">Know what it takes to succeed!</div>
                    <div class="assignment-info">
                        <span>{content.subject}</span>
                        <span>Class {content.grade}</span>
                        <span>{content.total_marks} Total Marks</span>
                    </div>
                </div>
                
                <!-- How to Use -->
                <div class="section">
                    <div class="section-header">
                        <div class="section-title">📖 How to Use This Rubric</div>
                    </div>
                    <div class="section-content">
                        <p style="font-size: 10pt; line-height: 1.6;">
                            This rubric shows <strong>what success looks like</strong> for your assignment. 
                            Read through each criterion and the different levels to understand what you need to do 
                            to achieve your best work!
                        </p>
                    </div>
                </div>
                
                <!-- Criteria -->
                <div class="section">
                    <div class="section-header">
                        <div class="section-title">📋 What You'll Be Assessed On</div>
                    </div>
                    <div class="section-content">
                        <div class="criteria-cards">
                            {criteria_cards}
                        </div>
                    </div>
                </div>
                
                <div class="page-break"></div>
                
                <!-- Success Checklist -->
                <div class="section">
                    <div class="section-header">
                        <div class="section-title">✅ Success Checklist</div>
                    </div>
                    <div class="section-content">
                        <div class="checklist">
                            {checklist_items}
                        </div>
                    </div>
                </div>
                
                <!-- Key Success Criteria -->
                <div class="section">
                    <div class="section-header">
                        <div class="section-title">🎯 Key Things to Remember</div>
                    </div>
                    <div class="section-content">
                        <div class="success-list">
                            {success_html}
                        </div>
                    </div>
                </div>
                
                <!-- Tips -->
                <div class="tip-box">
                    <strong>💡 Remember:</strong> Do your best to meet the criteria at each level. 
                    If you're unsure about something, ask your teacher for help before submitting!
                </div>
                
                <!-- Footer -->
                <div class="footer">
                    <div>Generated: {content.generated_date}</div>
                    <div style="margin-top: 4px; color: #38a169;">You're doing great! 🌟</div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_html_fallback(
        self,
        content,
        request_id: str,
        rubric_type: str
    ) -> str:
        """Generate HTML fallback if WeasyPrint is not available"""
        filename = f"{rubric_type}_rubric_{request_id}.html"
        output_path = self.output_dir / filename
        
        # Just save the HTML content
        html_content = self._generate_teacher_html(content) if rubric_type == "teacher" \
            else self._generate_student_html(content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path)
