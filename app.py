import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import io
import base64

# Import core modules
from core.risk_assessment import RiskAssessment
from core.privacy_enhancement import PrivacyEnhancement
from core.utility_measurement import UtilityMeasurement
from core.data_handler import DataHandler
from core.report_generator import ReportGenerator
from utils.file_operations import FileOperations
from utils.validation import DataValidator
from utils.encryption import DataEncryption

# Configure page
st.set_page_config(
    page_title="SafeData Pipeline - Government of India",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'risk_results' not in st.session_state:
    st.session_state.risk_results = None
if 'utility_results' not in st.session_state:
    st.session_state.utility_results = None
if 'config' not in st.session_state:
    st.session_state.config = {}

# Initialize core components
@st.cache_resource
def initialize_components():
    """Initialize all core components"""
    return {
        'data_handler': DataHandler(),
        'risk_assessment': RiskAssessment(),
        'privacy_enhancement': PrivacyEnhancement(),
        'utility_measurement': UtilityMeasurement(),
        'report_generator': ReportGenerator(),
        'file_ops': FileOperations(),
        'validator': DataValidator(),
        'encryption': DataEncryption()
    }

components = initialize_components()

def main():
    """Main application function"""
    
    # Header
    st.title("🔒 SafeData Pipeline")
    st.markdown("### Government of India - Ministry of Electronics and IT")
    st.markdown("**Data Privacy Protection and Anonymization System**")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Module",
        ["Home", "Data Upload", "Risk Assessment", "Privacy Enhancement", 
         "Utility Measurement", "Reports", "Configuration", "Help"]
    )
    
    # Main content based on selected page
    if page == "Home":
        show_home()
    elif page == "Data Upload":
        show_data_upload()
    elif page == "Risk Assessment":
        show_risk_assessment()
    elif page == "Privacy Enhancement":
        show_privacy_enhancement()
    elif page == "Utility Measurement":
        show_utility_measurement()
    elif page == "Reports":
        show_reports()
    elif page == "Configuration":
        show_configuration()
    elif page == "Help":
        show_help()

