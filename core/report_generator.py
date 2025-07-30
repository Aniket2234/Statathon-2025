import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import base64
import io
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from jinja2 import Template
import json

# For PDF generation
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

class ReportGenerator:
    """Report generation module for creating comprehensive privacy-utility reports"""
    
    def __init__(self):
        self.report_templates = {
            'executive': 'executive_summary_template.html',
            'technical': 'technical_report_template.html',
            'comprehensive': 'comprehensive_report_template.html'
        }
    
    def generate_pdf_report(self, report_data: Dict[str, Any], 
                           report_type: str = "Comprehensive Report") -> bytes:
        """
        Generate PDF report
        
        Args:
            report_data: Dictionary containing all report data
            report_type: Type of report to generate
        
        Returns:
            PDF content as bytes
        """
        if not PDF_AVAILABLE:
            raise ImportError("FPDF2 not available. Please install: pip install fpdf2")
        
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Title page
        self._add_title_page(pdf, report_data)
        
        # Executive summary
        self._add_executive_summary(pdf, report_data)
        
        if report_type in ["Technical Report", "Comprehensive Report"]:
            # Technical details
            self._add_technical_details(pdf, report_data)
        
        if report_type == "Comprehensive Report":
            # Detailed analysis
            self._add_detailed_analysis(pdf, report_data)
        
        # Recommendations
        self._add_recommendations(pdf, report_data)
        
        return pdf.output(dest='S').encode('latin-1')
    
    def generate_html_report(self, report_data: Dict[str, Any], 
                            report_type: str = "Comprehensive Report") -> str:
        """
        Generate HTML report
        
        Args:
            report_data: Dictionary containing all report data
            report_type: Type of report to generate
        
        Returns:
            HTML content as string
        """
        # Load template based on report type
        template_content = self._get_html_template(report_type)
        
        template = Template(template_content)
        
        # Prepare data for template
        template_data = self._prepare_template_data(report_data)
        
        # Render template
        html_content = template.render(**template_data)
        
        return html_content
    
    def _add_title_page(self, pdf: FPDF, report_data: Dict[str, Any]):
        """Add title page to PDF"""
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 24)
        pdf.cell(0, 20, report_data.get('title', 'SafeData Privacy-Utility Report'), 0, 1, 'C')
        
        pdf.ln(10)
        
        # Organization
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, report_data.get('organization', 'Government of India'), 0, 1, 'C')
        
        pdf.ln(5)
        
        # Subtitle
        pdf.set_font('Arial', '', 14)
        pdf.cell(0, 10, 'Ministry of Electronics and Information Technology', 0, 1, 'C')
        
        pdf.ln(20)
        
        # Report details
        pdf.set_font('Arial', '', 12)
        
        details = [
            f"Report Generated: {report_data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}",
            f"Author: {report_data.get('author', 'SafeData Pipeline System')}",
            f"Dataset Size: {report_data.get('data_info', {}).get('rows', 'N/A')} rows, {report_data.get('data_info', {}).get('columns', 'N/A')} columns"
        ]
        
        for detail in details:
            pdf.cell(0, 8, detail, 0, 1, 'L')
        
        pdf.ln(20)
        
        # Executive summary box
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'EXECUTIVE SUMMARY', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        
        summary_text = self._generate_executive_summary_text(report_data)
        
        # Split text into lines that fit the page width
        lines = self._split_text_to_lines(pdf, summary_text, 170)
        for line in lines[:10]:  # First 10 lines for title page
            pdf.cell(0, 6, line, 0, 1, 'L')
    
    def _add_executive_summary(self, pdf: FPDF, report_data: Dict[str, Any]):
        """Add executive summary section"""
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'EXECUTIVE SUMMARY', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 11)
        
        # Overall assessment
        overall_risk = report_data.get('risk_results', {}).get('overall_risk', 0)
        overall_utility = report_data.get('utility_results', {}).get('overall_utility', 0)
        
        assessment_text = f"""
This report presents a comprehensive analysis of data privacy and utility for the processed dataset.

PRIVACY ASSESSMENT:
- Overall Re-identification Risk: {overall_risk:.3f}
- Risk Level: {report_data.get('risk_results', {}).get('risk_level', 'Unknown')}
- K-Anonymity Violations: {report_data.get('risk_results', {}).get('k_violations', 'N/A')}
- Unique Records: {report_data.get('risk_results', {}).get('unique_records', 'N/A')}

UTILITY ASSESSMENT:
- Overall Utility Preservation: {overall_utility:.3f}
- Utility Level: {report_data.get('utility_results', {}).get('utility_level', 'Unknown')}

RECOMMENDATIONS:
The analysis indicates that the current privacy-utility trade-off requires careful consideration.
See detailed recommendations section for specific actions.
        """
        
        lines = self._split_text_to_lines(pdf, assessment_text.strip(), 170)
        for line in lines:
            pdf.cell(0, 6, line, 0, 1, 'L')
    
    def _add_technical_details(self, pdf: FPDF, report_data: Dict[str, Any]):
        """Add technical details section"""
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'TECHNICAL ANALYSIS', 0, 1, 'L')
        pdf.ln(5)
        
        # Risk Assessment Details
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 8, 'Risk Assessment Results', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        
        risk_results = report_data.get('risk_results', {})
        if risk_results:
            risk_details = [
                f"Dataset Size Analyzed: {risk_results.get('dataset_size', 'N/A')} records",
                f"Quasi-Identifiers: {', '.join(risk_results.get('quasi_identifiers', []))}",
                f"K-Threshold Used: {risk_results.get('k_threshold', 'N/A')}",
                f"Overall Risk Score: {risk_results.get('overall_risk', 0):.4f}",
                f"Equivalence Classes: {len(risk_results.get('equivalence_classes', []))}",
                f"Attack Scenarios Tested: {', '.join(risk_results.get('attack_scenarios', []))}"
            ]
            
            for detail in risk_details:
                pdf.cell(0, 6, detail, 0, 1, 'L')
        
        pdf.ln(10)
        
        # Utility Measurement Details
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 8, 'Utility Measurement Results', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        
        utility_results = report_data.get('utility_results', {})
        if utility_results:
            utility_details = [
                f"Metrics Computed: {', '.join(utility_results.get('metrics_computed', []))}",
                f"Statistical Similarity: {utility_results.get('statistical_similarity', {}).get('overall', 0):.4f}",
                f"Correlation Preservation: {utility_results.get('correlation_preservation', {}).get('overall', 0):.4f}",
                f"Distribution Similarity: {utility_results.get('distribution_similarity', {}).get('overall', 0):.4f}",
                f"Information Preservation: {utility_results.get('information_loss', {}).get('information_preservation', 0):.4f}"
            ]
            
            for detail in utility_details:
                pdf.cell(0, 6, detail, 0, 1, 'L')
    
    def _add_detailed_analysis(self, pdf: FPDF, report_data: Dict[str, Any]):
        """Add detailed analysis section"""
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'DETAILED ANALYSIS', 0, 1, 'L')
        pdf.ln(5)
        
        # Privacy Analysis
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 8, 'Privacy Protection Analysis', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        
        privacy_analysis = self._generate_privacy_analysis(report_data)
        lines = self._split_text_to_lines(pdf, privacy_analysis, 170)
        for line in lines:
            pdf.cell(0, 6, line, 0, 1, 'L')
        
        pdf.ln(10)
        
        # Utility Analysis
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 8, 'Data Utility Analysis', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        
        utility_analysis = self._generate_utility_analysis(report_data)
        lines = self._split_text_to_lines(pdf, utility_analysis, 170)
        for line in lines:
            pdf.cell(0, 6, line, 0, 1, 'L')
    
    def _add_recommendations(self, pdf: FPDF, report_data: Dict[str, Any]):
        """Add recommendations section"""
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'RECOMMENDATIONS', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 11)
        
        # Get recommendations from risk and utility results
        risk_recommendations = []
        utility_recommendations = []
        
        if 'risk_results' in report_data:
            # Would call risk assessment recommendations method
            risk_recommendations = [
                "Apply stronger anonymization techniques if risk level is high",
                "Consider using differential privacy for highly sensitive data",
                "Review quasi-identifier selection to minimize exposure"
            ]
        
        if 'utility_results' in report_data:
            utility_recommendations = report_data['utility_results'].get('recommendations', [])
        
        all_recommendations = risk_recommendations + utility_recommendations
        
        if all_recommendations:
            for i, rec in enumerate(all_recommendations, 1):
                pdf.cell(0, 8, f"{i}. {rec}", 0, 1, 'L')
        else:
            pdf.cell(0, 8, "No specific recommendations generated.", 0, 1, 'L')
    
    def _generate_executive_summary_text(self, report_data: Dict[str, Any]) -> str:
        """Generate executive summary text"""
        overall_risk = report_data.get('risk_results', {}).get('overall_risk', 0)
        overall_utility = report_data.get('utility_results', {}).get('overall_utility', 0)
        
        if overall_risk < 0.33:
            risk_assessment = "LOW RISK"
        elif overall_risk < 0.67:
            risk_assessment = "MEDIUM RISK"
        else:
            risk_assessment = "HIGH RISK"
        
        if overall_utility > 0.8:
            utility_assessment = "EXCELLENT"
        elif overall_utility > 0.6:
            utility_assessment = "GOOD"
        else:
            utility_assessment = "POOR"
        
        return f"""
This analysis evaluates the privacy protection and data utility of the processed dataset.
PRIVACY: {risk_assessment} (Score: {overall_risk:.3f})
UTILITY: {utility_assessment} (Score: {overall_utility:.3f})

The dataset has been processed using privacy enhancement techniques while attempting to preserve data utility.
The current configuration provides a balance between privacy protection and analytical value.
        """
    
    def _generate_privacy_analysis(self, report_data: Dict[str, Any]) -> str:
        """Generate detailed privacy analysis text"""
        risk_results = report_data.get('risk_results', {})
        
        analysis = f"""
The privacy analysis evaluated re-identification risks using multiple attack scenarios.

Key Findings:
- Overall re-identification risk: {risk_results.get('overall_risk', 0):.4f}
- Number of equivalence classes: {len(risk_results.get('equivalence_classes', []))}
- K-anonymity violations: {risk_results.get('k_violations', 0)}
- Unique records (highest risk): {risk_results.get('unique_records', 0)}

The analysis considered quasi-identifiers: {', '.join(risk_results.get('quasi_identifiers', []))}

Risk levels are classified as Low (<0.33), Medium (0.33-0.67), and High (>0.67).
Current risk level: {risk_results.get('risk_level', 'Unknown')}
        """
        
        return analysis.strip()
    
    def _generate_utility_analysis(self, report_data: Dict[str, Any]) -> str:
        """Generate detailed utility analysis text"""
        utility_results = report_data.get('utility_results', {})
        
        analysis = f"""
The utility analysis measured how well the processed data preserves the analytical value of the original dataset.

Key Metrics:
- Overall utility preservation: {utility_results.get('overall_utility', 0):.4f}
- Statistical similarity: {utility_results.get('statistical_similarity', {}).get('overall', 0):.4f}
- Correlation preservation: {utility_results.get('correlation_preservation', {}).get('overall', 0):.4f}
- Distribution similarity: {utility_results.get('distribution_similarity', {}).get('overall', 0):.4f}

Utility levels are classified as Excellent (>0.9), Good (0.7-0.9), Fair (0.5-0.7), and Poor (<0.5).
Current utility level: {utility_results.get('utility_level', 'Unknown')}

High utility scores indicate that the privacy-enhanced dataset maintains most of its analytical value.
        """
        
        return analysis.strip()
    
    def _split_text_to_lines(self, pdf: FPDF, text: str, max_width: int) -> List[str]:
        """Split text into lines that fit within the specified width"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if pdf.get_string_width(test_line) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _get_html_template(self, report_type: str) -> str:
        """Get HTML template based on report type"""
        # Default comprehensive template
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5rem;
        }
        .header .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-top: 0.5rem;
        }
        .section {
            background: white;
            padding: 2rem;
            margin-bottom: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }
        .metric-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #2c3e50;
        }
        .metric-label {
            color: #7f8c8d;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .risk-high { border-left-color: #e74c3c; }
        .risk-medium { border-left-color: #f39c12; }
        .risk-low { border-left-color: #27ae60; }
        .utility-excellent { border-left-color: #27ae60; }
        .utility-good { border-left-color: #3498db; }
        .utility-fair { border-left-color: #f39c12; }
        .utility-poor { border-left-color: #e74c3c; }
        .recommendations {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 1.5rem;
        }
        .recommendations h3 {
            color: #856404;
            margin-top: 0;
        }
        .recommendations ul {
            margin: 0;
            padding-left: 1.5rem;
        }
        .recommendations li {
            margin-bottom: 0.5rem;
            color: #856404;
        }
        .footer {
            text-align: center;
            padding: 2rem;
            color: #7f8c8d;
            font-size: 0.9rem;
        }
        .visualization-placeholder {
            background: #ecf0f1;
            height: 300px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #7f8c8d;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <div class="subtitle">{{ organization }}</div>
        <div class="subtitle">Generated on {{ date }}</div>
    </div>

    <div class="section">
        <h2>Executive Summary</h2>
        <div class="metric-grid">
            <div class="metric-card {{ risk_class }}">
                <div class="metric-value">{{ overall_risk }}</div>
                <div class="metric-label">Overall Risk Score</div>
            </div>
            <div class="metric-card {{ utility_class }}">
                <div class="metric-value">{{ overall_utility }}</div>
                <div class="metric-label">Overall Utility Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ risk_level }}</div>
                <div class="metric-label">Risk Level</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ utility_level }}</div>
                <div class="metric-label">Utility Level</div>
            </div>
        </div>
    </div>

    {% if risk_results %}
    <div class="section">
        <h2>Privacy Assessment</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-value">{{ risk_results.k_violations }}</div>
                <div class="metric-label">K-Anonymity Violations</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ risk_results.unique_records }}</div>
                <div class="metric-label">Unique Records</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ risk_results.equivalence_classes|length }}</div>
                <div class="metric-label">Equivalence Classes</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ risk_results.dataset_size }}</div>
                <div class="metric-label">Records Analyzed</div>
            </div>
        </div>
        
        <h3>Quasi-Identifiers Analyzed</h3>
        <p>{{ risk_results.quasi_identifiers|join(', ') }}</p>
        
        <h3>Attack Scenarios Tested</h3>
        <p>{{ risk_results.attack_scenarios|join(', ') }}</p>
    </div>
    {% endif %}

    {% if utility_results %}
    <div class="section">
        <h2>Utility Assessment</h2>
        <div class="metric-grid">
            {% if utility_results.statistical_similarity %}
            <div class="metric-card">
                <div class="metric-value">{{ "%.3f"|format(utility_results.statistical_similarity.overall) }}</div>
                <div class="metric-label">Statistical Similarity</div>
            </div>
            {% endif %}
            {% if utility_results.correlation_preservation %}
            <div class="metric-card">
                <div class="metric-value">{{ "%.3f"|format(utility_results.correlation_preservation.overall) }}</div>
                <div class="metric-label">Correlation Preservation</div>
            </div>
            {% endif %}
            {% if utility_results.distribution_similarity %}
            <div class="metric-card">
                <div class="metric-value">{{ "%.3f"|format(utility_results.distribution_similarity.overall) }}</div>
                <div class="metric-label">Distribution Similarity</div>
            </div>
            {% endif %}
            {% if utility_results.information_loss %}
            <div class="metric-card">
                <div class="metric-value">{{ "%.3f"|format(utility_results.information_loss.information_preservation) }}</div>
                <div class="metric-label">Information Preservation</div>
            </div>
            {% endif %}
        </div>
        
        <h3>Metrics Computed</h3>
        <p>{{ utility_results.metrics_computed|join(', ') }}</p>
    </div>
    {% endif %}

    {% if recommendations %}
    <div class="section">
        <h2>Recommendations</h2>
        <div class="recommendations">
            <h3>Action Items</h3>
            <ul>
                {% for rec in recommendations %}
                <li>{{ rec }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>
    {% endif %}

    <div class="footer">
        <p>Report generated by SafeData Pipeline System</p>
        <p>Government of India - Ministry of Electronics and Information Technology</p>
    </div>
</body>
</html>
        """
        
        return template_content
    
    def _prepare_template_data(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for template rendering"""
        risk_results = report_data.get('risk_results', {})
        utility_results = report_data.get('utility_results', {})
        
        overall_risk = risk_results.get('overall_risk', 0)
        overall_utility = utility_results.get('overall_utility', 0)
        
        # Determine CSS classes based on values
        if overall_risk < 0.33:
            risk_class = "risk-low"
        elif overall_risk < 0.67:
            risk_class = "risk-medium"
        else:
            risk_class = "risk-high"
        
        if overall_utility > 0.8:
            utility_class = "utility-excellent"
        elif overall_utility > 0.6:
            utility_class = "utility-good"
        elif overall_utility > 0.4:
            utility_class = "utility-fair"
        else:
            utility_class = "utility-poor"
        
        # Collect all recommendations
        recommendations = []
        if 'recommendations' in utility_results:
            recommendations.extend(utility_results['recommendations'])
        
        template_data = {
            'title': report_data.get('title', 'SafeData Privacy-Utility Report'),
            'organization': report_data.get('organization', 'Government of India'),
            'date': report_data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'author': report_data.get('author', 'SafeData Pipeline System'),
            'overall_risk': f"{overall_risk:.3f}",
            'overall_utility': f"{overall_utility:.3f}",
            'risk_level': risk_results.get('risk_level', 'Unknown'),
            'utility_level': utility_results.get('utility_level', 'Unknown'),
            'risk_class': risk_class,
            'utility_class': utility_class,
            'risk_results': risk_results,
            'utility_results': utility_results,
            'recommendations': recommendations
        }
        
        return template_data
