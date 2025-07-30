import os
import json
import pickle
import gzip
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import pandas as pd
import logging

class FileOperations:
    """File operations utility for handling various file operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_export_formats = ['csv', 'xlsx', 'json', 'parquet', 'pickle']
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        directories = ['config', 'templates', 'exports', 'logs', 'temp']
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def save_configuration(self, config: Dict[str, Any], filename: str) -> bool:
        """
        Save configuration to JSON file
        
        Args:
            config: Configuration dictionary
            filename: Name of the configuration file
        
        Returns:
            Success status
        """
        try:
            config_path = Path('config') / f"{filename}.json"
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, default=str)
            
            self.logger.info(f"Configuration saved to {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def load_configuration(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Load configuration from JSON file
        
        Args:
            filename: Name of the configuration file
        
        Returns:
            Configuration dictionary or None if error
        """
        try:
            config_path = Path('config') / f"{filename}.json"
            
            if not config_path.exists():
                self.logger.warning(f"Configuration file not found: {config_path}")
                return None
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.logger.info(f"Configuration loaded from {config_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            return None
    
    def list_configurations(self) -> List[str]:
        """
        List available configuration files
        
        Returns:
            List of configuration file names (without extension)
        """
        try:
            config_dir = Path('config')
            config_files = [f.stem for f in config_dir.glob('*.json')]
            return sorted(config_files)
            
        except Exception as e:
            self.logger.error(f"Error listing configurations: {str(e)}")
            return []
    
    def export_data(self, data: pd.DataFrame, filename: str, 
                   file_format: str = 'csv', compress: bool = False) -> str:
        """
        Export DataFrame to various formats
        
        Args:
            data: DataFrame to export
            filename: Output filename (without extension)
            file_format: Export format
            compress: Whether to compress the output
        
        Returns:
            Path to exported file
        """
        try:
            if file_format not in self.supported_export_formats:
                raise ValueError(f"Unsupported export format: {file_format}")
            
            exports_dir = Path('exports')
            exports_dir.mkdir(exist_ok=True)
            
            # Generate full filename
            output_path = exports_dir / f"{filename}.{file_format}"
            
            # Export based on format
            if file_format == 'csv':
                data.to_csv(output_path, index=False)
            elif file_format == 'xlsx':
                data.to_excel(output_path, index=False)
            elif file_format == 'json':
                data.to_json(output_path, orient='records', indent=2)
            elif file_format == 'parquet':
                data.to_parquet(output_path, index=False)
            elif file_format == 'pickle':
                data.to_pickle(output_path)
            
            # Compress if requested
            if compress:
                compressed_path = f"{output_path}.gz"
                with open(output_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove uncompressed file
                os.remove(output_path)
                output_path = compressed_path
            
            self.logger.info(f"Data exported to {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error exporting data: {str(e)}")
            raise
    
    def save_results(self, results: Dict[str, Any], result_type: str, 
                    filename: str = None) -> str:
        """
        Save analysis results to file
        
        Args:
            results: Results dictionary
            result_type: Type of results (risk, utility, etc.)
            filename: Optional custom filename
        
        Returns:
            Path to saved file
        """
        try:
            if filename is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{result_type}_results_{timestamp}"
            
            results_dir = Path('exports') / 'results'
            results_dir.mkdir(exist_ok=True)
            
            output_path = results_dir / f"{filename}.json"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            
            self.logger.info(f"Results saved to {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")
            raise
    
    def load_results(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Load analysis results from file
        
        Args:
            filename: Name of results file
        
        Returns:
            Results dictionary or None if error
        """
        try:
            results_dir = Path('exports') / 'results'
            file_path = results_dir / f"{filename}.json"
            
            if not file_path.exists():
                # Try with full path
                file_path = Path(filename)
                if not file_path.exists():
                    self.logger.warning(f"Results file not found: {filename}")
                    return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            self.logger.info(f"Results loaded from {file_path}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error loading results: {str(e)}")
            return None
    
    def backup_data(self, data: pd.DataFrame, backup_name: str = None) -> str:
        """
        Create backup of original data
        
        Args:
            data: DataFrame to backup
            backup_name: Optional backup name
        
        Returns:
            Path to backup file
        """
        try:
            if backup_name is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"data_backup_{timestamp}"
            
            backups_dir = Path('exports') / 'backups'
            backups_dir.mkdir(exist_ok=True)
            
            backup_path = backups_dir / f"{backup_name}.parquet"
            
            data.to_parquet(backup_path, index=False)
            
            self.logger.info(f"Data backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {str(e)}")
            raise
    
    def restore_backup(self, backup_path: str) -> Optional[pd.DataFrame]:
        """
        Restore data from backup
        
        Args:
            backup_path: Path to backup file
        
        Returns:
            Restored DataFrame or None if error
        """
        try:
            backup_file = Path(backup_path)
            
            if not backup_file.exists():
                self.logger.warning(f"Backup file not found: {backup_path}")
                return None
            
            data = pd.read_parquet(backup_file)
            
            self.logger.info(f"Data restored from backup: {backup_path}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error restoring backup: {str(e)}")
            return None
    
    def clean_temp_files(self, max_age_hours: int = 24):
        """
        Clean temporary files older than specified age
        
        Args:
            max_age_hours: Maximum age of files to keep (in hours)
        """
        try:
            import time
            
            temp_dir = Path('temp')
            if not temp_dir.exists():
                return
            
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            cleaned_count = 0
            
            for file_path in temp_dir.rglob('*'):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        cleaned_count += 1
            
            self.logger.info(f"Cleaned {cleaned_count} temporary files")
            
        except Exception as e:
            self.logger.error(f"Error cleaning temp files: {str(e)}")
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get information about a file
        
        Args:
            file_path: Path to the file
        
        Returns:
            Dictionary containing file information
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {'exists': False}
            
            stat = file_path.stat()
            
            info = {
                'exists': True,
                'name': file_path.name,
                'size_bytes': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'extension': file_path.suffix.lower(),
                'is_file': file_path.is_file(),
                'is_directory': file_path.is_dir()
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting file info: {str(e)}")
            return {'exists': False, 'error': str(e)}
    
    def create_project_structure(self):
        """Create complete project directory structure"""
        directories = [
            'config',
            'templates',
            'exports/results',
            'exports/backups',
            'exports/reports',
            'logs',
            'temp',
            'data/samples',
            'data/processed'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Project directory structure created")
    
    def get_disk_usage(self) -> Dict[str, float]:
        """
        Get disk usage for project directories
        
        Returns:
            Dictionary with disk usage in MB for each directory
        """
        try:
            usage = {}
            
            for directory in ['config', 'exports', 'logs', 'temp']:
                dir_path = Path(directory)
                if dir_path.exists():
                    total_size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
                    usage[directory] = round(total_size / (1024 * 1024), 2)  # Convert to MB
                else:
                    usage[directory] = 0.0
            
            return usage
            
        except Exception as e:
            self.logger.error(f"Error calculating disk usage: {str(e)}")
            return {}
