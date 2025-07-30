import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.cluster import KMeans
from collections import defaultdict, Counter
import itertools

class RiskAssessment:
    """Risk assessment module for evaluating re-identification risks"""
    
    def __init__(self):
        self.risk_thresholds = {
            'low': 0.33,
            'medium': 0.67,
            'high': 1.0
        }
    
    def assess_risk(self, data: pd.DataFrame, quasi_identifiers: List[str], 
                   sensitive_attributes: List[str] = None, k_threshold: int = 3,
                   sample_size: float = 1.0, attack_scenarios: List[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive risk assessment on the dataset
        
        Args:
            data: Input dataset
            quasi_identifiers: List of quasi-identifier columns
            sensitive_attributes: List of sensitive attribute columns
            k_threshold: K-anonymity threshold
            sample_size: Fraction of data to analyze
            attack_scenarios: List of attack scenarios to simulate
        
        Returns:
            Dictionary containing risk assessment results
        """
        if sample_size < 1.0:
            data = data.sample(frac=sample_size, random_state=42)
        
        results = {
            'dataset_size': len(data),
            'quasi_identifiers': quasi_identifiers,
            'sensitive_attributes': sensitive_attributes or [],
            'k_threshold': k_threshold,
            'attack_scenarios': attack_scenarios or ['Prosecutor Attack']
        }
        
        # Calculate equivalence classes
        eq_classes = self._calculate_equivalence_classes(data, quasi_identifiers)
        results['equivalence_classes'] = eq_classes
        
        # K-anonymity violations
        k_violations = self._count_k_violations(eq_classes, k_threshold)
        results['k_violations'] = k_violations
        results['k_anonymity_satisfied'] = k_violations == 0
        
        # Unique records (highest risk)
        unique_records = sum(1 for eq_class in eq_classes if eq_class['size'] == 1)
        results['unique_records'] = unique_records
        
        # Overall risk calculation
        overall_risk = self._calculate_overall_risk(eq_classes, len(data))
        results['overall_risk'] = overall_risk
        
        # Risk level classification
        results['risk_level'] = self._classify_risk_level(overall_risk)
        
        # Attack-specific risks
        for scenario in attack_scenarios or ['Prosecutor Attack']:
            risk_score = self._simulate_attack(data, quasi_identifiers, scenario, eq_classes)
            results[f'{scenario.lower().replace(" ", "_")}_risk'] = risk_score
        
        # Population uniqueness estimation
        if len(data) > 100:  # Only for reasonably sized datasets
            pop_uniqueness = self._estimate_population_uniqueness(eq_classes, len(data))
            results['population_uniqueness'] = pop_uniqueness
        
        # Sensitive attribute risks (if provided)
        if sensitive_attributes:
            sensitive_risks = self._assess_sensitive_attribute_risks(
                data, quasi_identifiers, sensitive_attributes, eq_classes
            )
            results['sensitive_attribute_risks'] = sensitive_risks
        
        return results
    
    def _calculate_equivalence_classes(self, data: pd.DataFrame, 
                                     quasi_identifiers: List[str]) -> List[Dict[str, Any]]:
        """Calculate equivalence classes based on quasi-identifiers"""
        if not quasi_identifiers:
            return []
        
        # Group by quasi-identifiers
        grouped = data.groupby(quasi_identifiers)
        
        eq_classes = []
        for name, group in grouped:
            eq_class = {
                'qi_values': name if isinstance(name, tuple) else (name,),
                'size': len(group),
                'indices': group.index.tolist()
            }
            eq_classes.append(eq_class)
        
        # Sort by size (smallest first - highest risk)
        eq_classes.sort(key=lambda x: x['size'])
        
        return eq_classes
    
    def _count_k_violations(self, eq_classes: List[Dict[str, Any]], k: int) -> int:
        """Count number of equivalence classes violating k-anonymity"""
        return sum(1 for eq_class in eq_classes if eq_class['size'] < k)
    
    def _calculate_overall_risk(self, eq_classes: List[Dict[str, Any]], 
                               total_records: int) -> float:
        """Calculate overall re-identification risk"""
        if not eq_classes or total_records == 0:
            return 0.0
        
        # Risk is inversely proportional to equivalence class size
        total_risk = 0.0
        for eq_class in eq_classes:
            class_risk = 1.0 / eq_class['size']  # Risk per record in this class
            total_risk += class_risk * eq_class['size']  # Total risk from this class
        
        return total_risk / total_records
    
    def _classify_risk_level(self, risk_score: float) -> str:
        """Classify risk level based on score"""
        if risk_score <= self.risk_thresholds['low']:
            return 'Low'
        elif risk_score <= self.risk_thresholds['medium']:
            return 'Medium'
        else:
            return 'High'
    
    def _simulate_attack(self, data: pd.DataFrame, quasi_identifiers: List[str],
                        attack_type: str, eq_classes: List[Dict[str, Any]]) -> float:
        """Simulate different types of linkage attacks"""
        if attack_type == "Prosecutor Attack":
            # Prosecutor knows individual is in the dataset
            return self._prosecutor_attack_risk(eq_classes)
        elif attack_type == "Journalist Attack":
            # Journalist doesn't know if individual is in dataset
            return self._journalist_attack_risk(eq_classes, len(data))
        elif attack_type == "Marketer Attack":
            # Marketer wants to learn about a group
            return self._marketer_attack_risk(eq_classes)
        else:
            return self._prosecutor_attack_risk(eq_classes)
    
    def _prosecutor_attack_risk(self, eq_classes: List[Dict[str, Any]]) -> float:
        """Calculate prosecutor attack risk (individual known to be in dataset)"""
        if not eq_classes:
            return 0.0
        
        total_records = sum(eq_class['size'] for eq_class in eq_classes)
        risk_sum = 0.0
        
        for eq_class in eq_classes:
            # Probability of correct re-identification for this class
            class_risk = 1.0 / eq_class['size']
            risk_sum += class_risk * eq_class['size']
        
        return risk_sum / total_records
    
    def _journalist_attack_risk(self, eq_classes: List[Dict[str, Any]], 
                               dataset_size: int) -> float:
        """Calculate journalist attack risk (individual may not be in dataset)"""
        prosecutor_risk = self._prosecutor_attack_risk(eq_classes)
        
        # Assume 50% probability that individual is in the dataset
        presence_probability = 0.5
        
        return prosecutor_risk * presence_probability
    
    def _marketer_attack_risk(self, eq_classes: List[Dict[str, Any]]) -> float:
        """Calculate marketer attack risk (interested in group characteristics)"""
        if not eq_classes:
            return 0.0
        
        # Risk based on smallest equivalence classes
        small_classes = [eq for eq in eq_classes if eq['size'] <= 5]
        
        if not small_classes:
            return 0.0
        
        total_in_small_classes = sum(eq['size'] for eq in small_classes)
        total_records = sum(eq['size'] for eq in eq_classes)
        
        return total_in_small_classes / total_records
    
    def _estimate_population_uniqueness(self, eq_classes: List[Dict[str, Any]], 
                                      sample_size: int) -> float:
        """Estimate population uniqueness using sample-based methods"""
        # Simple estimation based on unique records in sample
        unique_count = sum(1 for eq_class in eq_classes if eq_class['size'] == 1)
        
        # Estimate population uniqueness (simplified model)
        if sample_size > 0:
            sample_uniqueness = unique_count / sample_size
            # Adjust for population (assumes population is much larger)
            estimated_pop_uniqueness = min(sample_uniqueness * 1.5, 1.0)
            return estimated_pop_uniqueness
        
        return 0.0
    
    def _assess_sensitive_attribute_risks(self, data: pd.DataFrame, 
                                        quasi_identifiers: List[str],
                                        sensitive_attributes: List[str],
                                        eq_classes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess risks related to sensitive attributes"""
        risks = {}
        
        for sensitive_attr in sensitive_attributes:
            if sensitive_attr not in data.columns:
                continue
            
            attr_risks = {
                'attribute': sensitive_attr,
                'disclosure_risk': 0.0,
                'homogeneity_risk': 0.0,
                'inference_risk': 0.0
            }
            
            # Calculate disclosure risk for each equivalence class
            disclosure_risks = []
            homogeneity_risks = []
            
            for eq_class in eq_classes:
                class_indices = eq_class['indices']
                class_data = data.loc[class_indices]
                
                if len(class_data) == 0:
                    continue
                
                # Get sensitive values for this class
                sensitive_values = class_data[sensitive_attr].dropna()
                
                if len(sensitive_values) == 0:
                    continue
                
                # Disclosure risk: probability of inferring sensitive value
                unique_values = sensitive_values.nunique()
                class_disclosure_risk = 1.0 / unique_values if unique_values > 0 else 1.0
                disclosure_risks.append(class_disclosure_risk * len(class_data))
                
                # Homogeneity risk: all records have same sensitive value
                if unique_values == 1:
                    homogeneity_risks.append(len(class_data))
            
            # Calculate overall risks
            total_records = len(data)
            if total_records > 0:
                attr_risks['disclosure_risk'] = sum(disclosure_risks) / total_records
                attr_risks['homogeneity_risk'] = sum(homogeneity_risks) / total_records
            
            risks[sensitive_attr] = attr_risks
        
        return risks
    
    def create_risk_visualization(self, risk_results: Dict[str, Any]) -> go.Figure:
        """Create comprehensive risk visualization"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Equivalence Class Size Distribution',
                'Risk Level Distribution',
                'K-Anonymity Compliance',
                'Attack Scenario Risks'
            ),
            specs=[[{"type": "histogram"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        eq_classes = risk_results.get('equivalence_classes', [])
        
        if eq_classes:
            # Equivalence class size distribution
            sizes = [eq['size'] for eq in eq_classes]
            fig.add_trace(
                go.Histogram(x=sizes, name="Class Sizes", nbinsx=20),
                row=1, col=1
            )
            
            # Risk level pie chart
            risk_level = risk_results.get('risk_level', 'Unknown')
            risk_counts = {'Low': 0, 'Medium': 0, 'High': 0}
            risk_counts[risk_level] = 1
            
            fig.add_trace(
                go.Pie(
                    labels=list(risk_counts.keys()),
                    values=list(risk_counts.values()),
                    name="Risk Level"
                ),
                row=1, col=2
            )
            
            # K-anonymity compliance
            k_threshold = risk_results.get('k_threshold', 3)
            compliant = sum(1 for eq in eq_classes if eq['size'] >= k_threshold)
            non_compliant = len(eq_classes) - compliant
            
            fig.add_trace(
                go.Bar(
                    x=['Compliant', 'Non-Compliant'],
                    y=[compliant, non_compliant],
                    name="K-Anonymity"
                ),
                row=2, col=1
            )
            
            # Attack scenario risks
            attack_risks = []
            attack_names = []
            
            for key, value in risk_results.items():
                if key.endswith('_risk') and isinstance(value, (int, float)):
                    attack_names.append(key.replace('_risk', '').replace('_', ' ').title())
                    attack_risks.append(value)
            
            if attack_risks:
                fig.add_trace(
                    go.Bar(
                        x=attack_names,
                        y=attack_risks,
                        name="Attack Risks"
                    ),
                    row=2, col=2
                )
        
        fig.update_layout(
            title_text="Risk Assessment Dashboard",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def get_recommendations(self, risk_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on risk assessment results"""
        recommendations = []
        
        overall_risk = risk_results.get('overall_risk', 0)
        risk_level = risk_results.get('risk_level', 'Unknown')
        k_violations = risk_results.get('k_violations', 0)
        unique_records = risk_results.get('unique_records', 0)
        
        # High-level recommendations
        if risk_level == 'High':
            recommendations.append(
                "HIGH RISK DETECTED: Apply strong privacy enhancement techniques immediately"
            )
        elif risk_level == 'Medium':
            recommendations.append(
                "MEDIUM RISK: Consider applying privacy enhancement techniques"
            )
        else:
            recommendations.append(
                "LOW RISK: Current privacy level may be acceptable for some use cases"
            )
        
        # Specific recommendations
        if k_violations > 0:
            recommendations.append(
                f"Apply k-anonymity with k≥{risk_results.get('k_threshold', 3)} to address "
                f"{k_violations} violating equivalence classes"
            )
        
        if unique_records > 0:
            recommendations.append(
                f"Remove or generalize {unique_records} unique records that pose highest risk"
            )
        
        if overall_risk > 0.8:
            recommendations.append(
                "Consider synthetic data generation as original data has very high risk"
            )
        
        # Sensitive attribute recommendations
        sensitive_risks = risk_results.get('sensitive_attribute_risks', {})
        for attr, risks in sensitive_risks.items():
            if risks.get('disclosure_risk', 0) > 0.7:
                recommendations.append(
                    f"Apply l-diversity or t-closeness to sensitive attribute '{attr}'"
                )
        
        # Data collection recommendations
        if len(risk_results.get('quasi_identifiers', [])) > 5:
            recommendations.append(
                "Consider reducing the number of quasi-identifiers to minimize risk"
            )
        
        return recommendations
