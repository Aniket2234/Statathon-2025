import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import re
import logging
from datetime import datetime

class DataValidator:
    """Data validation utility for ensuring data quality and integrity"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Validation rules
        self.min_rows = 1
        self.max_rows = 1000000  # 1M rows max
        self.min_columns = 1
        self.max_columns = 1000
        self.max_missing_percentage = 90  # 90% missing data threshold
        
        # Column name patterns
        self.invalid_column_patterns = [
            r'^[0-9]',  # Starting with number
            r'\s+$',    # Ending with whitespace
            r'^\s+',    # Starting with whitespace
        ]
        
        # Data type validation patterns
        self.email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        self.phone_pattern = r'^[\+]?[1-9]?\d{9,15}$'
        self.date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
        ]
    
    def validate_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive data validation
        
        Args:
            data: Input DataFrame to validate
        
        Returns:
            Dictionary containing validation results
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {},
            'column_issues': {},
            'recommendations': []
        }
        
        try:
            # Basic structure validation
            self._validate_structure(data, validation_results)
            
            # Column validation
            self._validate_columns(data, validation_results)
            
            # Data type validation
            self._validate_data_types(data, validation_results)
            
            # Missing data validation
            self._validate_missing_data(data, validation_results)
            
            # Data consistency validation
            self._validate_consistency(data, validation_results)
            
            # Privacy-specific validation
            self._validate_privacy_concerns(data, validation_results)
            
            # Generate statistics
            validation_results['statistics'] = self._generate_statistics(data)
            
            # Determine overall validity
            if validation_results['errors']:
                validation_results['is_valid'] = False
            
            self.logger.info(f"Data validation completed. Valid: {validation_results['is_valid']}")
            
        except Exception as e:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Validation process failed: {str(e)}")
            self.logger.error(f"Data validation error: {str(e)}")
        
        return validation_results
    
    def _validate_structure(self, data: pd.DataFrame, results: Dict[str, Any]):
        """Validate basic data structure"""
        
        # Check if DataFrame is empty
        if data.empty:
            results['errors'].append("Dataset is empty")
            return
        
        # Check row count
        if len(data) < self.min_rows:
            results['errors'].append(f"Dataset has too few rows: {len(data)} (minimum: {self.min_rows})")
        elif len(data) > self.max_rows:
            results['warnings'].append(f"Dataset is very large: {len(data)} rows (consider chunked processing)")
        
        # Check column count
        if len(data.columns) < self.min_columns:
            results['errors'].append(f"Dataset has too few columns: {len(data.columns)}")
        elif len(data.columns) > self.max_columns:
            results['warnings'].append(f"Dataset has many columns: {len(data.columns)} (may impact performance)")
        
        # Check for duplicate columns
        duplicate_columns = data.columns[data.columns.duplicated()].tolist()
        if duplicate_columns:
            results['errors'].append(f"Duplicate column names found: {duplicate_columns}")
    
    def _validate_columns(self, data: pd.DataFrame, results: Dict[str, Any]):
        """Validate column names and properties"""
        
        for col in data.columns:
            col_issues = []
            
            # Check for invalid column name patterns
            for pattern in self.invalid_column_patterns:
                if re.search(pattern, str(col)):
                    col_issues.append(f"Invalid column name pattern: {col}")
            
            # Check for very long column names
            if len(str(col)) > 100:
                col_issues.append(f"Column name too long: {col}")
            
            # Check for special characters that might cause issues
            if any(char in str(col) for char in ['<', '>', '&', '"', "'"]):
                col_issues.append(f"Column name contains problematic characters: {col}")
            
            # Check for entirely numeric column names (can cause issues)
            if str(col).isdigit():
                col_issues.append(f"Purely numeric column name: {col}")
            
            if col_issues:
                results['column_issues'][col] = col_issues
                results['warnings'].extend(col_issues)
    
    def _validate_data_types(self, data: pd.DataFrame, results: Dict[str, Any]):
        """Validate data types and detect potential type mismatches"""
        
        for col in data.columns:
            series = data[col].dropna()
            
            if len(series) == 0:
                continue
            
            # Check for mixed data types in object columns
            if series.dtype == 'object':
                self._validate_object_column(col, series, results)
            
            # Check for numeric columns with potential issues
            elif series.dtype in ['int64', 'float64']:
                self._validate_numeric_column(col, series, results)
            
            # Check for datetime columns
            elif series.dtype == 'datetime64[ns]':
                self._validate_datetime_column(col, series, results)
    
    def _validate_object_column(self, col: str, series: pd.Series, results: Dict[str, Any]):
        """Validate object/string columns"""
        
        # Check if column might be numeric but stored as string
        numeric_count = 0
        total_count = 0
        
        for value in series.head(100):  # Sample first 100 values
            if pd.notna(value):
                total_count += 1
                try:
                    float(str(value).replace(',', '').replace('$', ''))
                    numeric_count += 1
                except:
                    pass
        
        if total_count > 0 and numeric_count / total_count > 0.8:
            results['warnings'].append(f"Column '{col}' appears to be numeric but stored as text")
        
        # Check for potential date columns
        date_count = 0
        for value in series.head(50):
            if pd.notna(value) and self._looks_like_date(str(value)):
                date_count += 1
        
        if date_count > len(series) * 0.5:
            results['warnings'].append(f"Column '{col}' appears to contain dates")
        
        # Check for potential email addresses
        email_count = sum(1 for value in series.head(50) 
                         if pd.notna(value) and re.match(self.email_pattern, str(value)))
        if email_count > 0:
            results['warnings'].append(f"Column '{col}' may contain email addresses (PII concern)")
        
        # Check for potential phone numbers
        phone_count = sum(1 for value in series.head(50)
                         if pd.notna(value) and re.match(self.phone_pattern, str(value).replace('-', '').replace(' ', '')))
        if phone_count > 0:
            results['warnings'].append(f"Column '{col}' may contain phone numbers (PII concern)")
    
    def _validate_numeric_column(self, col: str, series: pd.Series, results: Dict[str, Any]):
        """Validate numeric columns"""
        
        # Check for infinite values
        if np.isinf(series).any():
            results['warnings'].append(f"Column '{col}' contains infinite values")
        
        # Check for very large numbers that might be IDs stored as numeric
        if series.max() > 1e10:
            results['warnings'].append(f"Column '{col}' contains very large numbers (possible ID field)")
        
        # Check for negative values in potentially positive-only columns
        negative_indicators = ['age', 'count', 'quantity', 'amount', 'price', 'distance', 'weight', 'height']
        if any(indicator in col.lower() for indicator in negative_indicators):
            if (series < 0).any():
                results['warnings'].append(f"Column '{col}' has negative values (unexpected for this type)")
        
        # Check for extreme outliers
        if len(series) > 10:  # Only for reasonably sized series
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            
            if iqr > 0:
                outlier_threshold = 3 * iqr
                outliers = ((series < (q1 - outlier_threshold)) | 
                           (series > (q3 + outlier_threshold))).sum()
                
                outlier_percentage = (outliers / len(series)) * 100
                if outlier_percentage > 10:
                    results['warnings'].append(f"Column '{col}' has {outlier_percentage:.1f}% potential outliers")
    
    def _validate_datetime_column(self, col: str, series: pd.Series, results: Dict[str, Any]):
        """Validate datetime columns"""
        
        # Check for future dates (might be data entry errors)
        future_dates = series > pd.Timestamp.now()
        if future_dates.any():
            results['warnings'].append(f"Column '{col}' contains future dates")
        
        # Check for very old dates (might be default/error values)
        very_old = series < pd.Timestamp('1900-01-01')
        if very_old.any():
            results['warnings'].append(f"Column '{col}' contains dates before 1900")
    
    def _validate_missing_data(self, data: pd.DataFrame, results: Dict[str, Any]):
        """Validate missing data patterns"""
        
        total_cells = len(data) * len(data.columns)
        missing_cells = data.isnull().sum().sum()
        missing_percentage = (missing_cells / total_cells) * 100
        
        if missing_percentage > self.max_missing_percentage:
            results['errors'].append(f"Dataset has {missing_percentage:.1f}% missing data (exceeds {self.max_missing_percentage}% threshold)")
        elif missing_percentage > 50:
            results['warnings'].append(f"Dataset has high missing data rate: {missing_percentage:.1f}%")
        
        # Check for columns with all missing data
        completely_missing = data.columns[data.isnull().all()].tolist()
        if completely_missing:
            results['errors'].append(f"Columns with all missing values: {completely_missing}")
        
        # Check for columns with very high missing rates
        for col in data.columns:
            col_missing_rate = (data[col].isnull().sum() / len(data)) * 100
            if col_missing_rate > 80:
                results['warnings'].append(f"Column '{col}' has {col_missing_rate:.1f}% missing data")
    
    def _validate_consistency(self, data: pd.DataFrame, results: Dict[str, Any]):
        """Validate data consistency"""
        
        # Check for completely duplicate rows
        duplicate_rows = data.duplicated().sum()
        if duplicate_rows > 0:
            duplicate_percentage = (duplicate_rows / len(data)) * 100
            if duplicate_percentage > 10:
                results['warnings'].append(f"Dataset has {duplicate_rows} duplicate rows ({duplicate_percentage:.1f}%)")
            else:
                results['warnings'].append(f"Dataset has {duplicate_rows} duplicate rows")
        
        # Check for suspicious patterns in categorical data
        for col in data.select_dtypes(include=['object']).columns:
            value_counts = data[col].value_counts()
            
            # Check if one value dominates (>95% of data)
            if len(value_counts) > 0:
                top_value_percentage = (value_counts.iloc[0] / len(data)) * 100
                if top_value_percentage > 95:
                    results['warnings'].append(f"Column '{col}' is dominated by one value ({top_value_percentage:.1f}%)")
        
        # Check for suspiciously uniform numeric distributions
        for col in data.select_dtypes(include=[np.number]).columns:
            if data[col].nunique() == 1:
                results['warnings'].append(f"Column '{col}' has only one unique value")
    
    def _validate_privacy_concerns(self, data: pd.DataFrame, results: Dict[str, Any]):
        """Validate potential privacy and PII concerns"""
        
        # Check for potential identifier columns
        potential_id_columns = []
        
        for col in data.columns:
            col_lower = col.lower()
            
            # Check column names for ID indicators
            id_indicators = ['id', 'identifier', 'key', 'number', 'ssn', 'social', 'license', 'passport', 'account']
            if any(indicator in col_lower for indicator in id_indicators):
                potential_id_columns.append(col)
            
            # Check for high cardinality (potential unique identifiers)
            if data[col].nunique() == len(data) and len(data) > 10:
                potential_id_columns.append(col)
                results['warnings'].append(f"Column '{col}' appears to be a unique identifier")
        
        # Check for potential PII
        pii_indicators = {
            'name': ['name', 'firstname', 'lastname', 'fullname'],
            'email': ['email', 'mail'],
            'phone': ['phone', 'mobile', 'telephone'],
            'address': ['address', 'street', 'city', 'zip', 'postal'],
            'birth': ['birth', 'dob', 'birthday'],
            'ssn': ['ssn', 'social', 'security']
        }
        
        for pii_type, indicators in pii_indicators.items():
            for col in data.columns:
                if any(indicator in col.lower() for indicator in indicators):
                    results['warnings'].append(f"Column '{col}' may contain {pii_type.upper()} (PII concern)")
        
        # Check for potential quasi-identifiers
        quasi_id_indicators = ['age', 'gender', 'zip', 'postal', 'education', 'occupation', 'income']
        potential_qis = []
        
        for col in data.columns:
            if any(indicator in col.lower() for indicator in quasi_id_indicators):
                potential_qis.append(col)
        
        if potential_qis:
            results['recommendations'].append(f"Consider these columns as quasi-identifiers: {potential_qis}")
    
    def _looks_like_date(self, value: str) -> bool:
        """Check if a string value looks like a date"""
        for pattern in self.date_patterns:
            if re.match(pattern, value):
                return True
        return False
    
    def _generate_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive dataset statistics"""
        
        stats = {
            'shape': {
                'rows': len(data),
                'columns': len(data.columns)
            },
            'missing_data': {
                'total_missing_cells': data.isnull().sum().sum(),
                'missing_percentage': (data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100,
                'columns_with_missing': data.columns[data.isnull().any()].tolist()
            },
            'data_types': {
                'numeric_columns': len(data.select_dtypes(include=[np.number]).columns),
                'object_columns': len(data.select_dtypes(include=['object']).columns),
                'datetime_columns': len(data.select_dtypes(include=['datetime64']).columns)
            },
            'uniqueness': {},
            'memory_usage': {
                'total_mb': data.memory_usage(deep=True).sum() / (1024 * 1024)
            }
        }
        
        # Calculate uniqueness for each column
        for col in data.columns:
            unique_count = data[col].nunique()
            total_count = len(data) - data[col].isnull().sum()
            uniqueness_ratio = unique_count / total_count if total_count > 0 else 0
            
            stats['uniqueness'][col] = {
                'unique_values': unique_count,
                'uniqueness_ratio': uniqueness_ratio
            }
        
        return stats
    
    def validate_anonymization_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parameters for anonymization techniques
        
        Args:
            params: Dictionary of anonymization parameters
        
        Returns:
            Validation results
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Validate k-anonymity parameters
        if 'k' in params:
            k = params['k']
            if not isinstance(k, int) or k < 2:
                validation_results['errors'].append("K-anonymity parameter 'k' must be an integer >= 2")
            elif k > 100:
                validation_results['warnings'].append(f"K-anonymity parameter 'k' is very high ({k})")
        
        # Validate l-diversity parameters
        if 'l' in params:
            l = params['l']
            if not isinstance(l, int) or l < 2:
                validation_results['errors'].append("L-diversity parameter 'l' must be an integer >= 2")
        
        # Validate differential privacy parameters
        if 'epsilon' in params:
            epsilon = params['epsilon']
            if not isinstance(epsilon, (int, float)) or epsilon <= 0:
                validation_results['errors'].append("Differential privacy parameter 'epsilon' must be positive")
            elif epsilon > 10:
                validation_results['warnings'].append(f"Epsilon value is high ({epsilon}) - may provide weak privacy")
            elif epsilon < 0.1:
                validation_results['warnings'].append(f"Epsilon value is very low ({epsilon}) - may severely impact utility")
        
        # Validate t-closeness parameters
        if 't' in params:
            t = params['t']
            if not isinstance(t, (int, float)) or t <= 0 or t > 1:
                validation_results['errors'].append("T-closeness parameter 't' must be between 0 and 1")
        
        # Set overall validity
        if validation_results['errors']:
            validation_results['is_valid'] = False
        
        return validation_results
    
    def validate_quasi_identifiers(self, data: pd.DataFrame, 
                                  quasi_identifiers: List[str]) -> Dict[str, Any]:
        """
        Validate quasi-identifier selection
        
        Args:
            data: Input DataFrame
            quasi_identifiers: List of column names selected as quasi-identifiers
        
        Returns:
            Validation results
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Check if quasi-identifiers exist in data
        missing_qis = [qi for qi in quasi_identifiers if qi not in data.columns]
        if missing_qis:
            validation_results['errors'].append(f"Quasi-identifiers not found in data: {missing_qis}")
        
        valid_qis = [qi for qi in quasi_identifiers if qi in data.columns]
        
        if not valid_qis:
            validation_results['errors'].append("No valid quasi-identifiers selected")
            validation_results['is_valid'] = False
            return validation_results
        
        # Check quasi-identifier properties
        for qi in valid_qis:
            uniqueness_ratio = data[qi].nunique() / len(data)
            
            if uniqueness_ratio > 0.9:
                validation_results['warnings'].append(f"Quasi-identifier '{qi}' has very high uniqueness ({uniqueness_ratio:.2f})")
            
            if data[qi].isnull().sum() / len(data) > 0.5:
                validation_results['warnings'].append(f"Quasi-identifier '{qi}' has high missing data rate")
        
        # Check for too many quasi-identifiers
        if len(valid_qis) > 10:
            validation_results['warnings'].append(f"Many quasi-identifiers selected ({len(valid_qis)}) - may increase risk")
        
        # Set overall validity
        if validation_results['errors']:
            validation_results['is_valid'] = False
        
        return validation_results
