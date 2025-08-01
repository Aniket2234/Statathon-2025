#!/usr/bin/env python3
"""
Local Installation Script for SafeData Pipeline
Automatically installs all required dependencies and sets up the environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"⏳ {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    packages = [
        "pandas>=1.5.0",
        "numpy>=1.21.0", 
        "matplotlib>=3.5.0",
        "plotly>=5.0.0",
        "seaborn>=0.11.0",
        "scikit-learn>=1.1.0",
        "scipy>=1.9.0",
        "openpyxl>=3.0.0",
        "chardet>=5.0.0",
        "cryptography>=37.0.0",
        "fpdf2>=2.5.0",
        "jinja2>=3.1.0",
        "streamlit>=1.25.0"
    ]
    
    for package in packages:
        command = f"{sys.executable} -m pip install {package}"
        if not run_command(command, f"Installing {package.split('>=')[0]}"):
            return False
    
    return True

def test_installation():
    """Test if all modules can be imported"""
    modules_to_test = [
        ("pandas", "pd"),
        ("numpy", "np"),
        ("matplotlib.pyplot", "plt"),
        ("plotly.graph_objects", "go"),
        ("sklearn", "sklearn"),
        ("cryptography", "cryptography"),
        ("fpdf", "fpdf"),
        ("jinja2", "jinja2"),
        ("tkinter", "tk")
    ]
    
    print("\n🧪 Testing module imports...")
    all_good = True
    
    for module, alias in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            all_good = False
    
    return all_good

def create_directories():
    """Create necessary directories"""
    directories = ["config", "logs", "exports", "temp"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def main():
    """Main installation process"""
    print("SafeData Pipeline - Local Installation")
    print("=" * 50)
    
    # Check Python version
    if not check_python():
        print("\nPlease install Python 3.8 or newer from https://python.org")
        return False
    
    # Upgrade pip
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if not install_dependencies():
        print("\n❌ Failed to install some dependencies")
        return False
    
    # Test installation
    if not test_installation():
        print("\n❌ Some modules failed to import")
        return False
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    print("\n🎉 Installation completed successfully!")
    print("\nNext steps:")
    print("1. Run the GUI application: python gui_app.py")
    print("2. Or run the web interface: streamlit run app.py")
    print("3. Check LOCAL_SETUP.md for detailed usage instructions")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)