# SafeData Pipeline - Government of India

🔒 **Data Privacy Protection and Anonymization System**

Ministry of Electronics and Information Technology  
Government of India

---

## Overview

SafeData Pipeline is a comprehensive web-based application designed to meet the Government of India's data privacy protection and anonymization requirements. The system provides state-of-the-art privacy enhancement techniques while preserving data utility for analytical purposes.

### 🎯 Key Features

- **Risk Assessment**: Evaluate re-identification risks using multiple attack scenarios
- **Privacy Enhancement**: Apply k-anonymity, l-diversity, t-closeness, and differential privacy
- **Utility Measurement**: Assess data quality preservation after anonymization
- **Report Generation**: Create comprehensive privacy-utility analysis reports
- **Multi-format Support**: Handle CSV, Excel, JSON, XML, and Parquet files
- **Configuration Management**: Save and manage privacy parameter profiles

### 🏛️ Government Compliance

- Aligned with Ministry of Electronics and IT data protection framework
- Supports Digital Personal Data Protection Act requirements
- ISO/IEC 27001 compliant security practices
- NIST Privacy Framework alignment

---

## Quick Start

### Prerequisites

- Python 3.8 or higher
- 8GB RAM minimum (16GB recommended)
- 2GB free storage space
- Internet connection for initial setup

### Installation

1. **Clone or download the application files**
   ```bash
   git clone <repository-url>
   cd safedata-pipeline
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the application**
   Open your web browser and navigate to: `http://localhost:5000`

### Basic Workflow

1. **Upload Data** → Load your dataset (CSV, Excel, JSON, XML, Parquet)
2. **Assess Risk** → Identify re-identification vulnerabilities
3. **Apply Privacy** → Choose and configure anonymization techniques
4. **Measure Utility** → Evaluate data quality preservation
5. **Generate Reports** → Create comprehensive analysis documents

---

## Privacy Techniques

### 🛡️ K-Anonymity
Ensures each individual is indistinguishable from at least k-1 others
- **Best for**: Basic privacy protection with good utility
- **Parameters**: k-value, generalization method, suppression limit

### 🎭 L-Diversity  
Ensures diversity in sensitive attributes within equivalence classes
- **Best for**: Protecting against homogeneity attacks
- **Parameters**: l-value, sensitive attribute selection, diversity method

### ⚖️ T-Closeness
Ensures sensitive attribute distributions match global distribution
- **Best for**: Protecting against skewness attacks  
- **Parameters**: t-value, distance measure, sensitive attribute

### 🔢 Differential Privacy
Adds calibrated noise to prevent inference attacks
- **Best for**: Strong mathematical privacy guarantees
- **Parameters**: epsilon (privacy budget), sensitivity, noise mechanism

### 🧬 Synthetic Data Generation
Creates artificial datasets maintaining statistical properties
- **Best for**: Data sharing without exposing original records
- **Parameters**: generation method, sample size, preservation options

---

## System Architecture

