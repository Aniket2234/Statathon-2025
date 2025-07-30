import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats
from sklearn.metrics import mutual_info_score, adjusted_rand_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, r2_score
import warnings
warnings.filterwarnings('ignore')

class UtilityMeasurement:
    """Utility measurement module for evaluating data quality preservation"""
    
    def __init__(self):
        self.utility_thresholds = {
            'excellent': 0.9,
            'good': 0.7,
            'fair': 0.5,
            'poor': 0.3
        }
    
    def measure_utility(self, original_data: pd.DataFrame, processed_data: pd.DataFrame,
                       metrics: List[str] = None) -> Dict[str, Any]:
        """
        Measure utility preservation between original and processed datasets
        
        Args:
            original_data: Original dataset
            processed_data: Privacy-enhanced dataset
            metrics: List of utility metrics to compute
        
        Returns:
            Dictionary containing utility measurements
        """
        if metrics is None:
            metrics = ["Statistical Similarity", "Correlation Preservation", "Distribution Similarity"]
        
        results = {
            'metrics_computed': metrics,
            'dataset_sizes': {
                'original': len(original_data),
                'processed': len(processed_data)
            }
        }
        
        # Align datasets (in case of different sizes due to suppression)
        aligned_original, aligned_processed = self._align_datasets(original_data, processed_data)
        
        # Compute individual metrics
        if "Statistical Similarity" in metrics:
            results['statistical_similarity'] = self._measure_statistical_similarity(
                aligned_original, aligned_processed
            )
        
        if "Correlation Preservation" in metrics:
            results['correlation_preservation'] = self._measure_correlation_preservation(
                aligned_original, aligned_processed
            )
        
        if "Distribution Similarity" in metrics:
            results['distribution_similarity'] = self._measure_distribution_similarity(
                aligned_original, aligned_processed
            )
        
        if "Information Loss" in metrics:
            results['information_loss'] = self._measure_information_loss(
                aligned_original, aligned_processed
            )
        
        if "Classification Utility" in metrics:
            results['classification_utility'] = self._measure_classification_utility(
                aligned_original, aligned_processed
            )
        
        if "Query Accuracy" in metrics:
            results['query_accuracy'] = self._measure_query_accuracy(
                aligned_original, aligned_processed
            )
        
        # Calculate overall utility score
        results['overall_utility'] = self._calculate_overall_utility(results)
        
        # Generate visualizations
        results['visualizations'] = self._create_utility_visualizations(
            aligned_original, aligned_processed, results
        )
        
        # Provide utility assessment
        results['utility_level'] = self._assess_utility_level(results['overall_utility'])
        results['recommendations'] = self._generate_utility_recommendations(results)
        
        return results
    
    def _align_datasets(self, original: pd.DataFrame, processed: pd.DataFrame) -> tuple:
        """Align datasets for comparison"""
        # Use common columns
        common_columns = list(set(original.columns) & set(processed.columns))
        
        if not common_columns:
            return original, processed
        
        original_aligned = original[common_columns].copy()
        processed_aligned = processed[common_columns].copy()
        
        # If sizes are different, take minimum
        min_size = min(len(original_aligned), len(processed_aligned))
        
        return original_aligned.head(min_size), processed_aligned.head(min_size)
    
    def _measure_statistical_similarity(self, original: pd.DataFrame, 
                                       processed: pd.DataFrame) -> Dict[str, float]:
        """Measure statistical similarity between datasets"""
        results = {}
        
        for col in original.columns:
            if col not in processed.columns:
                continue
            
            orig_series = original[col].dropna()
            proc_series = processed[col].dropna()
            
            if len(orig_series) == 0 or len(proc_series) == 0:
                continue
            
            if orig_series.dtype in ['int64', 'float64'] and proc_series.dtype in ['int64', 'float64']:
                # Numerical similarity
                try:
                    # Mean preservation
                    mean_diff = abs(orig_series.mean() - proc_series.mean()) / (abs(orig_series.mean()) + 1e-8)
                    mean_similarity = max(0, 1 - mean_diff)
                    
                    # Standard deviation preservation
                    std_diff = abs(orig_series.std() - proc_series.std()) / (abs(orig_series.std()) + 1e-8)
                    std_similarity = max(0, 1 - std_diff)
                    
                    # Range preservation
                    orig_range = orig_series.max() - orig_series.min()
                    proc_range = proc_series.max() - proc_series.min()
                    range_diff = abs(orig_range - proc_range) / (abs(orig_range) + 1e-8)
                    range_similarity = max(0, 1 - range_diff)
                    
                    col_similarity = np.mean([mean_similarity, std_similarity, range_similarity])
                    results[f'{col}_numerical'] = col_similarity
                
                except Exception:
                    results[f'{col}_numerical'] = 0.0
            
            else:
                # Categorical similarity
                try:
                    orig_counts = orig_series.value_counts(normalize=True)
                    proc_counts = proc_series.value_counts(normalize=True)
                    
                    # Compare distributions
                    all_values = set(orig_counts.index) | set(proc_counts.index)
                    
                    similarity_sum = 0.0
                    for value in all_values:
                        orig_prob = orig_counts.get(value, 0)
                        proc_prob = proc_counts.get(value, 0)
                        similarity_sum += min(orig_prob, proc_prob)
                    
                    results[f'{col}_categorical'] = similarity_sum
                
                except Exception:
                    results[f'{col}_categorical'] = 0.0
        
        # Overall statistical similarity
        if results:
            results['overall'] = np.mean(list(results.values()))
        else:
            results['overall'] = 0.0
        
        return results
    
    def _measure_correlation_preservation(self, original: pd.DataFrame, 
                                        processed: pd.DataFrame) -> Dict[str, float]:
        """Measure correlation preservation"""
        results = {}
        
        # Get numerical columns
        orig_numeric = original.select_dtypes(include=[np.number])
        proc_numeric = processed.select_dtypes(include=[np.number])
        
        common_numeric = list(set(orig_numeric.columns) & set(proc_numeric.columns))
        
        if len(common_numeric) < 2:
            return {'overall': 0.0, 'note': 'Insufficient numerical columns for correlation analysis'}
        
        try:
            # Calculate correlation matrices
            orig_corr = orig_numeric[common_numeric].corr()
            proc_corr = proc_numeric[common_numeric].corr()
            
            # Compare correlations
            correlation_similarities = []
            
            for i in range(len(common_numeric)):
                for j in range(i + 1, len(common_numeric)):
                    col1, col2 = common_numeric[i], common_numeric[j]
                    
                    orig_corr_val = orig_corr.loc[col1, col2]
                    proc_corr_val = proc_corr.loc[col1, col2]
                    
                    if pd.isna(orig_corr_val) or pd.isna(proc_corr_val):
                        continue
                    
                    # Correlation preservation score
                    corr_diff = abs(orig_corr_val - proc_corr_val)
                    corr_similarity = max(0, 1 - corr_diff)
                    
                    correlation_similarities.append(corr_similarity)
                    results[f'{col1}_vs_{col2}'] = corr_similarity
            
            results['overall'] = np.mean(correlation_similarities) if correlation_similarities else 0.0
            results['correlation_matrix_difference'] = np.mean(np.abs(orig_corr.values - proc_corr.values))
        
        except Exception as e:
            results['overall'] = 0.0
            results['error'] = str(e)
        
        return results
    
    def _measure_distribution_similarity(self, original: pd.DataFrame, 
                                       processed: pd.DataFrame) -> Dict[str, float]:
        """Measure distribution similarity using statistical tests"""
        results = {}
        
        for col in original.columns:
            if col not in processed.columns:
                continue
            
            orig_series = original[col].dropna()
            proc_series = processed[col].dropna()
            
            if len(orig_series) == 0 or len(proc_series) == 0:
                continue
            
            if orig_series.dtype in ['int64', 'float64'] and proc_series.dtype in ['int64', 'float64']:
                # Numerical distribution similarity
                try:
                    # Kolmogorov-Smirnov test
                    ks_stat, ks_p_value = stats.ks_2samp(orig_series, proc_series)
                    ks_similarity = 1 - ks_stat  # Higher similarity = lower KS statistic
                    
                    # Wasserstein distance (Earth Mover's Distance)
                    wasserstein_dist = stats.wasserstein_distance(orig_series, proc_series)
                    # Normalize by the range of original data
                    data_range = orig_series.max() - orig_series.min()
                    if data_range > 0:
                        normalized_wasserstein = wasserstein_dist / data_range
                        wasserstein_similarity = max(0, 1 - normalized_wasserstein)
                    else:
                        wasserstein_similarity = 1.0
                    
                    col_similarity = np.mean([ks_similarity, wasserstein_similarity])
                    results[f'{col}_distribution'] = col_similarity
                
                except Exception:
                    results[f'{col}_distribution'] = 0.0
            
            else:
                # Categorical distribution similarity
                try:
                    orig_counts = orig_series.value_counts(normalize=True)
                    proc_counts = proc_series.value_counts(normalize=True)
                    
                    # Chi-square test for categorical data
                    all_categories = list(set(orig_counts.index) | set(proc_counts.index))
                    
                    orig_freq = [orig_counts.get(cat, 0) * len(orig_series) for cat in all_categories]
                    proc_freq = [proc_counts.get(cat, 0) * len(proc_series) for cat in all_categories]
                    
                    # Avoid chi-square test with zero frequencies
                    if min(orig_freq + proc_freq) > 0:
                        chi2_stat, chi2_p_value = stats.chisquare(proc_freq, orig_freq)
                        # Convert chi-square to similarity (lower stat = higher similarity)
                        chi2_similarity = 1 / (1 + chi2_stat)
                    else:
                        chi2_similarity = 0.0
                    
                    results[f'{col}_distribution'] = chi2_similarity
                
                except Exception:
                    results[f'{col}_distribution'] = 0.0
        
        # Overall distribution similarity
        distribution_scores = [v for k, v in results.items() if k.endswith('_distribution')]
        results['overall'] = np.mean(distribution_scores) if distribution_scores else 0.0
        
        return results
    
    def _measure_information_loss(self, original: pd.DataFrame, 
                                 processed: pd.DataFrame) -> Dict[str, float]:
        """Measure information loss"""
        results = {}
        
        try:
            # Entropy-based information loss
            total_entropy_loss = 0.0
            columns_processed = 0
            
            for col in original.columns:
                if col not in processed.columns:
                    continue
                
                orig_series = original[col].dropna()
                proc_series = processed[col].dropna()
                
                if len(orig_series) == 0 or len(proc_series) == 0:
                    continue
                
                # Calculate entropy
                orig_entropy = self._calculate_entropy(orig_series)
                proc_entropy = self._calculate_entropy(proc_series)
                
                if orig_entropy > 0:
                    entropy_loss = max(0, (orig_entropy - proc_entropy) / orig_entropy)
                else:
                    entropy_loss = 0.0
                
                results[f'{col}_entropy_loss'] = entropy_loss
                total_entropy_loss += entropy_loss
                columns_processed += 1
            
            results['overall_entropy_loss'] = total_entropy_loss / columns_processed if columns_processed > 0 else 0.0
            results['information_preservation'] = 1 - results['overall_entropy_loss']
            
            # Mutual information loss between columns
            numeric_cols = original.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 2:
                mi_losses = []
                
                for i in range(len(numeric_cols)):
                    for j in range(i + 1, len(numeric_cols)):
                        col1, col2 = numeric_cols[i], numeric_cols[j]
                        
                        if col1 in processed.columns and col2 in processed.columns:
                            try:
                                orig_mi = mutual_info_score(
                                    pd.cut(original[col1], bins=10, duplicates='drop').cat.codes,
                                    pd.cut(original[col2], bins=10, duplicates='drop').cat.codes
                                )
                                proc_mi = mutual_info_score(
                                    pd.cut(processed[col1], bins=10, duplicates='drop').cat.codes,
                                    pd.cut(processed[col2], bins=10, duplicates='drop').cat.codes
                                )
                                
                                if orig_mi > 0:
                                    mi_loss = (orig_mi - proc_mi) / orig_mi
                                    mi_losses.append(max(0, mi_loss))
                            except Exception:
                                continue
                
                results['mutual_information_loss'] = np.mean(mi_losses) if mi_losses else 0.0
            
        except Exception as e:
            results['error'] = str(e)
            results['overall_entropy_loss'] = 1.0
            results['information_preservation'] = 0.0
        
        return results
    
    def _measure_classification_utility(self, original: pd.DataFrame, 
                                       processed: pd.DataFrame) -> Dict[str, float]:
        """Measure utility for classification tasks"""
        results = {}
        
        try:
            # Find potential target columns (categorical with reasonable number of classes)
            potential_targets = []
            for col in original.columns:
                if col in processed.columns:
                    if original[col].dtype == 'object' or original[col].nunique() <= 20:
                        if 2 <= original[col].nunique() <= 10:  # Good target candidates
                            potential_targets.append(col)
            
            if not potential_targets:
                return {'note': 'No suitable target columns for classification analysis'}
            
            target_col = potential_targets[0]  # Use first suitable target
            feature_cols = [col for col in original.columns if col != target_col and col in processed.columns]
            
            if len(feature_cols) < 2:
                return {'note': 'Insufficient feature columns for classification analysis'}
            
            # Prepare data
            orig_features = original[feature_cols].copy()
            orig_target = original[target_col].copy()
            proc_features = processed[feature_cols].copy()
            proc_target = processed[target_col].copy()
            
            # Handle categorical features
            for col in feature_cols:
                if orig_features[col].dtype == 'object':
                    le = LabelEncoder()
                    orig_features[col] = le.fit_transform(orig_features[col].astype(str))
                    proc_features[col] = le.transform(proc_features[col].astype(str))
            
            # Handle categorical target
            if orig_target.dtype == 'object':
                le_target = LabelEncoder()
                orig_target = le_target.fit_transform(orig_target.astype(str))
                proc_target = le_target.transform(proc_target.astype(str))
            
            # Remove NaN values
            orig_mask = ~(orig_features.isna().any(axis=1) | pd.isna(orig_target))
            proc_mask = ~(proc_features.isna().any(axis=1) | pd.isna(proc_target))
            
            orig_features = orig_features[orig_mask]
            orig_target = orig_target[orig_mask]
            proc_features = proc_features[proc_mask]
            proc_target = proc_target[proc_mask]
            
            if len(orig_features) < 10 or len(proc_features) < 10:
                return {'note': 'Insufficient data for classification analysis'}
            
            # Train-test split
            X_train_orig, X_test_orig, y_train_orig, y_test_orig = train_test_split(
                orig_features, orig_target, test_size=0.3, random_state=42
            )
            X_train_proc, X_test_proc, y_train_proc, y_test_proc = train_test_split(
                proc_features, proc_target, test_size=0.3, random_state=42
            )
            
            # Train classifiers
            clf_orig = RandomForestClassifier(n_estimators=50, random_state=42)
            clf_proc = RandomForestClassifier(n_estimators=50, random_state=42)
            
            clf_orig.fit(X_train_orig, y_train_orig)
            clf_proc.fit(X_train_proc, y_train_proc)
            
            # Evaluate
            orig_accuracy = accuracy_score(y_test_orig, clf_orig.predict(X_test_orig))
            proc_accuracy = accuracy_score(y_test_proc, clf_proc.predict(X_test_proc))
            
            results['original_accuracy'] = orig_accuracy
            results['processed_accuracy'] = proc_accuracy
            results['accuracy_preservation'] = proc_accuracy / orig_accuracy if orig_accuracy > 0 else 0.0
            results['target_column'] = target_col
            
        except Exception as e:
            results['error'] = str(e)
            results['accuracy_preservation'] = 0.0
        
        return results
    
    def _measure_query_accuracy(self, original: pd.DataFrame, 
                               processed: pd.DataFrame) -> Dict[str, float]:
        """Measure accuracy of common queries"""
        results = {}
        
        try:
            # Count queries
            results['count_preservation'] = len(processed) / len(original) if len(original) > 0 else 0.0
            
            # Sum queries (for numerical columns)
            numeric_cols = original.select_dtypes(include=[np.number]).columns
            sum_preservations = []
            
            for col in numeric_cols:
                if col in processed.columns:
                    orig_sum = original[col].sum()
                    proc_sum = processed[col].sum()
                    
                    if abs(orig_sum) > 1e-8:
                        preservation = 1 - abs(orig_sum - proc_sum) / abs(orig_sum)
                        preservation = max(0, preservation)
                    else:
                        preservation = 1.0 if abs(proc_sum) < 1e-8 else 0.0
                    
                    sum_preservations.append(preservation)
                    results[f'{col}_sum_preservation'] = preservation
            
            results['average_sum_preservation'] = np.mean(sum_preservations) if sum_preservations else 0.0
            
            # Mean queries
            mean_preservations = []
            
            for col in numeric_cols:
                if col in processed.columns:
                    orig_mean = original[col].mean()
                    proc_mean = processed[col].mean()
                    
                    if abs(orig_mean) > 1e-8:
                        preservation = 1 - abs(orig_mean - proc_mean) / abs(orig_mean)
                        preservation = max(0, preservation)
                    else:
                        preservation = 1.0 if abs(proc_mean) < 1e-8 else 0.0
                    
                    mean_preservations.append(preservation)
                    results[f'{col}_mean_preservation'] = preservation
            
            results['average_mean_preservation'] = np.mean(mean_preservations) if mean_preservations else 0.0
            
            # Overall query accuracy
            query_scores = [
                results['count_preservation'],
                results['average_sum_preservation'],
                results['average_mean_preservation']
            ]
            results['overall_query_accuracy'] = np.mean(query_scores)
            
        except Exception as e:
            results['error'] = str(e)
            results['overall_query_accuracy'] = 0.0
        
        return results
    
    def _calculate_entropy(self, series: pd.Series) -> float:
        """Calculate entropy of a series"""
        try:
            if series.dtype in ['int64', 'float64']:
                # For numerical data, discretize first
                bins = min(20, series.nunique())
                discretized = pd.cut(series, bins=bins, duplicates='drop')
                value_counts = discretized.value_counts(normalize=True)
            else:
                # For categorical data
                value_counts = series.value_counts(normalize=True)
            
            entropy = -sum(p * np.log2(p) for p in value_counts if p > 0)
            return entropy
        
        except Exception:
            return 0.0
    
    def _calculate_overall_utility(self, results: Dict[str, Any]) -> float:
        """Calculate overall utility score"""
        utility_scores = []
        
        # Statistical similarity
        if 'statistical_similarity' in results and 'overall' in results['statistical_similarity']:
            utility_scores.append(results['statistical_similarity']['overall'])
        
        # Correlation preservation
        if 'correlation_preservation' in results and 'overall' in results['correlation_preservation']:
            utility_scores.append(results['correlation_preservation']['overall'])
        
        # Distribution similarity
        if 'distribution_similarity' in results and 'overall' in results['distribution_similarity']:
            utility_scores.append(results['distribution_similarity']['overall'])
        
        # Information preservation
        if 'information_loss' in results and 'information_preservation' in results['information_loss']:
            utility_scores.append(results['information_loss']['information_preservation'])
        
        # Classification utility
        if 'classification_utility' in results and 'accuracy_preservation' in results['classification_utility']:
            utility_scores.append(results['classification_utility']['accuracy_preservation'])
        
        # Query accuracy
        if 'query_accuracy' in results and 'overall_query_accuracy' in results['query_accuracy']:
            utility_scores.append(results['query_accuracy']['overall_query_accuracy'])
        
        return np.mean(utility_scores) if utility_scores else 0.0
    
    def _assess_utility_level(self, utility_score: float) -> str:
        """Assess utility level based on score"""
        if utility_score >= self.utility_thresholds['excellent']:
            return 'Excellent'
        elif utility_score >= self.utility_thresholds['good']:
            return 'Good'
        elif utility_score >= self.utility_thresholds['fair']:
            return 'Fair'
        elif utility_score >= self.utility_thresholds['poor']:
            return 'Poor'
        else:
            return 'Very Poor'
    
    def _generate_utility_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on utility results"""
        recommendations = []
        
        overall_utility = results.get('overall_utility', 0)
        utility_level = results.get('utility_level', 'Unknown')
        
        if utility_level == 'Very Poor':
            recommendations.append("CRITICAL: Utility is very poor. Consider less aggressive privacy techniques.")
        elif utility_level == 'Poor':
            recommendations.append("WARNING: Utility is poor. Review privacy parameters.")
        elif utility_level == 'Fair':
            recommendations.append("CAUTION: Utility is fair. Monitor for acceptable trade-offs.")
        
        # Specific metric recommendations
        if 'statistical_similarity' in results:
            stat_sim = results['statistical_similarity'].get('overall', 0)
            if stat_sim < 0.5:
                recommendations.append("Statistical properties are poorly preserved. Consider adjusting generalization levels.")
        
        if 'correlation_preservation' in results:
            corr_pres = results['correlation_preservation'].get('overall', 0)
            if corr_pres < 0.5:
                recommendations.append("Correlations are poorly preserved. Consider correlation-aware anonymization methods.")
        
        if 'information_loss' in results and 'information_preservation' in results['information_loss']:
            info_pres = results['information_loss']['information_preservation']
            if info_pres < 0.5:
                recommendations.append("High information loss detected. Consider synthetic data generation.")
        
        if 'classification_utility' in results and 'accuracy_preservation' in results['classification_utility']:
            class_util = results['classification_utility']['accuracy_preservation']
            if class_util < 0.7:
                recommendations.append("Classification accuracy significantly reduced. Review feature anonymization.")
        
        return recommendations
    
    def _create_utility_visualizations(self, original: pd.DataFrame, processed: pd.DataFrame,
                                      results: Dict[str, Any]) -> Dict[str, go.Figure]:
        """Create utility visualization plots"""
        visualizations = {}
        
        try:
            # Overall utility radar chart
            radar_fig = self._create_utility_radar_chart(results)
            visualizations['utility_radar'] = radar_fig
            
            # Distribution comparison plots
            dist_fig = self._create_distribution_comparison(original, processed)
            visualizations['distribution_comparison'] = dist_fig
            
            # Correlation heatmaps
            corr_fig = self._create_correlation_heatmaps(original, processed)
            visualizations['correlation_comparison'] = corr_fig
            
            # Utility scores bar chart
            scores_fig = self._create_utility_scores_chart(results)
            visualizations['utility_scores'] = scores_fig
            
        except Exception as e:
            # Create a simple error visualization
            error_fig = go.Figure()
            error_fig.add_annotation(
                text=f"Error creating visualizations: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            visualizations['error'] = error_fig
        
        return visualizations
    
    def _create_utility_radar_chart(self, results: Dict[str, Any]) -> go.Figure:
        """Create radar chart for utility metrics"""
        metrics = []
        values = []
        
        if 'statistical_similarity' in results and 'overall' in results['statistical_similarity']:
            metrics.append('Statistical Similarity')
            values.append(results['statistical_similarity']['overall'])
        
        if 'correlation_preservation' in results and 'overall' in results['correlation_preservation']:
            metrics.append('Correlation Preservation')
            values.append(results['correlation_preservation']['overall'])
        
        if 'distribution_similarity' in results and 'overall' in results['distribution_similarity']:
            metrics.append('Distribution Similarity')
            values.append(results['distribution_similarity']['overall'])
        
        if 'information_loss' in results and 'information_preservation' in results['information_loss']:
            metrics.append('Information Preservation')
            values.append(results['information_loss']['information_preservation'])
        
        if not metrics:
            # Create empty radar chart
            fig = go.Figure()
            fig.add_annotation(text="No utility metrics available", 
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=metrics,
            fill='toself',
            name='Utility Scores'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title="Utility Preservation Radar Chart"
        )
        
        return fig
    
    def _create_distribution_comparison(self, original: pd.DataFrame, 
                                       processed: pd.DataFrame) -> go.Figure:
        """Create distribution comparison plots"""
        # Select first few numerical columns for comparison
        numeric_cols = original.select_dtypes(include=[np.number]).columns
        cols_to_plot = numeric_cols[:4]  # Plot up to 4 columns
        
        if len(cols_to_plot) == 0:
            fig = go.Figure()
            fig.add_annotation(text="No numerical columns available for distribution comparison",
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        n_cols = len(cols_to_plot)
        n_rows = (n_cols + 1) // 2
        
        fig = make_subplots(
            rows=n_rows, cols=2,
            subplot_titles=[f'{col} Distribution' for col in cols_to_plot]
        )
        
        for i, col in enumerate(cols_to_plot):
            row = (i // 2) + 1
            col_pos = (i % 2) + 1
            
            if col in processed.columns:
                # Original distribution
                fig.add_trace(
                    go.Histogram(x=original[col], name=f'Original {col}', opacity=0.7,
                               nbinsx=20, histnorm='probability'),
                    row=row, col=col_pos
                )
                
                # Processed distribution
                fig.add_trace(
                    go.Histogram(x=processed[col], name=f'Processed {col}', opacity=0.7,
                               nbinsx=20, histnorm='probability'),
                    row=row, col=col_pos
                )
        
        fig.update_layout(
            title="Distribution Comparison: Original vs Processed",
            showlegend=True,
            height=400 * n_rows
        )
        
        return fig
    
    def _create_correlation_heatmaps(self, original: pd.DataFrame, 
                                    processed: pd.DataFrame) -> go.Figure:
        """Create correlation heatmaps comparison"""
        numeric_cols = original.select_dtypes(include=[np.number]).columns
        common_numeric = [col for col in numeric_cols if col in processed.columns]
        
        if len(common_numeric) < 2:
            fig = go.Figure()
            fig.add_annotation(text="Insufficient numerical columns for correlation analysis",
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        # Limit to first 10 columns for readability
        common_numeric = common_numeric[:10]
        
        orig_corr = original[common_numeric].corr()
        proc_corr = processed[common_numeric].corr()
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=['Original Data Correlations', 'Processed Data Correlations']
        )
        
        # Original correlations
        fig.add_trace(
            go.Heatmap(z=orig_corr.values, x=orig_corr.columns, y=orig_corr.columns,
                      colorscale='RdBu', zmid=0),
            row=1, col=1
        )
        
        # Processed correlations
        fig.add_trace(
            go.Heatmap(z=proc_corr.values, x=proc_corr.columns, y=proc_corr.columns,
                      colorscale='RdBu', zmid=0),
            row=1, col=2
        )
        
        fig.update_layout(title="Correlation Matrix Comparison", height=500)
        
        return fig
    
    def _create_utility_scores_chart(self, results: Dict[str, Any]) -> go.Figure:
        """Create bar chart of utility scores"""
        metrics = []
        scores = []
        
        # Extract utility scores
        if 'statistical_similarity' in results and 'overall' in results['statistical_similarity']:
            metrics.append('Statistical Similarity')
            scores.append(results['statistical_similarity']['overall'])
        
        if 'correlation_preservation' in results and 'overall' in results['correlation_preservation']:
            metrics.append('Correlation Preservation')
            scores.append(results['correlation_preservation']['overall'])
        
        if 'distribution_similarity' in results and 'overall' in results['distribution_similarity']:
            metrics.append('Distribution Similarity')
            scores.append(results['distribution_similarity']['overall'])
        
        if 'information_loss' in results and 'information_preservation' in results['information_loss']:
            metrics.append('Information Preservation')
            scores.append(results['information_loss']['information_preservation'])
        
        if 'classification_utility' in results and 'accuracy_preservation' in results['classification_utility']:
            metrics.append('Classification Utility')
            scores.append(results['classification_utility']['accuracy_preservation'])
        
        if 'query_accuracy' in results and 'overall_query_accuracy' in results['query_accuracy']:
            metrics.append('Query Accuracy')
            scores.append(results['query_accuracy']['overall_query_accuracy'])
        
        if not metrics:
            fig = go.Figure()
            fig.add_annotation(text="No utility scores available",
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=metrics,
            y=scores,
            marker_color=['green' if s > 0.7 else 'orange' if s > 0.5 else 'red' for s in scores]
        ))
        
        fig.update_layout(
            title="Utility Scores by Metric",
            xaxis_title="Utility Metric",
            yaxis_title="Score",
            yaxis=dict(range=[0, 1])
        )
        
        return fig
