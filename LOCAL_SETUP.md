# SafeData Pipeline - Local Setup Guide

## Quick Start

### 1. Download the Project
Download all files from this Replit project to your local computer:

**Required Files:**
- `gui_app.py` - Main GUI application
- `app.py` - Web interface (backup option)
- `core/` folder - All processing modules
- `config/` folder - Configuration files
- `templates/` folder - Report templates
- `utils/` folder - Utility functions
- `requirements.txt` or `pyproject.toml` - Dependencies

### 2. Install Python
Download and install Python 3.8 or newer from [python.org](https://python.org)

**Windows:**
- Download the installer and check "Add Python to PATH"
- Verify installation: `python --version`

**macOS:**
- Use the installer or install via Homebrew: `brew install python`
- Verify installation: `python3 --version`

**Linux:**
- Most distributions include Python 3
- Install if needed: `sudo apt install python3 python3-pip` (Ubuntu/Debian)
- Verify installation: `python3 --version`

### 3. Install Dependencies
Open terminal/command prompt in the project folder and run:

```bash
# Option 1: Using pip
pip install pandas numpy matplotlib plotly scikit-learn streamlit openpyxl chardet cryptography fpdf2 jinja2 seaborn scipy

# Option 2: If you have requirements.txt
pip install -r requirements.txt

# Option 3: If you have pyproject.toml
pip install .
```

**Required Packages:**
- `pandas` - Data manipulation
- `numpy` - Numerical computing  
- `matplotlib` - Plotting and visualizations
- `plotly` - Interactive charts
- `scikit-learn` - Machine learning utilities
- `openpyxl` - Excel file support
- `chardet` - Character encoding detection
- `cryptography` - Data encryption
- `fpdf2` - PDF report generation
- `jinja2` - Template rendering

### 4. Run the GUI Application

**Method 1: Direct Launch**
```bash
python gui_app.py
```

**Method 2: Using Launcher Script**
```bash
python launch_gui.py
```

**Method 3: Web Interface (Backup)**
```bash
streamlit run app.py --server.port 8501
```
Then open http://localhost:8501 in your browser

## Detailed Setup Instructions

### Windows Setup

1. **Download Project Files**
   - Click "Download as ZIP" or use Git: `git clone <repository-url>`
   - Extract to desired location (e.g., `C:\SafeData`)

2. **Install Python**
   - Download from python.org
   - During installation, check "Add Python to PATH"
   - Restart computer if needed

3. **Open Command Prompt**
   - Press Win+R, type `cmd`, press Enter
   - Navigate to project folder: `cd C:\SafeData`

4. **Install Dependencies**
   ```cmd
   pip install pandas numpy matplotlib plotly scikit-learn openpyxl chardet cryptography fpdf2 jinja2
   ```

5. **Run Application**
   ```cmd
   python gui_app.py
   ```

### macOS Setup

1. **Download Project Files**
   - Download ZIP or use Git: `git clone <repository-url>`
   - Extract to desired location (e.g., `~/SafeData`)

2. **Install Python (if needed)**
   ```bash
   # Using Homebrew (recommended)
   brew install python
   
   # Or download from python.org
   ```

3. **Open Terminal**
   - Press Cmd+Space, type "Terminal", press Enter
   - Navigate to project: `cd ~/SafeData`

4. **Install Dependencies**
   ```bash
   pip3 install pandas numpy matplotlib plotly scikit-learn openpyxl chardet cryptography fpdf2 jinja2
   ```

5. **Run Application**
   ```bash
   python3 gui_app.py
   ```

### Linux Setup

1. **Download Project Files**
   ```bash
   git clone <repository-url>
   cd SafeData
   ```

2. **Install Python and Pip (if needed)**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-tkinter
   
   # CentOS/RHEL
   sudo yum install python3 python3-pip tkinter
   
   # Arch Linux
   sudo pacman -S python python-pip tk
   ```

3. **Install Dependencies**
   ```bash
   pip3 install pandas numpy matplotlib plotly scikit-learn openpyxl chardet cryptography fpdf2 jinja2
   ```

4. **Run Application**
   ```bash
   python3 gui_app.py
   ```

## Virtual Environment Setup (Recommended)

Using a virtual environment keeps your project dependencies isolated:

### Create Virtual Environment
```bash
# Windows
python -m venv safedata_env
safedata_env\Scripts\activate

# macOS/Linux
python3 -m venv safedata_env
source safedata_env/bin/activate
```

### Install Dependencies in Virtual Environment
```bash
pip install pandas numpy matplotlib plotly scikit-learn openpyxl chardet cryptography fpdf2 jinja2
```

### Run Application
```bash
python gui_app.py
```

### Deactivate Virtual Environment (when done)
```bash
deactivate
```

## File Structure

Your local project should have this structure:
```
SafeData/
├── gui_app.py              # Main GUI application
├── app.py                  # Web interface
├── launch_gui.py           # GUI launcher script
├── requirements.txt        # Dependencies list
├── core/
│   ├── data_handler.py
│   ├── risk_assessment.py
│   ├── privacy_enhancement.py
│   ├── utility_measurement.py
│   └── report_generator.py
├── config/
│   ├── privacy_profiles.json
│   └── system_config.json
├── templates/
│   └── report_template.html
├── utils/
│   └── (utility modules)
├── logs/                   # Created automatically
├── exports/                # Created automatically
└── temp/                   # Created automatically
```

## System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.14, or Linux with desktop environment
- **RAM**: 4GB (8GB recommended)
- **Storage**: 1GB free space
- **Python**: 3.8 or newer
- **Display**: Desktop environment with GUI support

### Recommended Requirements
- **RAM**: 8GB or more
- **CPU**: Quad-core processor
- **Storage**: SSD for better performance
- **Python**: 3.9 or newer

## Troubleshooting

### Common Issues

**"Python not found"**
- Ensure Python is installed and added to PATH
- Try `python3` instead of `python` on macOS/Linux

**"Module not found" errors**
- Install missing packages: `pip install <package-name>`
- Verify virtual environment is activated if using one

**GUI won't start**
- Ensure you're running on a desktop environment (not server)
- Try the web interface as backup: `streamlit run app.py`

**Permission errors**
- Run terminal/command prompt as administrator (Windows)
- Check file permissions on macOS/Linux

**Memory errors with large files**
- Start with smaller datasets for testing
- Increase system RAM if possible
- Adjust chunk size in application settings

### Getting Help

**Check Installation**
```bash
python --version
pip list | grep pandas
python -c "import tkinter; print('GUI support available')"
```

**Test Basic Functionality**
```bash
python -c "from core.data_handler import DataHandler; print('Core modules working')"
```

**Run with Debug Output**
```bash
python gui_app.py --debug
```

## Performance Optimization

### For Large Datasets
- Use sampling during risk assessment
- Enable chunked processing
- Close other applications to free memory
- Consider using SSD storage

### For Better Responsiveness
- GUI uses background threading for processing
- Progress bars show real-time status
- All long operations run in separate threads

## Security Considerations

### Data Protection
- Application processes data locally (no cloud upload)
- Enable encryption in configuration for sensitive data
- Temporary files are automatically cleaned up
- Original data files are never modified

### Best Practices
- Keep software updated
- Use strong system passwords
- Run regular antivirus scans
- Backup important data before processing

## Next Steps

1. **Download** all project files to your computer
2. **Install** Python 3.8+ and required packages
3. **Run** `python gui_app.py` to start the application
4. **Test** with a small sample dataset first
5. **Configure** privacy profiles for your use cases
6. **Generate** reports and export processed data

The application will open in a new desktop window with the familiar Government of India interface and all the privacy enhancement features you're used to from the web version.