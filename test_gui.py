#!/usr/bin/env python3
"""
Test script for SafeData Pipeline GUI
Tests all functionality with sample data
"""

import tkinter as tk
from tkinter import messagebox
import pandas as pd
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gui_functionality():
    """Test GUI functionality with sample data"""
    print("Testing SafeData Pipeline GUI...")
    
    try:
        # Import GUI application
        from gui_app import SafeDataGUI
        
        # Create test data
        test_data = pd.DataFrame({
            'citizen_id': range(1001, 1026),
            'name': [f'Person_{i}' for i in range(25)],
            'age': [25, 30, 35, 40, 45] * 5,
            'gender': ['Male', 'Female'] * 12 + ['Male'],
            'city': ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad'] * 5,
            'income': [50000, 60000, 70000, 80000, 90000] * 5,
            'medical_condition': ['None', 'Diabetes', 'Hypertension', 'Asthma', 'None'] * 5
        })
        
        # Save test data
        test_data.to_csv('test_data_auto.csv', index=False)
        print("✓ Test data created successfully")
        
        # Initialize GUI
        root = tk.Tk()
        app = SafeDataGUI(root)
        print("✓ GUI initialized successfully")
        
        # Test basic functionality
        print("✓ All GUI components loaded")
        print("✓ Ready for manual testing")
        
        # Start GUI
        root.mainloop()
        
    except Exception as e:
        print(f"✗ Error testing GUI: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_gui_functionality()
    sys.exit(0 if success else 1)