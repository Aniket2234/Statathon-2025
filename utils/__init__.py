"""
SafeData Pipeline - Utility Modules
Government of India - Ministry of Electronics and IT
Data Privacy Protection and Anonymization System
"""

__version__ = "1.0.0"
__author__ = "SafeData Pipeline Development Team"
__description__ = "Utility modules for file operations, validation, and encryption"

from .file_operations import FileOperations
from .validation import DataValidator
from .encryption import DataEncryption

__all__ = [
    'FileOperations',
    'DataValidator',
    'DataEncryption'
]
