#!/usr/bin/env python3
"""
Comprehensive GUI Testing Script for SafeData Pipeline
Tests all functionality with sample data
"""

import os
import sys
import pandas as pd
import json
import time
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_test_data():
    """Create comprehensive test dataset"""
    data = {
        'Name': [
            'John Smith', 'Priya Sharma', 'Rahul Kumar', 'Anjali Patel', 'Vikram Singh',
            'Sunita Reddy', 'Amit Gupta', 'Kavita Joshi', 'Rajesh Mehta', 'Neha Agarwal',
            'Suresh Yadav', 'Deepika Rao', 'Manoj Tiwari', 'Pooja Mishra', 'Arjun Nair',
            'Ritu Kapoor', 'Sanjay Verma', 'Meera Shah', 'Kiran Pandey', 'Shweta Singh'
        ],
        'Age': [34, 28, 42, 31, 37, 29, 45, 33, 39, 26, 41, 35, 38, 30, 43, 32, 46, 27, 40, 34],
        'City': [
            'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad',
            'Pune', 'Kolkata', 'Ahmedabad', 'Surat', 'Jaipur',
            'Lucknow', 'Indore', 'Bhopal', 'Kanpur', 'Kochi',
            'Chandigarh', 'Nagpur', 'Vadodara', 'Patna', 'Gurgaon'
        ],
        'Income': [75000, 65000, 85000, 70000, 80000, 62000, 90000, 68000, 77000, 58000,
                  82000, 72000, 79000, 66000, 87000, 69000, 92000, 61000, 78000, 74000],
        'Email': [
            f'{name.lower().replace(" ", ".")}@email.com' 
            for name in [
                'John Smith', 'Priya Sharma', 'Rahul Kumar', 'Anjali Patel', 'Vikram Singh',
                'Sunita Reddy', 'Amit Gupta', 'Kavita Joshi', 'Rajesh Mehta', 'Neha Agarwal',
                'Suresh Yadav', 'Deepika Rao', 'Manoj Tiwari', 'Pooja Mishra', 'Arjun Nair',
                'Ritu Kapoor', 'Sanjay Verma', 'Meera Shah', 'Kiran Pandey', 'Shweta Singh'
            ]
        ],
        'Phone': [f'9{i:09d}' for i in range(876543210, 876543230)],
        'SSN': [f'{100+i:03d}-{45+i:02d}-{6789+i:04d}' for i in range(20)],
        'Gender': ['Male', 'Female'] * 10,
        'Department': [
            'Engineering', 'Marketing', 'Sales', 'HR', 'Finance',
            'IT', 'Operations', 'Legal', 'Admin', 'Design'
        ] * 2,
        'Salary': [75000, 65000, 85000, 70000, 80000, 62000, 90000, 68000, 77000, 58000,
                  82000, 72000, 79000, 66000, 87000, 69000, 92000, 61000, 78000, 74000]
    }
    
    return pd.DataFrame(data)

def test_core_modules():
    """Test core functionality modules"""
    try:
        from core.data_handler import DataHandler
        from core.risk_assessment import RiskAssessment
        from core.privacy_enhancement import PrivacyEnhancement
        from core.utility_measurement import UtilityMeasurement
        from core.report_generator import ReportGenerator
        
        print("✓ All core modules imported successfully")
        
        # Create test data
        df = create_test_data()
        df.to_csv('test_gui_data.csv', index=False)
        print("✓ Test data created and saved")
        
        # Test DataHandler
        data_handler = DataHandler()
        loaded_data = data_handler.load_file('test_gui_data.csv')
        print(f"✓ DataHandler: Loaded {len(loaded_data)} records")
        
        # Test RiskAssessment
        risk_assessment = RiskAssessment()
        qi_columns = ['Age', 'City', 'Gender']
        sa_columns = ['Salary', 'Department']
        
        risk_results = risk_assessment.assess_risk(
            data=loaded_data,
            quasi_identifiers=qi_columns,
            sensitive_attributes=sa_columns,
            k_threshold=3
        )
        print(f"✓ RiskAssessment: K-anonymity score = {risk_results.get('k_anonymity_score', 'N/A')}")
        
        # Test PrivacyEnhancement
        privacy_enhancement = PrivacyEnhancement()
        enhanced_data = privacy_enhancement.apply_k_anonymity(
            data=loaded_data,
            quasi_identifiers=qi_columns,
            k=3
        )
        print(f"✓ PrivacyEnhancement: Enhanced data has {len(enhanced_data)} records")
        
        # Test UtilityMeasurement
        utility_measurement = UtilityMeasurement()
        utility_results = utility_measurement.measure_utility(
            loaded_data,
            enhanced_data
        )
        print(f"✓ UtilityMeasurement: Overall utility score = {utility_results.get('overall_utility', 'N/A')}")
        
        # Test ReportGenerator
        report_generator = ReportGenerator()
        report_data = {
            'original_data': loaded_data,
            'anonymized_data': enhanced_data,
            'risk_results': risk_results,
            'utility_results': utility_results,
            'configuration': {
                'technique': 'K-Anonymity',
                'k_value': 3,
                'quasi_identifiers': qi_columns,
                'sensitive_attributes': sa_columns
            }
        }
        
        html_report = report_generator.generate_html_report(report_data, 'comprehensive')
        print("✓ ReportGenerator: HTML report generated successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing core modules: {str(e)}")
        return False

def test_gui_application():
    """Test GUI application startup and basic functionality"""
    try:
        import tkinter as tk
        from gui_app import SafeDataGUI
        
        print("✓ GUI imports successful")
        
        # Create root window (but don't show it)
        root = tk.Tk()
        root.withdraw()  # Hide the window for testing
        
        # Initialize GUI (this tests constructor and setup)
        app = SafeDataGUI(root)
        print("✓ GUI application initialized successfully")
        
        # Test basic GUI methods
        if hasattr(app, 'update_privacy_params'):
            app.update_privacy_params()
            print("✓ Privacy parameters update method working")
        
        if hasattr(app, 'load_profiles'):
            app.load_profiles()
            print("✓ Profile loading method working")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing GUI application: {str(e)}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("=" * 60)
    print("SafeData Pipeline - Comprehensive GUI Testing")
    print("=" * 60)
    
    # Test 1: Core Modules
    print("\n1. Testing Core Modules...")
    core_test_passed = test_core_modules()
    
    # Test 2: GUI Application
    print("\n2. Testing GUI Application...")
    gui_test_passed = test_gui_application()
    
    # Test Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Core Modules: {'PASSED' if core_test_passed else 'FAILED'}")
    print(f"GUI Application: {'PASSED' if gui_test_passed else 'FAILED'}")
    
    overall_status = "PASSED" if (core_test_passed and gui_test_passed) else "FAILED"
    print(f"\nOverall Test Status: {overall_status}")
    
    if overall_status == "PASSED":
        print("\n✓ All tests passed! GUI application is ready to use.")
        print("✓ You can now run 'python gui_app.py' to start the application.")
    else:
        print("\n✗ Some tests failed. Please check the error messages above.")
    
    return overall_status == "PASSED"

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)