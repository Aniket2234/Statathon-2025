#!/usr/bin/env python3
"""
Simple launcher for SafeData Pipeline GUI
Tests GUI functionality and provides fallback options
"""

import sys
import os

def test_gui_requirements():
    """Test if GUI requirements are available"""
    try:
        import tkinter as tk
        print("✓ tkinter is available")
        
        # Test if display is available
        root = tk.Tk()
        root.withdraw()  # Hide the window
        root.destroy()
        print("✓ Display available for GUI")
        return True
    except Exception as e:
        print(f"✗ GUI not available: {e}")
        return False

def launch_gui():
    """Launch the GUI application"""
    if test_gui_requirements():
        print("Launching SafeData Pipeline GUI...")
        try:
            from gui_app import SafeDataGUI
            import tkinter as tk
            
            root = tk.Tk()
            app = SafeDataGUI(root)
            print("✓ GUI application started successfully")
            root.mainloop()
            
        except Exception as e:
            print(f"✗ Error launching GUI: {e}")
            return False
    else:
        print("GUI requirements not met. Please use the web interface instead:")
        print("Run: streamlit run app.py --server.port 5000")
        return False
    
    return True

if __name__ == "__main__":
    print("SafeData Pipeline - GUI Launcher")
    print("=" * 40)
    
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    success = launch_gui()
    
    if not success:
        print("\nAlternative: Web interface is available")
        print("The web version provides the same functionality")
        
    sys.exit(0 if success else 1)