def show_home():
    """Display home page with overview"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Welcome to SafeData Pipeline")
        
        st.markdown("""
        **SafeData Pipeline** is a comprehensive data privacy protection system designed to meet 
        the Government of India's data anonymization and privacy requirements.
        
        ### Key Features:
        - **Risk Assessment**: Evaluate re-identification risks in datasets
        - **Privacy Enhancement**: Apply k-anonymity, l-diversity, and differential privacy
        - **Utility Measurement**: Measure data utility preservation after anonymization
        - **Report Generation**: Generate comprehensive privacy-utility reports
        - **Multi-format Support**: Handle CSV, Excel, JSON, XML, and Parquet files
        
        ### Quick Start:
        1. Upload your dataset using the **Data Upload** module
        2. Run **Risk Assessment** to identify vulnerabilities
        3. Apply **Privacy Enhancement** techniques
        4. Measure **Utility** to ensure data quality
        5. Generate comprehensive **Reports**
        """)
    
    with col2:
        st.header("System Status")
        
        # Show current data status
        if st.session_state.data is not None:
            st.success("✅ Dataset Loaded")
            st.info(f"Rows: {len(st.session_state.data)}")
            st.info(f"Columns: {len(st.session_state.data.columns)}")
        else:
            st.warning("⚠️ No Dataset Loaded")
        
        if st.session_state.processed_data is not None:
            st.success("✅ Privacy Enhanced Data Available")
        
        if st.session_state.risk_results is not None:
            st.success("✅ Risk Assessment Complete")
        
        # Quick actions
        st.header("Quick Actions")
        if st.button("Load Sample Configuration"):
            load_sample_config()
        
        if st.button("Clear All Data"):
            clear_session_data()

def show_data_upload():
    """Data upload and validation interface"""
    st.header("📁 Data Upload and Validation")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx', 'xls', 'json', 'xml', 'parquet'],
        help="Supported formats: CSV, Excel, JSON, XML, Parquet"
    )
    
    if uploaded_file is not None:
        try:
            with st.spinner("Loading and validating data..."):
                # Load data based on file type
                data = components['data_handler'].load_data(uploaded_file)
                
                # Validate data
                validation_results = components['validator'].validate_data(data)
                
                if validation_results['is_valid']:
                    st.session_state.data = data
                    st.success("✅ Data loaded successfully!")
                    
                    # Display data preview
                    st.subheader("Data Preview")
                    st.dataframe(data.head(10))
                    
                    # Display data info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Rows", len(data))
                    with col2:
                        st.metric("Columns", len(data.columns))
                    with col3:
                        st.metric("Missing Values", data.isnull().sum().sum())
                    
                    # Column information
                    st.subheader("Column Information")
                    col_info = pd.DataFrame({
                        'Column': data.columns,
                        'Type': data.dtypes,
                        'Non-Null Count': data.count(),
                        'Unique Values': data.nunique()
                    })
                    st.dataframe(col_info)
                    
                else:
                    st.error("❌ Data validation failed!")
                    for error in validation_results['errors']:
                        st.error(error)
                    
                    # Offer data repair
                    if st.button("Attempt Data Repair"):
                        repaired_data = components['data_handler'].repair_data(data)
                        st.session_state.data = repaired_data
                        st.success("Data repair attempted. Please review the data.")
                        st.rerun()
                        
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
    
    # Data corruption handling section
    if st.session_state.data is not None:
        st.subheader("🔧 Data Quality Assessment")
        
        quality_report = components['data_handler'].assess_data_quality(st.session_state.data)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Quality Score", f"{quality_report['overall_quality']:.2f}%")
            st.metric("Completeness", f"{quality_report['completeness']:.2f}%")
        
        with col2:
            st.metric("Consistency", f"{quality_report['consistency']:.2f}%")
            st.metric("Validity", f"{quality_report['validity']:.2f}%")
        
        if quality_report['issues']:
            st.warning("Data Quality Issues Detected:")
            for issue in quality_report['issues']:
                st.write(f"- {issue}")
            
            if st.button("Apply Automatic Fixes"):
                fixed_data = components['data_handler'].apply_fixes(st.session_state.data, quality_report['issues'])
                st.session_state.data = fixed_data
                st.success("Automatic fixes applied!")
                st.rerun()

def show_risk_assessment():
    """Risk assessment interface"""
    st.header("⚠️ Risk Assessment")
    
    if st.session_state.data is None:
        st.warning("Please upload a dataset first.")
        return
    
    st.subheader("Configure Risk Assessment")
    
    # Quasi-identifier selection
    st.write("**Select Quasi-Identifiers:**")
    data_columns = st.session_state.data.columns.tolist()
    quasi_identifiers = st.multiselect(
        "Quasi-identifiers are attributes that can be used to re-identify individuals",
        data_columns,
        default=[]
    )
    
    # Sensitive attributes
    sensitive_attrs = st.multiselect(
        "Select Sensitive Attributes:",
        data_columns,
        default=[]
    )
    
    # Risk assessment parameters
    col1, col2 = st.columns(2)
    with col1:
        k_threshold = st.slider("K-Anonymity Threshold", 2, 20, 3)
        sample_size = st.slider("Sample Size for Assessment (%)", 10, 100, 50)
    
    with col2:
        attack_scenarios = st.multiselect(
            "Attack Scenarios to Simulate:",
            ["Prosecutor Attack", "Journalist Attack", "Marketer Attack"],
            default=["Prosecutor Attack"]
        )
    
    if st.button("Run Risk Assessment", type="primary"):
        if not quasi_identifiers:
            st.error("Please select at least one quasi-identifier.")
            return
        
        with st.spinner("Running risk assessment..."):
            try:
                risk_results = components['risk_assessment'].assess_risk(
                    st.session_state.data,
                    quasi_identifiers=quasi_identifiers,
                    sensitive_attributes=sensitive_attrs,
                    k_threshold=k_threshold,
                    sample_size=sample_size/100,
                    attack_scenarios=attack_scenarios
                )
                
                st.session_state.risk_results = risk_results
                
                # Display results
                st.success("✅ Risk assessment completed!")
                
                # Overall risk metrics
                st.subheader("Risk Metrics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Overall Risk", f"{risk_results['overall_risk']:.3f}")
                with col2:
                    st.metric("K-Anonymity Violations", risk_results['k_violations'])
                with col3:
                    st.metric("Unique Records", risk_results['unique_records'])
                with col4:
                    st.metric("Risk Level", risk_results['risk_level'])
                
                # Risk visualization
                st.subheader("Risk Visualization")
                fig = components['risk_assessment'].create_risk_visualization(risk_results)
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed risk analysis
                st.subheader("Detailed Analysis")
                if 'equivalence_classes' in risk_results:
                    ec_df = pd.DataFrame(risk_results['equivalence_classes'])
                    st.dataframe(ec_df)
                
                # Recommendations
                st.subheader("Recommendations")
                recommendations = components['risk_assessment'].get_recommendations(risk_results)
                for rec in recommendations:
                    st.info(f"💡 {rec}")
                    
            except Exception as e:
                st.error(f"Error during risk assessment: {str(e)}")

def show_privacy_enhancement():
    """Privacy enhancement interface"""
    st.header("🛡️ Privacy Enhancement")
    
    if st.session_state.data is None:
        st.warning("Please upload a dataset first.")
        return
    
    st.subheader("Select Privacy Enhancement Technique")
    
    technique = st.selectbox(
        "Choose Privacy Technique:",
        ["K-Anonymity", "L-Diversity", "T-Closeness", "Differential Privacy", "Synthetic Data Generation"]
    )
    
    # Configuration based on selected technique
    if technique == "K-Anonymity":
        show_k_anonymity_config()
    elif technique == "L-Diversity":
        show_l_diversity_config()
    elif technique == "T-Closeness":
        show_t_closeness_config()
    elif technique == "Differential Privacy":
        show_differential_privacy_config()
    elif technique == "Synthetic Data Generation":
        show_synthetic_data_config()

def show_k_anonymity_config():
    """K-Anonymity configuration"""
    st.subheader("K-Anonymity Configuration")
    
    data_columns = st.session_state.data.columns.tolist()
    
    # Parameter selection
    col1, col2 = st.columns(2)
    with col1:
        k_value = st.slider("K Value", 2, 20, 3)
        quasi_identifiers = st.multiselect("Quasi-Identifiers:", data_columns)
    
    with col2:
        generalization_method = st.selectbox(
            "Generalization Method:",
            ["Global Recoding", "Local Recoding", "Clustering"]
        )
        suppression_limit = st.slider("Suppression Limit (%)", 0, 50, 10)
    
    if st.button("Apply K-Anonymity", type="primary"):
        if not quasi_identifiers:
            st.error("Please select quasi-identifiers.")
            return
        
        with st.spinner("Applying K-Anonymity..."):
            try:
                processed_data = components['privacy_enhancement'].apply_k_anonymity(
                    st.session_state.data,
                    k=k_value,
                    quasi_identifiers=quasi_identifiers,
                    method=generalization_method,
                    suppression_limit=suppression_limit/100
                )
                
                st.session_state.processed_data = processed_data
                st.success("✅ K-Anonymity applied successfully!")
                
                # Show before/after comparison
                show_data_comparison()
                
            except Exception as e:
                st.error(f"Error applying K-Anonymity: {str(e)}")

def show_l_diversity_config():
    """L-Diversity configuration"""
    st.subheader("L-Diversity Configuration")
    
    data_columns = st.session_state.data.columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        l_value = st.slider("L Value", 2, 10, 2)
        quasi_identifiers = st.multiselect("Quasi-Identifiers:", data_columns)
    
    with col2:
        sensitive_attribute = st.selectbox("Sensitive Attribute:", data_columns)
        diversity_method = st.selectbox(
            "Diversity Method:",
            ["Distinct L-Diversity", "Entropy L-Diversity", "Recursive L-Diversity"]
        )
    
    if st.button("Apply L-Diversity", type="primary"):
        with st.spinner("Applying L-Diversity..."):
            try:
                processed_data = components['privacy_enhancement'].apply_l_diversity(
                    st.session_state.data,
                    l=l_value,
                    quasi_identifiers=quasi_identifiers,
                    sensitive_attribute=sensitive_attribute,
                    method=diversity_method
                )
                
                st.session_state.processed_data = processed_data
                st.success("✅ L-Diversity applied successfully!")
                
                show_data_comparison()
                
            except Exception as e:
                st.error(f"Error applying L-Diversity: {str(e)}")

def show_differential_privacy_config():
    """Differential Privacy configuration"""
    st.subheader("Differential Privacy Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        epsilon = st.slider("Epsilon (Privacy Budget)", 0.1, 10.0, 1.0, 0.1)
        noise_mechanism = st.selectbox("Noise Mechanism:", ["Laplace", "Gaussian"])
    
    with col2:
        sensitivity = st.number_input("Global Sensitivity", min_value=0.1, value=1.0, step=0.1)
        numeric_columns = st.multiselect(
            "Numeric Columns to Add Noise:",
            st.session_state.data.select_dtypes(include=[np.number]).columns.tolist()
        )
    
    if st.button("Apply Differential Privacy", type="primary"):
        with st.spinner("Applying Differential Privacy..."):
            try:
                processed_data = components['privacy_enhancement'].apply_differential_privacy(
                    st.session_state.data,
                    epsilon=epsilon,
                    sensitivity=sensitivity,
                    mechanism=noise_mechanism,
                    numeric_columns=numeric_columns
                )
                
                st.session_state.processed_data = processed_data
                st.success("✅ Differential Privacy applied successfully!")
                
                show_data_comparison()
                
            except Exception as e:
                st.error(f"Error applying Differential Privacy: {str(e)}")

def show_synthetic_data_config():
    """Synthetic Data Generation configuration"""
    st.subheader("Synthetic Data Generation")
    
    col1, col2 = st.columns(2)
    with col1:
        generation_method = st.selectbox(
            "Generation Method:",
            ["Statistical", "Copula", "GAN-based"]
        )
        sample_size = st.slider("Generated Sample Size (%)", 50, 200, 100)
    
    with col2:
        preserve_correlations = st.checkbox("Preserve Correlations", True)
        preserve_distributions = st.checkbox("Preserve Distributions", True)
    
    if st.button("Generate Synthetic Data", type="primary"):
        with st.spinner("Generating synthetic data..."):
            try:
                processed_data = components['privacy_enhancement'].generate_synthetic_data(
                    st.session_state.data,
                    method=generation_method,
                    sample_size=sample_size/100,
                    preserve_correlations=preserve_correlations,
                    preserve_distributions=preserve_distributions
                )
                
                st.session_state.processed_data = processed_data
                st.success("✅ Synthetic data generated successfully!")
                
                show_data_comparison()
                
            except Exception as e:
                st.error(f"Error generating synthetic data: {str(e)}")

def show_t_closeness_config():
    """T-Closeness configuration"""
    st.subheader("T-Closeness Configuration")
    
    data_columns = st.session_state.data.columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        t_value = st.slider("T Value", 0.1, 1.0, 0.2, 0.1)
        quasi_identifiers = st.multiselect("Quasi-Identifiers:", data_columns)
    
    with col2:
        sensitive_attribute = st.selectbox("Sensitive Attribute:", data_columns)
        distance_measure = st.selectbox("Distance Measure:", ["EMD", "Hierarchical"])
    
    if st.button("Apply T-Closeness", type="primary"):
        with st.spinner("Applying T-Closeness..."):
            try:
                processed_data = components['privacy_enhancement'].apply_t_closeness(
                    st.session_state.data,
                    t=t_value,
                    quasi_identifiers=quasi_identifiers,
                    sensitive_attribute=sensitive_attribute,
                    distance_measure=distance_measure
                )
                
                st.session_state.processed_data = processed_data
                st.success("✅ T-Closeness applied successfully!")
                
                show_data_comparison()
                
            except Exception as e:
                st.error(f"Error applying T-Closeness: {str(e)}")

def show_data_comparison():
    """Show before/after data comparison"""
    if st.session_state.processed_data is not None:
        st.subheader("Data Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Original Data (First 5 rows):**")
            st.dataframe(st.session_state.data.head())
        
        with col2:
            st.write("**Processed Data (First 5 rows):**")
            st.dataframe(st.session_state.processed_data.head())
        
        # Statistics comparison
        st.write("**Statistics Comparison:**")
        original_stats = st.session_state.data.describe()
        processed_stats = st.session_state.processed_data.describe()
        
        stats_comparison = pd.DataFrame({
            'Original': original_stats.loc['mean'] if 'mean' in original_stats.index else original_stats.iloc[0],
            'Processed': processed_stats.loc['mean'] if 'mean' in processed_stats.index else processed_stats.iloc[0]
        })
        st.dataframe(stats_comparison)

def show_utility_measurement():
    """Utility measurement interface"""
    st.header("📊 Utility Measurement")
    
    if st.session_state.data is None or st.session_state.processed_data is None:
        st.warning("Please upload data and apply privacy enhancement first.")
        return
    
    st.subheader("Utility Analysis Configuration")
    
    # Metric selection
    utility_metrics = st.multiselect(
        "Select Utility Metrics:",
        ["Statistical Similarity", "Correlation Preservation", "Distribution Similarity", 
         "Information Loss", "Classification Utility", "Query Accuracy"],
        default=["Statistical Similarity", "Correlation Preservation"]
    )
    
    if st.button("Measure Utility", type="primary"):
        with st.spinner("Measuring utility..."):
            try:
                utility_results = components['utility_measurement'].measure_utility(
                    st.session_state.data,
                    st.session_state.processed_data,
                    metrics=utility_metrics
                )
                
                st.session_state.utility_results = utility_results
                
                # Display results
                st.success("✅ Utility measurement completed!")
                
                # Overall utility score
                st.subheader("Utility Scores")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Overall Utility", f"{utility_results['overall_utility']:.3f}")
                with col2:
                    st.metric("Statistical Similarity", f"{utility_results.get('statistical_similarity', 0):.3f}")
                with col3:
                    st.metric("Information Loss", f"{utility_results.get('information_loss', 0):.3f}")
                
                # Detailed metrics
                st.subheader("Detailed Utility Metrics")
                
                for metric, value in utility_results.items():
                    if metric not in ['overall_utility', 'visualizations']:
                        st.write(f"**{metric.replace('_', ' ').title()}**: {value:.4f}")
                
                # Visualizations
                if 'visualizations' in utility_results:
                    st.subheader("Utility Visualizations")
                    for viz_name, viz_fig in utility_results['visualizations'].items():
                        st.write(f"**{viz_name}**")
                        st.plotly_chart(viz_fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error measuring utility: {str(e)}")

def show_reports():
    """Reports generation interface"""
    st.header("📋 Reports Generation")
    
    if not any([st.session_state.risk_results, st.session_state.utility_results]):
        st.warning("Please run risk assessment or utility measurement first.")
        return
    
    st.subheader("Generate Privacy-Utility Report")
    
    # Report configuration
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox("Report Type:", ["Executive Summary", "Technical Report", "Comprehensive Report"])
        report_format = st.selectbox("Format:", ["PDF", "HTML", "Both"])
    
    with col2:
        include_visualizations = st.checkbox("Include Visualizations", True)
        include_recommendations = st.checkbox("Include Recommendations", True)
    
    # Report metadata
    st.subheader("Report Metadata")
    report_title = st.text_input("Report Title:", "SafeData Privacy-Utility Analysis Report")
    organization = st.text_input("Organization:", "Government of India - Ministry of Electronics and IT")
    author = st.text_input("Author:", "SafeData Pipeline System")
    
    if st.button("Generate Report", type="primary"):
        with st.spinner("Generating report..."):
            try:
                report_data = {
                    'title': report_title,
                    'organization': organization,
                    'author': author,
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'data_info': {
                        'rows': len(st.session_state.data) if st.session_state.data is not None else 0,
                        'columns': len(st.session_state.data.columns) if st.session_state.data is not None else 0
                    },
                    'risk_results': st.session_state.risk_results,
                    'utility_results': st.session_state.utility_results,
                    'include_visualizations': include_visualizations,
                    'include_recommendations': include_recommendations
                }
                
                # Generate report based on format
                if report_format in ["PDF", "Both"]:
                    pdf_report = components['report_generator'].generate_pdf_report(
                        report_data, report_type
                    )
                    
                    st.success("✅ PDF report generated!")
                    
                    # Provide download link
                    b64_pdf = base64.b64encode(pdf_report).decode()
                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="SafeData_Report.pdf">Download PDF Report</a>'
                    st.markdown(href, unsafe_allow_html=True)
                
                if report_format in ["HTML", "Both"]:
                    html_report = components['report_generator'].generate_html_report(
                        report_data, report_type
                    )
                    
                    st.success("✅ HTML report generated!")
                    
                    # Display HTML report
                    with st.expander("View HTML Report", expanded=True):
                        import streamlit.components.v1 as components
                        components.html(html_report, height=600, scrolling=True)
                    
                    # Provide download link
                    b64_html = base64.b64encode(html_report.encode()).decode()
                    href = f'<a href="data:text/html;base64,{b64_html}" download="SafeData_Report.html">Download HTML Report</a>'
                    st.markdown(href, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")
    
    # Export processed data
    if st.session_state.processed_data is not None:
        st.subheader("Export Processed Data")
        
        export_format = st.selectbox("Export Format:", ["CSV", "Excel", "JSON", "Parquet"])
        
        if st.button("Export Data"):
            try:
                if export_format == "CSV":
                    csv = st.session_state.processed_data.to_csv(index=False)
                    st.download_button("Download CSV", csv, "processed_data.csv", "text/csv")
                
                elif export_format == "Excel":
                    buffer = io.BytesIO()
                    st.session_state.processed_data.to_excel(buffer, index=False)
                    st.download_button("Download Excel", buffer.getvalue(), "processed_data.xlsx", 
                                     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                
                elif export_format == "JSON":
                    json_str = st.session_state.processed_data.to_json(orient='records', indent=2)
                    st.download_button("Download JSON", json_str, "processed_data.json", "application/json")
                
                elif export_format == "Parquet":
                    buffer = io.BytesIO()
                    st.session_state.processed_data.to_parquet(buffer)
                    st.download_button("Download Parquet", buffer.getvalue(), "processed_data.parquet", 
                                     "application/octet-stream")
                
            except Exception as e:
                st.error(f"Error exporting data: {str(e)}")

def show_configuration():
    """Configuration management interface"""
    st.header("⚙️ Configuration Management")
    
    # Load privacy profiles
    try:
        with open('config/privacy_profiles.json', 'r') as f:
            privacy_profiles = json.load(f)
    except:
        privacy_profiles = {}
    
    st.subheader("Privacy Profiles")
    
    # Select existing profile
    if privacy_profiles:
        selected_profile = st.selectbox(
            "Load Existing Profile:",
            ["None"] + list(privacy_profiles.keys())
        )
        
        if selected_profile != "None" and st.button("Load Profile"):
            st.session_state.config = privacy_profiles[selected_profile]
            st.success(f"Profile '{selected_profile}' loaded!")
    
    # Create/Edit profile
    st.subheader("Create/Edit Profile")
    
    profile_name = st.text_input("Profile Name:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Risk Assessment Settings:**")
        k_threshold = st.slider("K-Anonymity Threshold:", 2, 20, 
                               st.session_state.config.get('k_threshold', 3))
        risk_level = st.selectbox("Risk Level:", ["Low", "Medium", "High"],
                                index=["Low", "Medium", "High"].index(st.session_state.config.get('risk_level', 'Medium')))
    
    with col2:
        st.write("**Privacy Enhancement Settings:**")
        privacy_technique = st.selectbox("Default Technique:", 
                                       ["K-Anonymity", "L-Diversity", "Differential Privacy"],
                                       index=0 if 'privacy_technique' not in st.session_state.config 
                                       else ["K-Anonymity", "L-Diversity", "Differential Privacy"].index(st.session_state.config['privacy_technique']))
        
        utility_threshold = st.slider("Minimum Utility Threshold:", 0.0, 1.0,
                                    st.session_state.config.get('utility_threshold', 0.7), 0.1)
    
    # Save profile
    if st.button("Save Profile") and profile_name:
        new_profile = {
            'k_threshold': k_threshold,
            'risk_level': risk_level,
            'privacy_technique': privacy_technique,
            'utility_threshold': utility_threshold,
            'created_date': datetime.now().isoformat()
        }
        
        privacy_profiles[profile_name] = new_profile
        
        # Save to file
        os.makedirs('config', exist_ok=True)
        with open('config/privacy_profiles.json', 'w') as f:
            json.dump(privacy_profiles, f, indent=2)
        
        st.success(f"Profile '{profile_name}' saved!")
    
    # System configuration
    st.subheader("System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_file_size = st.number_input("Max File Size (MB):", 1, 1000, 100)
        chunk_size = st.number_input("Processing Chunk Size:", 1000, 100000, 10000)
    
    with col2:
        enable_encryption = st.checkbox("Enable Data Encryption", True)
        enable_logging = st.checkbox("Enable Detailed Logging", True)
    
    if st.button("Save System Configuration"):
        system_config = {
            'max_file_size': max_file_size,
            'chunk_size': chunk_size,
            'enable_encryption': enable_encryption,
            'enable_logging': enable_logging
        }
        
        with open('config/system_config.json', 'w') as f:
            json.dump(system_config, f, indent=2)
        
        st.success("System configuration saved!")

def show_help():
    """Help and documentation interface"""
    st.header("❓ Help & Documentation")
    
    # Load guide content
    try:
        with open('guide.txt', 'r', encoding='utf-8') as f:
            guide_content = f.read()
    except:
        guide_content = "Guide file not found."
    
    # Help topics
    help_topic = st.selectbox(
        "Select Help Topic:",
        ["Quick Start Guide", "Data Upload", "Risk Assessment", "Privacy Enhancement", 
         "Utility Measurement", "Report Generation", "Configuration", "Troubleshooting", "API Reference"]
    )
    
    if help_topic == "Quick Start Guide":
        st.markdown("""
        ## Quick Start Guide
        
        ### Step 1: Upload Data
        1. Go to the **Data Upload** page
        2. Select your data file (CSV, Excel, JSON, XML, or Parquet)
        3. Review the data preview and quality assessment
        4. Apply automatic fixes if needed
        
        ### Step 2: Assess Risk
        1. Navigate to **Risk Assessment**
        2. Select quasi-identifiers and sensitive attributes
        3. Configure risk parameters
        4. Run the assessment to identify vulnerabilities
        
        ### Step 3: Apply Privacy Enhancement
        1. Choose a privacy technique in **Privacy Enhancement**
        2. Configure parameters based on your requirements
        3. Apply the selected technique to your data
        4. Review the before/after comparison
        
        ### Step 4: Measure Utility
        1. Go to **Utility Measurement**
        2. Select relevant utility metrics
        3. Run the analysis to evaluate data quality preservation
        
        ### Step 5: Generate Reports
        1. Visit the **Reports** section
        2. Configure report settings
        3. Generate PDF or HTML reports
        4. Export processed data in your preferred format
        """)
    
    elif help_topic == "Data Upload":
        st.markdown("""
        ## Data Upload Guide
        
        ### Supported File Formats
        - **CSV**: Comma-separated values
        - **Excel**: .xlsx and .xls files
        - **JSON**: JavaScript Object Notation
        - **XML**: Extensible Markup Language
        - **Parquet**: Columnar storage format
        
        ### Data Quality Checks
        The system automatically performs:
        - Missing value detection
        - Data type validation
        - Consistency checks
        - Format validation
        
        ### Automatic Data Repair
        Available fixes include:
        - Missing value imputation
        - Data type conversion
        - Encoding correction
        - Format standardization
        """)
    
    elif help_topic == "Troubleshooting":
        st.markdown("""
        ## Troubleshooting
        
        ### Common Issues
        
        **File Upload Errors**
        - Ensure file format is supported
        - Check file size limits
        - Verify file is not corrupted
        
        **Memory Issues**
        - Use smaller datasets for testing
        - Enable chunked processing
        - Close other applications
        
        **Privacy Enhancement Failures**
        - Verify quasi-identifiers are selected
        - Check parameter ranges
        - Ensure sufficient data diversity
        
        **Report Generation Issues**
        - Complete all required analyses first
        - Check report configuration
        - Verify template files exist
        
        ### Getting Help
        - Check the guide.txt file for detailed documentation
        - Review error messages carefully
        - Contact system administrator for technical support
        """)
    
    # Show guide content
    st.subheader("Complete User Guide")
    with st.expander("View Complete Guide", expanded=False):
        st.text(guide_content)

def load_sample_config():
    """Load sample configuration"""
    sample_config = {
        'k_threshold': 3,
        'risk_level': 'Medium',
        'privacy_technique': 'K-Anonymity',
        'utility_threshold': 0.7
    }
    st.session_state.config = sample_config
    st.success("Sample configuration loaded!")

def clear_session_data():
    """Clear all session data"""
    st.session_state.data = None
    st.session_state.processed_data = None
    st.session_state.risk_results = None
    st.session_state.utility_results = None
    st.session_state.config = {}
    st.success("All data cleared!")
    st.rerun()

if __name__ == "__main__":
    main()
