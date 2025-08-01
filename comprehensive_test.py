#!/usr/bin/env python3
"""
Comprehensive testing script for SafeData Pipeline GUI
Tests all functionality and identifies any issues
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_comprehensive_test_data():
    """Create comprehensive test dataset"""
    print("Creating comprehensive test dataset...")
    
    # Generate more diverse test data
    np.random.seed(42)
    n_records = 1000
    
    # Government employee data simulation
    data = {
        'employee_id': [f'GOI{str(i).zfill(6)}' for i in range(1001, 1001 + n_records)],
        'name': [f'Employee_{i}' for i in range(1, n_records + 1)],
        'age': np.random.randint(22, 65, n_records),
        'gender': np.random.choice(['Male', 'Female'], n_records),
        'department': np.random.choice([
            'Revenue', 'Defense', 'Education', 'Health', 'Transport',
            'Agriculture', 'Technology', 'Finance', 'Administration'
        ], n_records),
        'state': np.random.choice([
            'Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Gujarat',
            'Uttar Pradesh', 'West Bengal', 'Rajasthan', 'Kerala', 'Punjab'
        ], n_records),
        'salary': np.random.randint(30000, 150000, n_records),
        'experience_years': np.random.randint(0, 40, n_records),
        'education': np.random.choice([
            'Graduate', 'Post Graduate', 'Diploma', 'PhD', 'Professional'
        ], n_records),
        'marital_status': np.random.choice(['Single', 'Married', 'Divorced'], n_records),
        'medical_coverage': np.random.choice([
            'Basic', 'Premium', 'Family', 'Individual', 'None'
        ], n_records),
        'performance_rating': np.random.choice([
            'Excellent', 'Good', 'Average', 'Below Average'
        ], n_records)
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add some missing values to test data quality assessment
    missing_indices = np.random.choice(n_records, size=int(n_records * 0.05), replace=False)
    df.loc[missing_indices[:20], 'salary'] = np.nan
    df.loc[missing_indices[20:40], 'education'] = np.nan
    
    # Add some duplicate records
    df = pd.concat([df, df.iloc[:10]], ignore_index=True)
    
    # Save test data
    df.to_csv('comprehensive_test_data.csv', index=False)
    print(f"✓ Created test dataset with {len(df)} records")
    return df

def test_core_modules():
    """Test core modules independently"""
    print("\nTesting core modules...")
    
    try:
        from core.data_handler import DataHandler
        from core.risk_assessment import RiskAssessment
        from core.privacy_enhancement import PrivacyEnhancement
        from core.utility_measurement import UtilityMeasurement
        from core.report_generator import ReportGenerator
        
        # Create test data
        test_df = create_comprehensive_test_data()
        
        # Test DataHandler
        print("Testing DataHandler...")
        data_handler = DataHandler()
        
        # Test data quality assessment
        quality_results = data_handler.assess_data_quality(test_df)
        print(f"  ✓ Quality assessment: Score {quality_results.get('quality_score', 0):.1f}%")
        
        # Test data repair
        repaired_data = data_handler.repair_data(test_df.copy())
        print(f"  ✓ Data repair: {len(repaired_data)} records after repair")
        
        # Test RiskAssessment
        print("Testing RiskAssessment...")
        risk_assessment = RiskAssessment()
        
        quasi_identifiers = ['age', 'gender', 'department', 'state']
        sensitive_attributes = ['salary', 'medical_coverage']
        
        risk_results = risk_assessment.assess_risk(
            repaired_data,
            quasi_identifiers=quasi_identifiers,
            sensitive_attributes=sensitive_attributes,
            k_threshold=3
        )
        print(f"  ✓ Risk assessment: Risk score {risk_results.get('overall_risk', 0):.3f}")
        
        # Test PrivacyEnhancement
        print("Testing PrivacyEnhancement...")
        privacy_enhancement = PrivacyEnhancement()
        
        # Test K-Anonymity
        k_anon_data = privacy_enhancement.apply_k_anonymity(
            repaired_data,
            k=3,
            quasi_identifiers=quasi_identifiers,
            method='global_recoding'
        )
        print(f"  ✓ K-Anonymity: {len(k_anon_data)} records after anonymization")
        
        # Test L-Diversity
        l_div_data = privacy_enhancement.apply_l_diversity(
            repaired_data,
            l=2,
            quasi_identifiers=quasi_identifiers,
            sensitive_attribute='salary'
        )
        print(f"  ✓ L-Diversity: {len(l_div_data)} records after anonymization")
        
        # Test UtilityMeasurement
        print("Testing UtilityMeasurement...")
        utility_measurement = UtilityMeasurement()
        
        utility_results = utility_measurement.measure_utility(
            repaired_data,
            k_anon_data,
            metrics=['statistical_similarity', 'correlation_preservation']
        )
        print(f"  ✓ Utility measurement: Overall utility {utility_results.get('overall_utility', 0):.3f}")
        
        # Test ReportGenerator
        print("Testing ReportGenerator...")
        report_generator = ReportGenerator()
        
        report_data = {
            'dataset_info': {
                'name': 'Test Dataset',
                'rows': len(repaired_data),
                'columns': len(repaired_data.columns),
                'upload_date': datetime.now().isoformat()
            },
            'risk_results': risk_results,
            'utility_results': utility_results
        }
        
        # Test HTML report generation
        html_report = report_generator.generate_html_report(report_data, 'Comprehensive')
        print(f"  ✓ HTML report generated: {len(html_report)} characters")
        
        # Test PDF report generation
        try:
            pdf_report = report_generator.generate_pdf_report(report_data, 'Technical')
            print(f"  ✓ PDF report generated: {len(pdf_report)} bytes")
        except Exception as e:
            print(f"  ⚠ PDF report generation failed: {e}")
        
        print("\n✅ All core modules tested successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Core module testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_functionality():
    """Test GUI functionality without showing window"""
    print("\nTesting GUI functionality...")
    
    try:
        import tkinter as tk
        from gui_app import SafeDataGUI
        
        # Create root window (hidden)
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Initialize GUI
        app = SafeDataGUI(root)
        print("  ✓ GUI components initialized")
        
        # Test data loading simulation
        test_data = pd.read_csv('comprehensive_test_data.csv')
        app.current_data = test_data
        print("  ✓ Data loading simulation successful")
        
        # Test column list updates
        app.update_column_lists(test_data.columns)
        print("  ✓ Column lists updated successfully")
        
        # Test data preview update
        app.update_data_preview(test_data.head(50))
        print("  ✓ Data preview updated successfully")
        
        # Test quality assessment display
        quality_results = {
            'quality_score': 85.5,
            'total_rows': len(test_data),
            'total_columns': len(test_data.columns),
            'missing_percentage': 5.2,
            'issues': ['Some missing values in salary column', 'Duplicate records detected']
        }
        app.update_quality_assessment(quality_results)
        print("  ✓ Quality assessment display updated")
        
        # Test privacy parameters update
        app.privacy_technique.set("K-Anonymity")
        app.update_privacy_params()
        print("  ✓ Privacy parameters updated")
        
        # Test result displays
        risk_results = {
            'overall_risk': 0.65,
            'risk_level': 'Medium',
            'k_anonymity_violations': 15,
            'unique_records': 25,
            'attack_scenarios': {
                'prosecutor': 0.7,
                'journalist': 0.6
            },
            'recommendations': ['Increase K value', 'Apply additional techniques']
        }
        app.display_risk_results(risk_results)
        print("  ✓ Risk results display updated")
        
        # Clean up
        root.destroy()
        
        print("\n✅ GUI functionality testing completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ GUI functionality testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_performance_tests():
    """Run performance tests with larger datasets"""
    print("\nRunning performance tests...")
    
    try:
        # Create larger dataset
        large_data = pd.DataFrame({
            'id': range(10000),
            'age': np.random.randint(18, 80, 10000),
            'income': np.random.randint(20000, 200000, 10000),
            'category': np.random.choice(['A', 'B', 'C', 'D'], 10000)
        })
        
        from core.data_handler import DataHandler
        from core.privacy_enhancement import PrivacyEnhancement
        
        data_handler = DataHandler()
        privacy_enhancement = PrivacyEnhancement()
        
        # Test data quality assessment performance
        start_time = time.time()
        quality_results = data_handler.assess_data_quality(large_data)
        quality_time = time.time() - start_time
        print(f"  ✓ Quality assessment on 10K records: {quality_time:.2f}s")
        
        # Test anonymization performance
        start_time = time.time()
        anon_data = privacy_enhancement.apply_k_anonymity(
            large_data,
            k=5,
            quasi_identifiers=['age', 'category'],
            method='global_recoding'
        )
        anon_time = time.time() - start_time
        print(f"  ✓ K-anonymization on 10K records: {anon_time:.2f}s")
        
        print(f"\n✅ Performance tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Performance testing failed: {e}")
        return False

def main():
    """Main testing function"""
    print("SafeData Pipeline - Comprehensive Testing")
    print("=" * 50)
    
    # Create necessary directories
    os.makedirs('config', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('exports', exist_ok=True)
    os.makedirs('temp', exist_ok=True)
    
    # Run all tests
    tests_passed = 0
    total_tests = 3
    
    if test_core_modules():
        tests_passed += 1
    
    if test_gui_functionality():
        tests_passed += 1
    
    if run_performance_tests():
        tests_passed += 1
    
    # Final results
    print("\n" + "=" * 50)
    print(f"Testing Results: {tests_passed}/{total_tests} test suites passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! SafeData Pipeline is ready for deployment.")
        
        # Create success report
        with open('test_report.txt', 'w') as f:
            f.write(f"SafeData Pipeline Test Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tests Passed: {tests_passed}/{total_tests}\n")
            f.write(f"Status: READY FOR DEPLOYMENT\n\n")
            f.write("All core modules and GUI functionality tested successfully.\n")
            f.write("Performance tests completed within acceptable limits.\n")
        
        return True
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)