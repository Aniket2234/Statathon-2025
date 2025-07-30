"""
SafeData Pipeline - Core Modules
Government of India - Ministry of Electronics and IT
Data Privacy Protection and Anonymization System
"""

__version__ = "1.0.0"
__author__ = "SafeData Pipeline Development Team"
__description__ = "Core modules for data privacy protection and anonymization"

from .data_handler import DataHandler
from .risk_assessment import RiskAssessment
from .privacy_enhancement import PrivacyEnhancement
from .utility_measurement import UtilityMeasurement
from .report_generator import ReportGenerator

__all__ = [
    'DataHandler',
    'RiskAssessment', 
    'PrivacyEnhancement',
    'UtilityMeasurement',
    'ReportGenerator'
]
