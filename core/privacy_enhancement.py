import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder, StandardScaler
import random
from collections import defaultdict, Counter
import itertools

class PrivacyEnhancement:
    """Privacy enhancement module implementing various anonymization techniques"""
    
    def __init__(self):
        self.random_state = 42
        np.random.seed(self.random_state)
        random.seed(self.random_state)
    
    def apply_k_anonymity(self, data: pd.DataFrame, k: int, 
                         quasi_identifiers: List[str], method: str = "Global Recoding",
                         suppression_limit: float = 0.1) -> pd.DataFrame:
        """
        Apply k-anonymity to the dataset
        
        Args:
            data: Input dataset
            k: K-anonymity parameter
            quasi_identifiers: List of quasi-identifier columns
            method: Anonymization method
            suppression_limit: Maximum fraction of records to suppress
        
        Returns:
            Anonymized dataset
        """
        if not quasi_identifiers:
            return data.copy()
        
        result_data = data.copy()
        
        if method == "Global Recoding":
            result_data = self._apply_global_recoding(result_data, k, quasi_identifiers)
        elif method == "Local Recoding":
            result_data = self._apply_local_recoding(result_data, k, quasi_identifiers)
        elif method == "Clustering":
            result_data = self._apply_clustering_anonymization(result_data, k, quasi_identifiers)
        
        # Apply suppression if needed
        result_data = self._apply_suppression(result_data, k, quasi_identifiers, suppression_limit)
        
        return result_data
    
    def apply_l_diversity(self, data: pd.DataFrame, l: int, 
                         quasi_identifiers: List[str], sensitive_attribute: str,
                         method: str = "Distinct L-Diversity") -> pd.DataFrame:
        """
        Apply l-diversity to the dataset
        
        Args:
            data: Input dataset
            l: L-diversity parameter
            quasi_identifiers: List of quasi-identifier columns
            sensitive_attribute: Sensitive attribute column
            method: L-diversity method
        
        Returns:
            Anonymized dataset
        """
        if not quasi_identifiers or sensitive_attribute not in data.columns:
            return data.copy()
        
        result_data = data.copy()
        
        # First apply basic k-anonymity with k=l
        result_data = self._apply_global_recoding(result_data, l, quasi_identifiers)
        
        # Then ensure l-diversity
        if method == "Distinct L-Diversity":
            result_data = self._ensure_distinct_l_diversity(result_data, l, quasi_identifiers, sensitive_attribute)
        elif method == "Entropy L-Diversity":
            result_data = self._ensure_entropy_l_diversity(result_data, l, quasi_identifiers, sensitive_attribute)
        elif method == "Recursive L-Diversity":
            result_data = self._ensure_recursive_l_diversity(result_data, l, quasi_identifiers, sensitive_attribute)
        
        return result_data
    
    def apply_t_closeness(self, data: pd.DataFrame, t: float,
                         quasi_identifiers: List[str], sensitive_attribute: str,
                         distance_measure: str = "EMD") -> pd.DataFrame:
        """
        Apply t-closeness to the dataset
        
        Args:
            data: Input dataset
            t: T-closeness parameter
            quasi_identifiers: List of quasi-identifier columns
            sensitive_attribute: Sensitive attribute column
            distance_measure: Distance measure to use
        
        Returns:
            Anonymized dataset
        """
        if not quasi_identifiers or sensitive_attribute not in data.columns:
            return data.copy()
        
        result_data = data.copy()
        
        # Apply generalization to achieve t-closeness
        result_data = self._apply_t_closeness_generalization(
            result_data, t, quasi_identifiers, sensitive_attribute, distance_measure
        )
        
        return result_data
    
    def apply_differential_privacy(self, data: pd.DataFrame, epsilon: float,
                                  sensitivity: float = 1.0, mechanism: str = "Laplace",
                                  numeric_columns: List[str] = None) -> pd.DataFrame:
        """
        Apply differential privacy by adding calibrated noise
        
        Args:
            data: Input dataset
            epsilon: Privacy parameter (smaller = more private)
            sensitivity: Global sensitivity
            mechanism: Noise mechanism
            numeric_columns: Columns to add noise to
        
        Returns:
            Dataset with differential privacy applied
        """
        result_data = data.copy()
        
        if numeric_columns is None:
            numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in numeric_columns:
            if col in result_data.columns:
                if mechanism == "Laplace":
                    noise = np.random.laplace(0, sensitivity / epsilon, len(result_data))
                elif mechanism == "Gaussian":
                    # For Gaussian mechanism, need to account for delta
                    sigma = np.sqrt(2 * np.log(1.25)) * sensitivity / epsilon
                    noise = np.random.normal(0, sigma, len(result_data))
                else:
                    noise = np.random.laplace(0, sensitivity / epsilon, len(result_data))
                
                result_data[col] = result_data[col] + noise
        
        return result_data
    
    def generate_synthetic_data(self, data: pd.DataFrame, method: str = "Statistical",
                               sample_size: float = 1.0, preserve_correlations: bool = True,
                               preserve_distributions: bool = True) -> pd.DataFrame:
        """
        Generate synthetic data maintaining statistical properties
        
        Args:
            data: Input dataset
            method: Generation method
            sample_size: Size of synthetic dataset relative to original
            preserve_correlations: Whether to preserve correlations
            preserve_distributions: Whether to preserve distributions
        
        Returns:
            Synthetic dataset
        """
        n_samples = int(len(data) * sample_size)
        
        if method == "Statistical":
            return self._generate_statistical_synthetic(data, n_samples, preserve_correlations, preserve_distributions)
        elif method == "Copula":
            return self._generate_copula_synthetic(data, n_samples)
        elif method == "GAN-based":
            return self._generate_gan_synthetic(data, n_samples)
        else:
            return self._generate_statistical_synthetic(data, n_samples, preserve_correlations, preserve_distributions)
    
    def _apply_global_recoding(self, data: pd.DataFrame, k: int, 
                              quasi_identifiers: List[str]) -> pd.DataFrame:
        """Apply global recoding for k-anonymity"""
        result_data = data.copy()
        
        for qi in quasi_identifiers:
            if qi not in result_data.columns:
                continue
            
            # Determine generalization strategy based on data type
            if result_data[qi].dtype in ['int64', 'float64']:
                result_data[qi] = self._generalize_numeric(result_data[qi], k)
            else:
                result_data[qi] = self._generalize_categorical(result_data[qi], k)
        
        return result_data
    
    def _apply_local_recoding(self, data: pd.DataFrame, k: int,
                             quasi_identifiers: List[str]) -> pd.DataFrame:
        """Apply local recoding for k-anonymity"""
        result_data = data.copy()
        
        # Group records by quasi-identifiers
        grouped = result_data.groupby(quasi_identifiers)
        
        records_to_generalize = []
        for name, group in grouped:
            if len(group) < k:
                records_to_generalize.extend(group.index.tolist())
        
        # Apply generalization to violating records
        for idx in records_to_generalize:
            for qi in quasi_identifiers:
                if qi in result_data.columns:
                    if result_data[qi].dtype in ['int64', 'float64']:
                        # Generalize numeric values
                        original_value = result_data.loc[idx, qi]
                        generalized_value = self._generalize_single_numeric(original_value)
                        result_data.loc[idx, qi] = generalized_value
                    else:
                        # Generalize categorical values
                        result_data.loc[idx, qi] = "*"
        
        return result_data
    
    def _apply_clustering_anonymization(self, data: pd.DataFrame, k: int,
                                       quasi_identifiers: List[str]) -> pd.DataFrame:
        """Apply clustering-based anonymization"""
        result_data = data.copy()
        
        # Prepare data for clustering
        qi_data = result_data[quasi_identifiers].copy()
        
        # Encode categorical variables
        encoders = {}
        for col in qi_data.columns:
            if qi_data[col].dtype == 'object':
                encoders[col] = LabelEncoder()
                qi_data[col] = encoders[col].fit_transform(qi_data[col].astype(str))
        
        # Standardize numerical data
        scaler = StandardScaler()
        qi_scaled = scaler.fit_transform(qi_data)
        
        # Perform clustering
        n_clusters = max(1, len(data) // k)
        kmeans = KMeans(n_clusters=n_clusters, random_state=self.random_state)
        clusters = kmeans.fit_predict(qi_scaled)
        
        # Generalize within each cluster
        for cluster_id in range(n_clusters):
            cluster_indices = np.where(clusters == cluster_id)[0]
            if len(cluster_indices) >= k:
                continue
            
            # Generalize this cluster
            for idx in cluster_indices:
                for qi in quasi_identifiers:
                    if qi in result_data.columns:
                        if result_data[qi].dtype in ['int64', 'float64']:
                            cluster_values = result_data.loc[cluster_indices, qi]
                            result_data.loc[idx, qi] = cluster_values.mean()
                        else:
                            result_data.loc[idx, qi] = "*"
        
        return result_data
    
    def _apply_suppression(self, data: pd.DataFrame, k: int,
                          quasi_identifiers: List[str], suppression_limit: float) -> pd.DataFrame:
        """Apply suppression to records that still violate k-anonymity"""
        result_data = data.copy()
        
        # Identify violating records
        grouped = result_data.groupby(quasi_identifiers)
        violating_indices = []
        
        for name, group in grouped:
            if len(group) < k:
                violating_indices.extend(group.index.tolist())
        
        # Suppress up to the limit
        max_suppressions = int(len(data) * suppression_limit)
        if len(violating_indices) <= max_suppressions:
            result_data = result_data.drop(violating_indices)
        else:
            # Suppress the most violating records first (smallest groups)
            group_sizes = {}
            for name, group in grouped:
                for idx in group.index:
                    group_sizes[idx] = len(group)
            
            sorted_indices = sorted(violating_indices, key=lambda x: group_sizes[x])
            to_suppress = sorted_indices[:max_suppressions]
            result_data = result_data.drop(to_suppress)
        
        return result_data
    
    def _ensure_distinct_l_diversity(self, data: pd.DataFrame, l: int,
                                   quasi_identifiers: List[str], sensitive_attribute: str) -> pd.DataFrame:
        """Ensure distinct l-diversity"""
        result_data = data.copy()
        
        grouped = result_data.groupby(quasi_identifiers)
        
        for name, group in grouped:
            sensitive_values = group[sensitive_attribute].dropna()
            unique_values = sensitive_values.nunique()
            
            if unique_values < l:
                # Need to generalize or suppress
                # Simple approach: generalize quasi-identifiers
                group_indices = group.index.tolist()
                for qi in quasi_identifiers:
                    if qi in result_data.columns:
                        if result_data[qi].dtype in ['int64', 'float64']:
                            mean_val = result_data.loc[group_indices, qi].mean()
                            result_data.loc[group_indices, qi] = mean_val
                        else:
                            result_data.loc[group_indices, qi] = "*"
        
        return result_data
    
    def _ensure_entropy_l_diversity(self, data: pd.DataFrame, l: int,
                                   quasi_identifiers: List[str], sensitive_attribute: str) -> pd.DataFrame:
        """Ensure entropy l-diversity"""
        result_data = data.copy()
        
        grouped = result_data.groupby(quasi_identifiers)
        
        for name, group in grouped:
            sensitive_values = group[sensitive_attribute].dropna()
            
            if len(sensitive_values) == 0:
                continue
            
            # Calculate entropy
            value_counts = sensitive_values.value_counts()
            probabilities = value_counts / len(sensitive_values)
            entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
            
            required_entropy = np.log2(l)
            
            if entropy < required_entropy:
                # Apply generalization
                group_indices = group.index.tolist()
                for qi in quasi_identifiers:
                    if qi in result_data.columns:
                        if result_data[qi].dtype in ['int64', 'float64']:
                            mean_val = result_data.loc[group_indices, qi].mean()
                            result_data.loc[group_indices, qi] = mean_val
                        else:
                            result_data.loc[group_indices, qi] = "*"
        
        return result_data
    
    def _ensure_recursive_l_diversity(self, data: pd.DataFrame, l: int,
                                     quasi_identifiers: List[str], sensitive_attribute: str) -> pd.DataFrame:
        """Ensure recursive (c,l)-diversity"""
        # Simplified implementation of recursive l-diversity
        return self._ensure_distinct_l_diversity(data, l, quasi_identifiers, sensitive_attribute)
    
    def _apply_t_closeness_generalization(self, data: pd.DataFrame, t: float,
                                         quasi_identifiers: List[str], sensitive_attribute: str,
                                         distance_measure: str) -> pd.DataFrame:
        """Apply generalization to achieve t-closeness"""
        result_data = data.copy()
        
        # Calculate global distribution
        global_dist = result_data[sensitive_attribute].value_counts(normalize=True)
        
        grouped = result_data.groupby(quasi_identifiers)
        
        for name, group in grouped:
            local_dist = group[sensitive_attribute].value_counts(normalize=True)
            
            # Calculate distance between distributions
            distance = self._calculate_distribution_distance(global_dist, local_dist, distance_measure)
            
            if distance > t:
                # Apply generalization
                group_indices = group.index.tolist()
                for qi in quasi_identifiers:
                    if qi in result_data.columns:
                        if result_data[qi].dtype in ['int64', 'float64']:
                            mean_val = result_data.loc[group_indices, qi].mean()
                            result_data.loc[group_indices, qi] = mean_val
                        else:
                            result_data.loc[group_indices, qi] = "*"
        
        return result_data
    
    def _calculate_distribution_distance(self, global_dist: pd.Series, local_dist: pd.Series,
                                       distance_measure: str) -> float:
        """Calculate distance between two distributions"""
        if distance_measure == "EMD":
            # Simplified Earth Mover's Distance
            all_values = set(global_dist.index) | set(local_dist.index)
            distance = 0.0
            
            for value in all_values:
                global_prob = global_dist.get(value, 0)
                local_prob = local_dist.get(value, 0)
                distance += abs(global_prob - local_prob)
            
            return distance / 2  # Normalize
        else:
            # Hierarchical distance (simplified)
            return self._calculate_distribution_distance(global_dist, local_dist, "EMD")
    
    def _generalize_numeric(self, series: pd.Series, k: int) -> pd.Series:
        """Generalize numeric values"""
        # Create ranges based on quantiles
        n_bins = max(1, len(series) // k)
        bins = pd.qcut(series, q=n_bins, duplicates='drop')
        return bins.astype(str)
    
    def _generalize_categorical(self, series: pd.Series, k: int) -> pd.Series:
        """Generalize categorical values"""
        value_counts = series.value_counts()
        result = series.copy()
        
        # Replace infrequent values with "*"
        for value, count in value_counts.items():
            if count < k:
                result = result.replace(value, "*")
        
        return result
    
    def _generalize_single_numeric(self, value: float) -> str:
        """Generalize a single numeric value"""
        # Simple range generalization
        if pd.isna(value):
            return "*"
        
        # Create range around the value
        range_size = max(1, abs(value) * 0.1)  # 10% range
        lower = value - range_size
        upper = value + range_size
        
        return f"[{lower:.2f}-{upper:.2f}]"
    
    def _generate_statistical_synthetic(self, data: pd.DataFrame, n_samples: int,
                                       preserve_correlations: bool, preserve_distributions: bool) -> pd.DataFrame:
        """Generate synthetic data using statistical methods"""
        synthetic_data = pd.DataFrame()
        
        for col in data.columns:
            if data[col].dtype in ['int64', 'float64']:
                # Numeric column
                if preserve_distributions:
                    # Sample from empirical distribution
                    synthetic_data[col] = np.random.choice(data[col].dropna(), size=n_samples, replace=True)
                else:
                    # Sample from normal distribution with same mean/std
                    mean = data[col].mean()
                    std = data[col].std()
                    synthetic_data[col] = np.random.normal(mean, std, n_samples)
            else:
                # Categorical column
                value_counts = data[col].value_counts(normalize=True)
                synthetic_data[col] = np.random.choice(
                    value_counts.index, size=n_samples, replace=True, p=value_counts.values
                )
        
        # Simple correlation preservation (if requested)
        if preserve_correlations and len(data.select_dtypes(include=[np.number]).columns) > 1:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                # Calculate correlation matrix
                corr_matrix = data[numeric_cols].corr()
                
                # Apply correlation structure (simplified approach)
                for i, col1 in enumerate(numeric_cols):
                    for j, col2 in enumerate(numeric_cols):
                        if i < j and abs(corr_matrix.loc[col1, col2]) > 0.3:
                            # Add some correlation
                            correlation_factor = corr_matrix.loc[col1, col2] * 0.5
                            noise = np.random.normal(0, synthetic_data[col2].std() * 0.1, n_samples)
                            synthetic_data[col1] += synthetic_data[col2] * correlation_factor + noise
        
        return synthetic_data
    
    def _generate_copula_synthetic(self, data: pd.DataFrame, n_samples: int) -> pd.DataFrame:
        """Generate synthetic data using copula methods (simplified)"""
        # Simplified copula-based generation
        return self._generate_statistical_synthetic(data, n_samples, True, True)
    
    def _generate_gan_synthetic(self, data: pd.DataFrame, n_samples: int) -> pd.DataFrame:
        """Generate synthetic data using GAN-based methods (simplified)"""
        # Simplified GAN-based generation (would require actual GAN implementation)
        return self._generate_statistical_synthetic(data, n_samples, True, True)
