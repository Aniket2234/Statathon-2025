import pandas as pd
import numpy as np
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Union
import io
import chardet
import openpyxl
from pathlib import Path
import logging

class DataHandler:
    """Data handling module for loading, validating, and repairing datasets"""
    
    def __init__(self):
        self.supported_formats = ['csv', 'xlsx', 'xls', 'json', 'xml', 'parquet', 'tsv']
        self.chunk_size = 10000
        self.max_file_size = 100 * 1024 * 1024  # 100MB default
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_file(self, filename: str) -> pd.DataFrame:
        """
        Load data file from filesystem path
        
        Args:
            filename: Path to the file
            
        Returns:
            Loaded pandas DataFrame
        """
        try:
            with open(filename, 'rb') as f:
                file_type = Path(filename).suffix.lower()[1:]
                return self.load_data(f, file_type)
        except Exception as e:
            self.logger.error(f"Error loading file {filename}: {str(e)}")
            raise
    
    def load_data(self, file_obj, file_type: Optional[str] = None) -> pd.DataFrame:
        """
        Load data from various file formats with error handling
        
        Args:
            file_obj: File object or path
            file_type: File type override
        
        Returns:
            Loaded pandas DataFrame
        """
        try:
            # Detect file type if not provided
            if file_type is None:
                if hasattr(file_obj, 'name'):
                    file_type = Path(file_obj.name).suffix.lower()[1:]
                else:
                    raise ValueError("Cannot determine file type")
            
            file_type = file_type.lower()
            
            if file_type not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_type}")
            
            # Load based on file type
            if file_type == 'csv':
                return self._load_csv(file_obj)
            elif file_type in ['xlsx', 'xls']:
                return self._load_excel(file_obj)
            elif file_type == 'json':
                return self._load_json(file_obj)
            elif file_type == 'xml':
                return self._load_xml(file_obj)
            elif file_type == 'parquet':
                return self._load_parquet(file_obj)
            elif file_type == 'tsv':
                return self._load_tsv(file_obj)
            else:
                raise ValueError(f"Loader not implemented for {file_type}")
                
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise
    
    def _load_csv(self, file_obj) -> pd.DataFrame:
        """Load CSV file with encoding detection"""
        try:
            # Read raw bytes for encoding detection
            if hasattr(file_obj, 'read'):
                raw_data = file_obj.read()
                if isinstance(raw_data, str):
                    # Already decoded string
                    file_obj.seek(0)
                    return pd.read_csv(file_obj)
                else:
                    # Detect encoding
                    encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
                    
                    # Convert to string and create StringIO
                    content = raw_data.decode(encoding)
                    return pd.read_csv(io.StringIO(content))
            else:
                # File path
                return pd.read_csv(file_obj)
                
        except UnicodeDecodeError:
            # Fallback encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    if hasattr(file_obj, 'seek'):
                        file_obj.seek(0)
                    return pd.read_csv(file_obj, encoding=encoding)
                except:
                    continue
            raise ValueError("Unable to decode CSV file with any standard encoding")
        
        except pd.errors.EmptyDataError:
            return pd.DataFrame()
        
        except Exception as e:
            # Try different separators
            separators = [',', ';', '\t', '|']
            for sep in separators:
                try:
                    if hasattr(file_obj, 'seek'):
                        file_obj.seek(0)
                    return pd.read_csv(file_obj, sep=sep)
                except:
                    continue
            raise ValueError(f"Unable to parse CSV file: {str(e)}")
    
    def _load_excel(self, file_obj) -> pd.DataFrame:
        """Load Excel file with sheet detection"""
        try:
            # Read all sheets and combine or use first sheet
            excel_file = pd.ExcelFile(file_obj)
            
            if len(excel_file.sheet_names) == 1:
                return pd.read_excel(file_obj, sheet_name=excel_file.sheet_names[0])
            else:
                # Use first sheet or largest sheet
                sheet_data = {}
                for sheet in excel_file.sheet_names[:3]:  # Limit to first 3 sheets
                    try:
                        df = pd.read_excel(file_obj, sheet_name=sheet)
                        if not df.empty:
                            sheet_data[sheet] = df
                    except:
                        continue
                
                if sheet_data:
                    # Return largest sheet
                    largest_sheet = max(sheet_data.keys(), key=lambda x: len(sheet_data[x]))
                    return sheet_data[largest_sheet]
                else:
                    return pd.DataFrame()
                    
        except Exception as e:
            raise ValueError(f"Unable to parse Excel file: {str(e)}")
    
    def _load_json(self, file_obj) -> pd.DataFrame:
        """Load JSON file with structure detection"""
        try:
            if hasattr(file_obj, 'read'):
                content = file_obj.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                data = json.loads(content)
            else:
                with open(file_obj, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                # Try to find tabular data in the dict
                for key, value in data.items():
                    if isinstance(value, list) and len(value) > 0:
                        if isinstance(value[0], dict):
                            return pd.DataFrame(value)
                
                # If no tabular data found, flatten the dict
                return pd.json_normalize(data)
            else:
                # Single value, create single-row DataFrame
                return pd.DataFrame([data])
                
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unable to parse JSON file: {str(e)}")
    
    def _load_xml(self, file_obj) -> pd.DataFrame:
        """Load XML file with structure detection"""
        try:
            if hasattr(file_obj, 'read'):
                content = file_obj.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                root = ET.fromstring(content)
            else:
                tree = ET.parse(file_obj)
                root = tree.getroot()
            
            # Convert XML to list of dictionaries
            records = []
            
            # Try to find repeating elements (common in data XML)
            children = list(root)
            if children:
                # Check if children have similar structure
                first_child_tags = set(child.tag for child in children[0])
                
                for child in children:
                    record = {}
                    self._xml_to_dict(child, record)
                    records.append(record)
            else:
                # Single record
                record = {}
                self._xml_to_dict(root, record)
                records.append(record)
            
            return pd.DataFrame(records)
            
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unable to parse XML file: {str(e)}")
    
    def _xml_to_dict(self, element, record: dict, prefix: str = ""):
        """Convert XML element to dictionary"""
        tag = element.tag
        if prefix:
            tag = f"{prefix}_{tag}"
        
        if element.text and element.text.strip():
            record[tag] = element.text.strip()
        
        # Handle attributes
        for attr, value in element.attrib.items():
            record[f"{tag}_{attr}"] = value
        
        # Handle children
        for child in element:
            self._xml_to_dict(child, record, tag)
    
    def _load_parquet(self, file_obj) -> pd.DataFrame:
        """Load Parquet file"""
        try:
            return pd.read_parquet(file_obj)
        except Exception as e:
            raise ValueError(f"Unable to parse Parquet file: {str(e)}")
    
    def _load_tsv(self, file_obj) -> pd.DataFrame:
        """Load TSV (Tab-Separated Values) file"""
        try:
            return pd.read_csv(file_obj, sep='\t')
        except Exception as e:
            raise ValueError(f"Unable to parse TSV file: {str(e)}")
    
    def assess_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Assess data quality and identify issues
        
        Args:
            data: Input DataFrame
        
        Returns:
            Dictionary containing quality assessment results
        """
        quality_report = {
            'overall_quality': 0.0,
            'completeness': 0.0,
            'consistency': 0.0,
            'validity': 0.0,
            'issues': [],
            'recommendations': []
        }
        
        if data.empty:
            quality_report['issues'].append("Dataset is empty")
            return quality_report
        
        total_cells = len(data) * len(data.columns)
        
        # Completeness: Check for missing values
        missing_cells = data.isnull().sum().sum()
        completeness = 1 - (missing_cells / total_cells) if total_cells > 0 else 0
        quality_report['completeness'] = completeness * 100
        
        if missing_cells > 0:
            missing_percentage = (missing_cells / total_cells) * 100
            quality_report['issues'].append(f"Missing values: {missing_cells} cells ({missing_percentage:.1f}%)")
            
            if missing_percentage > 50:
                quality_report['recommendations'].append("High missing data rate - consider data collection review")
            elif missing_percentage > 20:
                quality_report['recommendations'].append("Significant missing data - apply imputation techniques")
        
        # Consistency: Check for data type consistency
        consistency_score = 0.0
        consistency_issues = 0
        
        for col in data.columns:
            series = data[col].dropna()
            if len(series) == 0:
                continue
            
            # Check for mixed data types in object columns
            if series.dtype == 'object':
                # Check if numeric values are stored as strings
                numeric_like = 0
                for value in series.head(100):  # Sample first 100 values
                    try:
                        float(str(value))
                        numeric_like += 1
                    except:
                        pass
                
                if numeric_like > len(series) * 0.8:  # >80% numeric-like
                    quality_report['issues'].append(f"Column '{col}' contains numeric data stored as text")
                    consistency_issues += 1
            
            # Check for inconsistent date formats
            if series.dtype == 'object':
                date_patterns = 0
                for value in series.head(50):
                    if self._looks_like_date(str(value)):
                        date_patterns += 1
                
                if date_patterns > len(series) * 0.5:
                    quality_report['issues'].append(f"Column '{col}' may contain inconsistent date formats")
                    consistency_issues += 1
        
        consistency_score = max(0, 1 - (consistency_issues / len(data.columns)))
        quality_report['consistency'] = consistency_score * 100
        
        # Validity: Check for data range and format validity
        validity_score = 0.0
        validity_issues = 0
        
        for col in data.columns:
            series = data[col].dropna()
            if len(series) == 0:
                continue
            
            # Check for negative values in potentially positive-only columns
            if series.dtype in ['int64', 'float64']:
                if 'age' in col.lower() or 'count' in col.lower() or 'quantity' in col.lower():
                    negative_count = (series < 0).sum()
                    if negative_count > 0:
                        quality_report['issues'].append(f"Column '{col}' has {negative_count} negative values")
                        validity_issues += 1
                
                # Check for extreme outliers
                q1 = series.quantile(0.25)
                q3 = series.quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 3 * iqr
                upper_bound = q3 + 3 * iqr
                
                outliers = ((series < lower_bound) | (series > upper_bound)).sum()
                if outliers > len(series) * 0.1:  # >10% outliers
                    quality_report['issues'].append(f"Column '{col}' has {outliers} potential outliers")
        
        validity_score = max(0, 1 - (validity_issues / len(data.columns)))
        quality_report['validity'] = validity_score * 100
        
        # Calculate overall quality score
        quality_report['overall_quality'] = np.mean([
            quality_report['completeness'],
            quality_report['consistency'],
            quality_report['validity']
        ])
        
        return quality_report
    
    def _looks_like_date(self, value: str) -> bool:
        """Check if a string value looks like a date"""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # M/D/YY or MM/DD/YYYY
        ]
        
        import re
        for pattern in date_patterns:
            if re.match(pattern, value):
                return True
        return False
    
    def repair_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply automatic data repair techniques
        
        Args:
            data: Input DataFrame with quality issues
        
        Returns:
            Repaired DataFrame
        """
        repaired_data = data.copy()
        
        self.logger.info("Starting data repair process...")
        
        # Repair 1: Handle missing values
        for col in repaired_data.columns:
            if repaired_data[col].isnull().any():
                if repaired_data[col].dtype in ['int64', 'float64']:
                    # Fill numeric missing values with median
                    median_val = repaired_data[col].median()
                    repaired_data[col].fillna(median_val, inplace=True)
                else:
                    # Fill categorical missing values with mode
                    if not repaired_data[col].mode().empty:
                        mode_val = repaired_data[col].mode()[0]
                        repaired_data[col].fillna(mode_val, inplace=True)
                    else:
                        repaired_data[col].fillna("Unknown", inplace=True)
        
        # Repair 2: Convert numeric strings to proper numeric types
        for col in repaired_data.columns:
            if repaired_data[col].dtype == 'object':
                # Try to convert to numeric
                try:
                    # Remove common non-numeric characters
                    cleaned_series = repaired_data[col].astype(str).str.replace('[$,]', '', regex=True)
                    numeric_series = pd.to_numeric(cleaned_series, errors='coerce')
                    
                    # If >80% of values can be converted, make the conversion
                    non_null_count = numeric_series.notna().sum()
                    if non_null_count > len(repaired_data) * 0.8:
                        repaired_data[col] = numeric_series
                        # Fill remaining NaN with median
                        repaired_data[col].fillna(repaired_data[col].median(), inplace=True)
                except:
                    pass
        
        # Repair 3: Standardize text data
        for col in repaired_data.columns:
            if repaired_data[col].dtype == 'object':
                # Remove leading/trailing whitespace
                repaired_data[col] = repaired_data[col].astype(str).str.strip()
                
                # Standardize case for categorical-looking data
                unique_values = repaired_data[col].nunique()
                if unique_values < len(repaired_data) * 0.1:  # <10% unique values (likely categorical)
                    repaired_data[col] = repaired_data[col].str.title()
        
        # Repair 4: Handle date columns (especially date_of_birth)
        for col in repaired_data.columns:
            if repaired_data[col].dtype == 'object' and ('date' in col.lower() or 'birth' in col.lower()):
                # Try to parse as dates
                try:
                    date_series = pd.to_datetime(repaired_data[col], errors='coerce', infer_datetime_format=True)
                    if date_series.notna().sum() > len(repaired_data) * 0.8:
                        repaired_data[col] = date_series
                except:
                    pass
        
        # Repair 5: Remove completely duplicate rows
        before_dedup = len(repaired_data)
        repaired_data = repaired_data.drop_duplicates()
        after_dedup = len(repaired_data)
        
        if before_dedup != after_dedup:
            self.logger.info(f"Removed {before_dedup - after_dedup} duplicate rows")
        
        # Repair 6: Handle extreme outliers in numeric columns
        for col in repaired_data.columns:
            if repaired_data[col].dtype in ['int64', 'float64']:
                q1 = repaired_data[col].quantile(0.25)
                q3 = repaired_data[col].quantile(0.75)
                iqr = q3 - q1
                
                # Cap extreme outliers (beyond 3*IQR)
                lower_bound = q1 - 3 * iqr
                upper_bound = q3 + 3 * iqr
                
                outlier_count = ((repaired_data[col] < lower_bound) | (repaired_data[col] > upper_bound)).sum()
                if outlier_count > 0:
                    repaired_data[col] = repaired_data[col].clip(lower=lower_bound, upper=upper_bound)
                    self.logger.info(f"Capped {outlier_count} outliers in column '{col}'")
        
        self.logger.info("Data repair process completed")
        return repaired_data
    
    def apply_fixes(self, data: pd.DataFrame, issues: List[str]) -> pd.DataFrame:
        """
        Apply comprehensive automatic fixes for any dataset issues including PyArrow compatibility
        
        Args:
            data: Input DataFrame
            issues: List of specific issues to fix
        
        Returns:
            Fixed DataFrame with full compatibility
        """
        fixed_data = data.copy()
        
        # Apply PyArrow compatibility fixes first
        fixed_data = self._fix_pyarrow_compatibility(fixed_data)
        
        # Apply specific issue fixes
        for issue in issues:
            if "Missing values" in issue:
                fixed_data = self._fix_missing_values(fixed_data)
            elif "negative values" in issue:
                fixed_data = self._fix_negative_values(fixed_data, issue)
            elif "numeric data stored as text" in issue:
                fixed_data = self._fix_text_numeric(fixed_data, issue)
            elif "date formats" in issue:
                fixed_data = self._fix_date_formats(fixed_data, issue)
        
        # Apply comprehensive data cleaning
        fixed_data = self._apply_comprehensive_fixes(fixed_data)
        
        return fixed_data
    
    def _fix_pyarrow_compatibility(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Fix PyArrow compatibility issues that cause Streamlit display problems
        """
        fixed_data = data.copy()
        
        for col in fixed_data.columns:
            series = fixed_data[col]
            
            # Handle nullable integer types that cause PyArrow issues
            if hasattr(series.dtype, 'name') and 'Int' in str(series.dtype):
                try:
                    # Convert to standard numpy types
                    if series.dtype.name.startswith('Int'):
                        fixed_data[col] = series.astype('int64', errors='ignore')
                    elif series.dtype.name.startswith('Float'):
                        fixed_data[col] = series.astype('float64', errors='ignore')
                except:
                    # Convert to object if conversion fails
                    fixed_data[col] = series.astype('object')
            
            # Handle mixed types in object columns
            if series.dtype == 'object':
                try:
                    # Try to infer and convert to appropriate type
                    cleaned_series = self._clean_mixed_types(series)
                    fixed_data[col] = cleaned_series
                except:
                    # Keep as string if all else fails
                    fixed_data[col] = series.astype(str)
            
            # Handle datetime issues
            if 'datetime' in str(series.dtype):
                try:
                    # Ensure timezone-naive datetime for PyArrow compatibility
                    if hasattr(series.dt, 'tz') and series.dt.tz is not None:
                        fixed_data[col] = series.dt.tz_localize(None)
                except:
                    fixed_data[col] = series.astype(str)
        
        return fixed_data
    
    def _clean_mixed_types(self, series: pd.Series) -> pd.Series:
        """Clean series with mixed data types"""
        if series.empty:
            return series
        
        # Try numeric conversion first
        try:
            # Remove common non-numeric characters
            cleaned_str = series.astype(str).str.replace(r'[^\d\.\-\+]', '', regex=True)
            numeric_series = pd.to_numeric(cleaned_str, errors='coerce')
            
            # If >70% can be converted to numeric, use numeric
            valid_numeric = numeric_series.notna().sum()
            if valid_numeric > len(series) * 0.7:
                # Fill NaN with 0 for numeric columns
                return numeric_series.fillna(0)
        except:
            pass
        
        # Try datetime conversion
        try:
            datetime_series = pd.to_datetime(series, errors='coerce', infer_datetime_format=True)
            valid_datetime = datetime_series.notna().sum()
            if valid_datetime > len(series) * 0.7:
                return datetime_series
        except:
            pass
        
        # Clean as string
        return series.astype(str).str.strip()
    
    def _apply_comprehensive_fixes(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply comprehensive automatic fixes for any dataset
        """
        fixed_data = data.copy()
        
        # Fix 1: Clean column names
        fixed_data.columns = [self._clean_column_name(col) for col in fixed_data.columns]
        
        # Fix 2: Handle duplicate column names
        fixed_data.columns = self._fix_duplicate_columns(fixed_data.columns)
        
        # Fix 3: Remove empty rows/columns
        fixed_data = fixed_data.dropna(how='all')  # Remove completely empty rows
        fixed_data = fixed_data.loc[:, fixed_data.notna().any()]  # Remove completely empty columns
        
        # Fix 4: Standardize data types
        for col in fixed_data.columns:
            series = fixed_data[col]
            
            # Handle boolean-like columns
            if series.dtype == 'object':
                unique_vals = series.dropna().unique()
                if len(unique_vals) <= 10:  # Small number of unique values
                    bool_vals = {'true', 'false', 'yes', 'no', '1', '0', 'y', 'n'}
                    if all(str(val).lower() in bool_vals for val in unique_vals):
                        bool_map = {'true': True, 'false': False, 'yes': True, 'no': False, 
                                   '1': True, '0': False, 'y': True, 'n': False}
                        fixed_data[col] = series.map(lambda x: bool_map.get(str(x).lower(), x))
        
        # Fix 5: Handle special characters and encoding issues
        for col in fixed_data.columns:
            if fixed_data[col].dtype == 'object':
                try:
                    # Remove non-printable characters
                    fixed_data[col] = fixed_data[col].astype(str).str.replace(r'[^\x20-\x7E]', '', regex=True)
                except:
                    pass
        
        # Fix 6: Ensure all data is JSON serializable for compatibility
        for col in fixed_data.columns:
            series = fixed_data[col]
            if series.dtype == 'object':
                # Convert complex objects to strings
                fixed_data[col] = series.apply(lambda x: str(x) if not pd.isna(x) else x)
        
        return fixed_data
    
    def _clean_column_name(self, col_name: str) -> str:
        """Clean column names for better compatibility"""
        import re
        # Convert to string and clean
        cleaned = str(col_name).strip()
        # Replace special characters with underscores
        cleaned = re.sub(r'[^\w\s]', '_', cleaned)
        # Replace spaces with underscores
        cleaned = re.sub(r'\s+', '_', cleaned)
        # Remove multiple underscores
        cleaned = re.sub(r'_+', '_', cleaned)
        # Remove leading/trailing underscores
        cleaned = cleaned.strip('_')
        return cleaned if cleaned else 'column'
    
    def _fix_duplicate_columns(self, columns):
        """Fix duplicate column names"""
        seen = {}
        new_columns = []
        
        for col in columns:
            if col in seen:
                seen[col] += 1
                new_columns.append(f"{col}_{seen[col]}")
            else:
                seen[col] = 0
                new_columns.append(col)
        
        return new_columns
    
    def _fix_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """Fix missing values using appropriate imputation"""
        for col in data.columns:
            if data[col].isnull().any():
                if data[col].dtype in ['int64', 'float64']:
                    median_val = data[col].median()
                    if not pd.isna(median_val):
                        data[col].fillna(median_val, inplace=True)
                else:
                    if not data[col].mode().empty:
                        data[col].fillna(data[col].mode()[0], inplace=True)
        return data
    
    def _fix_negative_values(self, data: pd.DataFrame, issue: str) -> pd.DataFrame:
        """Fix negative values in appropriate columns"""
        # Extract column name from issue description
        import re
        match = re.search(r"Column '([^']+)'", issue)
        if match:
            col_name = match.group(1)
            if col_name in data.columns:
                data[col_name] = data[col_name].abs()
        return data
    
    def _fix_text_numeric(self, data: pd.DataFrame, issue: str) -> pd.DataFrame:
        """Convert text to numeric where appropriate"""
        import re
        match = re.search(r"Column '([^']+)'", issue)
        if match:
            col_name = match.group(1)
            if col_name in data.columns:
                try:
                    cleaned = data[col_name].astype(str).str.replace('[$,]', '', regex=True)
                    numeric_series = pd.to_numeric(cleaned, errors='coerce')
                    median_val = numeric_series.median()
                    if not pd.isna(median_val):
                        data[col_name] = numeric_series.fillna(median_val)
                except:
                    pass
        return data
    
    def _fix_date_formats(self, data: pd.DataFrame, issue: str) -> pd.DataFrame:
        """Standardize date formats"""
        import re
        match = re.search(r"Column '([^']+)'", issue)
        if match:
            col_name = match.group(1)
            if col_name in data.columns:
                try:
                    data[col_name] = pd.to_datetime(data[col_name], errors='coerce', infer_datetime_format=True)
                except:
                    pass
        return data
