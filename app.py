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
import streamlit.components.v1 as stc

# Configure page
st.set_page_config(
    page_title="SafeData Pipeline - Government of India",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Display external URL information for Replit deployment
if 'REPL_SLUG' in os.environ:
    repl_slug = os.environ.get('REPL_SLUG', 'workspace')
    repl_owner = os.environ.get('REPL_OWNER', 'fitnessanddietm') 
    external_url = f"https://{repl_slug}.{repl_owner}.repl.co"
    st.sidebar.info(f"🌐 External Access: {external_url}")
    print(f"SafeData Pipeline is accessible at: {external_url}")

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
                    stat_sim = utility_results.get('statistical_similarity', {})
                    stat_val = stat_sim.get('overall', 0) if isinstance(stat_sim, dict) else stat_sim
                    st.metric("Statistical Similarity", f"{stat_val:.3f}")
                with col3:
                    info_loss = utility_results.get('information_loss', {})
                    info_val = info_loss.get('information_preservation', 0) if isinstance(info_loss, dict) else info_loss
                    st.metric("Information Preservation", f"{info_val:.3f}")
                
                # Detailed metrics
                st.subheader("Detailed Utility Metrics")
                
                for metric, value in utility_results.items():
                    if metric not in ['overall_utility', 'visualizations', 'metrics_computed', 'dataset_sizes', 'utility_level', 'recommendations']:
                        if isinstance(value, (int, float)):
                            st.write(f"**{metric.replace('_', ' ').title()}**: {value:.4f}")
                        elif isinstance(value, dict) and 'overall' in value:
                            st.write(f"**{metric.replace('_', ' ').title()}**: {value['overall']:.4f}")
                        else:
                            st.write(f"**{metric.replace('_', ' ').title()}**: {str(value)}")
                
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
                        stc.html(html_report, height=600, scrolling=True)
                    
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
        - **CSV**: Comma-separated values with automatic encoding detection
        - **Excel**: .xlsx and .xls files with multi-sheet support
        - **JSON**: JavaScript Object Notation with nested structure handling
        - **XML**: Extensible Markup Language with automatic structure detection
        - **Parquet**: Columnar storage format for big data
        - **TSV**: Tab-separated values
        
        ### File Upload Process
        1. **File Selection**: Click "Choose a file" and select your dataset
        2. **Automatic Loading**: System detects file type and loads data
        3. **Encoding Detection**: Automatic character encoding identification
        4. **Structure Analysis**: Column identification and data type inference
        5. **Preview Generation**: First 10 rows displayed for verification
        
        ### Data Quality Assessment
        The system automatically evaluates:
        - **Completeness**: Percentage of missing values per column
        - **Consistency**: Data type uniformity and format consistency
        - **Validity**: Range checks and format validation
        - **Overall Quality Score**: Composite score from 0-100%
        
        #### Quality Metrics Explained:
        - **Quality Score**: Overall data health (>90% excellent, 70-90% good, 50-70% fair, <50% poor)
        - **Completeness**: (Total cells - Missing cells) / Total cells × 100%
        - **Consistency**: Uniform data types and formats across columns
        - **Validity**: Values within expected ranges and proper formats
        
        ### Data Quality Issues Detection
        Common issues automatically identified:
        - **Missing Values**: Empty or null cells requiring imputation
        - **Mixed Data Types**: Numeric data stored as text strings
        - **Inconsistent Formats**: Varying date formats within columns
        - **Extreme Outliers**: Values beyond 3× interquartile range
        - **Negative Values**: In columns expecting positive values (age, count, etc.)
        - **Duplicate Rows**: Identical records that may need removal
        
        ### Automatic Data Repair Features
        **PyArrow Compatibility Fixes**:
        - Converts nullable integer types to standard numpy types
        - Handles mixed data types in object columns
        - Fixes timezone-aware datetime issues
        - Resolves complex object serialization problems
        
        **Data Type Corrections**:
        - **Numeric Conversion**: Converts "123", "$1,234" to proper numbers
        - **Date Standardization**: Unifies various date formats (YYYY-MM-DD, MM/DD/YYYY, etc.)
        - **Boolean Mapping**: Converts "yes/no", "true/false", "1/0" to boolean
        - **Text Cleaning**: Removes non-printable characters and standardizes case
        
        **Missing Value Imputation**:
        - **Numeric Columns**: Uses median for robust central tendency
        - **Categorical Columns**: Uses mode (most frequent value)
        - **Fallback**: Uses "Unknown" for categories without clear mode
        
        **Column Name Cleaning**:
        - Removes special characters and replaces with underscores
        - Handles duplicate column names by adding numeric suffixes
        - Ensures compatibility with analysis modules
        
        ### File Size and Performance
        - **Maximum File Size**: 100MB (configurable)
        - **Chunked Processing**: Large files processed in 10,000-row chunks
        - **Memory Optimization**: Efficient data types to reduce memory usage
        - **Progress Tracking**: Real-time feedback during large file processing
        
        ### Best Practices
        - **Clean Headers**: Use descriptive column names without special characters
        - **Consistent Formatting**: Maintain uniform date and number formats
        - **Complete Records**: Minimize missing values where possible
        - **Reasonable Size**: Start with smaller datasets for testing
        - **Backup Original**: Keep original files before applying fixes
        """)
    
    elif help_topic == "Risk Assessment":
        st.markdown("""
        ## Risk Assessment Guide
        
        ### Overview
        Risk assessment evaluates the re-identification risk of your dataset by simulating various attack scenarios and measuring anonymity levels.
        
        ### Key Concepts
        **Quasi-Identifiers (QIDs)**:
        - Attributes that can be linked to external data for re-identification
        - Examples: Age, Gender, ZIP code, Education level, Job title
        - NOT direct identifiers like names, SSNs, email addresses
        - NOT sensitive attributes you want to protect
        
        **Sensitive Attributes**:
        - Information you want to keep private and protected
        - Examples: Medical conditions, Salary, Political affiliation, Sexual orientation
        - These should NOT be used as quasi-identifiers
        
        ### Configuration Options
        
        #### Quasi-Identifier Selection
        - **Purpose**: Select columns that could be used to re-identify individuals
        - **Guidelines**: 
          - Include demographic information (age, gender, location)
          - Include publicly available attributes
          - Exclude direct identifiers and sensitive information
        - **Examples**: Age, Gender, ZIP_Code, Education_Level, Occupation
        
        #### Sensitive Attribute Selection
        - **Purpose**: Identify information requiring protection
        - **Guidelines**: 
          - Private health information
          - Financial data
          - Personal preferences
        - **Examples**: Medical_Condition, Income, Political_Party
        
        #### K-Anonymity Threshold
        - **Range**: 2-20 (default: 3)
        - **Meaning**: Minimum group size for each combination of quasi-identifiers
        - **Interpretation**:
          - K=3: Each person is indistinguishable from at least 2 others
          - K=5: Higher privacy, each person in group of 5+ with same QIDs
          - K=10+: Very high privacy but may reduce data utility
        
        #### Sample Size for Assessment
        - **Range**: 10-100% (default: 50%)
        - **Purpose**: Percentage of data to analyze (for performance)
        - **Guidelines**:
          - Large datasets: Use 10-30% for faster analysis
          - Small datasets: Use 100% for complete assessment
          - Critical applications: Always use 100%
        
        #### Attack Scenarios
        **Prosecutor Attack**:
        - Assumes attacker knows target is in dataset
        - Measures worst-case re-identification risk
        - Most conservative and commonly used
        
        **Journalist Attack**:
        - Assumes attacker suspects target might be in dataset
        - Considers probability that target exists in data
        - More realistic for general scenarios
        
        **Marketer Attack**:
        - Assumes attacker wants to find anyone matching profile
        - Focuses on population statistics rather than individuals
        - Relevant for marketing and research applications
        
        ### Risk Metrics Explained
        
        **Overall Risk Score**:
        - Scale: 0.0 (no risk) to 1.0 (maximum risk)
        - Interpretation:
          - 0.0-0.2: Low risk (acceptable for most uses)
          - 0.2-0.5: Medium risk (requires privacy enhancement)
          - 0.5-0.8: High risk (significant privacy concerns)
          - 0.8-1.0: Critical risk (urgent action required)
        
        **K-Anonymity Violations**:
        - Number of equivalence classes with fewer than K records
        - Zero violations = full K-anonymity achieved
        - High violations = many individuals easily identifiable
        
        **Unique Records**:
        - Records with unique combination of quasi-identifiers
        - These individuals are highly re-identifiable
        - Should be minimized through anonymization
        
        **Risk Level Categories**:
        - **Low**: Safe for sharing with minimal restrictions
        - **Medium**: Suitable for research with data use agreements
        - **High**: Requires anonymization before sharing
        - **Critical**: Should not be shared without strong privacy measures
        
        ### Equivalence Classes Analysis
        Shows groups of records with identical quasi-identifier values:
        - **Class Size**: Number of records in each group
        - **Frequency**: How common each combination is
        - **Risk Score**: Re-identification probability for each class
        
        ### Recommendations System
        Based on assessment results, system provides:
        - **Immediate Actions**: Quick fixes to reduce obvious risks
        - **Privacy Techniques**: Suggested anonymization methods
        - **Parameter Guidance**: Recommended K values and techniques
        - **Utility Trade-offs**: Expected impact on data usefulness
        
        ### Best Practices
        - **Start Conservative**: Begin with higher K values (5-10)
        - **Iterate**: Run multiple assessments with different parameters
        - **Consider Context**: Higher risk tolerance for internal use vs. public sharing
        - **Document Decisions**: Record rationale for quasi-identifier selection
        - **Regular Re-assessment**: Evaluate risk after any data changes
        """)
    
    elif help_topic == "Privacy Enhancement":
        st.markdown("""
        ## Privacy Enhancement Guide
        
        ### Overview
        Privacy enhancement applies anonymization techniques to protect individual privacy while preserving data utility for analysis.
        
        ### Available Techniques
        
        #### K-Anonymity
        **Purpose**: Ensures each person is indistinguishable from at least K-1 others
        
        **Configuration Options**:
        - **K Value** (2-20): Minimum group size for anonymity
          - K=3: Basic privacy, faster processing
          - K=5: Balanced privacy and utility
          - K=10+: High privacy, may impact utility
        
        - **Generalization Method**:
          - **Global Recoding**: Same generalization rules applied to entire dataset
            - Pros: Consistent, simple to understand
            - Cons: May over-generalize some regions
            - Best for: Uniform datasets, regulatory compliance
          
          - **Local Recoding**: Different rules for different parts of dataset
            - Pros: Better utility preservation, adaptive
            - Cons: More complex, potential inconsistencies
            - Best for: Diverse datasets, research applications
          
          - **Clustering**: Groups similar records before generalization
            - Pros: Natural groupings, good utility
            - Cons: Complex algorithm, longer processing
            - Best for: Large datasets, complex relationships
        
        - **Suppression Limit** (0-50%): Maximum percentage of records to remove
          - 0-10%: Minimal data loss, may not achieve anonymity
          - 10-25%: Balanced approach for most applications
          - 25-50%: High privacy, significant data loss
        
        **Generalization Examples**:
        - Age: 25 → 20-30, 35 → 30-40
        - ZIP Code: 12345 → 123**, 67890 → 678**
        - Salary: $45,000 → $40,000-$50,000
        
        #### L-Diversity
        **Purpose**: Ensures sensitive attributes have at least L different values in each group
        
        **Configuration Options**:
        - **L Value** (2-10): Minimum diversity in sensitive attributes
          - L=2: Basic diversity protection
          - L=3-5: Good balance for most applications
          - L=6+: High diversity, may require larger datasets
        
        - **Diversity Methods**:
          - **Distinct L-Diversity**: At least L different values present
            - Simple, fast computation
            - May not address skewed distributions
          
          - **Entropy L-Diversity**: Measures information content
            - Accounts for value distribution
            - More robust against skewed data
          
          - **Recursive L-Diversity**: Prevents dominance by single value
            - Strongest protection against attribute disclosure
            - Most complex to compute
        
        **Example**: Medical dataset with diagnosis as sensitive attribute
        - Each age group must contain at least L different diagnoses
        - Prevents inferring diagnosis from demographic information
        
        #### T-Closeness
        **Purpose**: Ensures sensitive attribute distribution in each group is close to overall distribution
        
        **Configuration Options**:
        - **T Value** (0.1-1.0): Maximum allowed distance from global distribution
          - T=0.1: Very close to global distribution, high utility
          - T=0.3: Balanced privacy and utility
          - T=0.5+: Strong privacy, may impact analysis
        
        - **Distance Measures**:
          - **Earth Mover's Distance**: Optimal for numerical attributes
          - **Variational Distance**: Better for categorical attributes
        
        **Benefits**: Prevents attribute disclosure while maintaining statistical properties
        
        #### Differential Privacy
        **Purpose**: Provides mathematical guarantee that individual participation doesn't significantly affect results
        
        **Configuration Options**:
        - **Epsilon (ε)** (0.1-10.0): Privacy budget
          - ε < 1.0: Strong privacy, more noise
          - ε = 1.0: Balanced approach
          - ε > 2.0: Weaker privacy, less noise
        
        - **Noise Distribution**:
          - **Laplace**: Standard for most applications
          - **Gaussian**: Better for complex queries
        
        - **Sensitivity**: How much one record can change the result
          - Automatically calculated based on query type
          - Affects amount of noise added
        
        **Applications**: Statistical queries, machine learning, research studies
        
        #### Synthetic Data Generation
        **Purpose**: Creates artificial dataset with similar statistical properties
        
        **Methods**:
        - **Marginal Distributions**: Preserves column-wise statistics
        - **Correlation Preservation**: Maintains relationships between variables
        - **Deep Learning**: Uses neural networks for complex patterns
        
        **Advantages**: Complete privacy, unlimited sharing, no suppression
        **Considerations**: May not capture all data nuances
        
        ### Before/After Comparison
        
        The system provides comprehensive comparison:
        - **Row Count Changes**: Track any record suppression
        - **Column Modifications**: See which attributes were generalized
        - **Value Transformations**: Understand specific changes made
        - **Statistical Comparison**: Compare means, distributions, correlations
        
        ### Best Practices
        
        #### Technique Selection
        - **K-Anonymity**: Basic anonymization, regulatory compliance
        - **L-Diversity**: When protecting sensitive attributes
        - **T-Closeness**: Research requiring statistical accuracy
        - **Differential Privacy**: Strong mathematical guarantees needed
        - **Synthetic Data**: Maximum sharing flexibility required
        
        #### Parameter Guidelines
        - Start with conservative values and adjust based on utility needs
        - Consider your data sharing context (internal vs. public)
        - Balance privacy requirements with analytical needs
        - Test multiple approaches to find optimal settings
        
        #### Quality Assurance
        - Always review before/after comparison
        - Verify anonymization goals are met
        - Check that essential relationships are preserved
        - Validate results with domain experts
        """)
    
    elif help_topic == "Utility Measurement":
        st.markdown("""
        ## Utility Measurement Guide
        
        ### Overview
        Utility measurement evaluates how well the anonymized data preserves the analytical value of the original dataset.
        
        ### Available Metrics
        
        #### Statistical Similarity
        **Purpose**: Measures how closely anonymized data matches original statistical properties
        
        **Components**:
        - **Mean Preservation**: Difference in column averages
        - **Standard Deviation**: Variability preservation
        - **Distribution Shape**: Skewness and kurtosis comparison
        - **Range Preservation**: Min/max value retention
        
        **Scoring**:
        - 1.0: Perfect preservation (identical statistics)
        - 0.8-1.0: Excellent preservation
        - 0.6-0.8: Good preservation
        - 0.4-0.6: Fair preservation
        - <0.4: Poor preservation
        
        **Interpretation**: Higher scores indicate better preservation of basic statistical properties
        
        #### Correlation Preservation
        **Purpose**: Evaluates whether relationships between variables are maintained
        
        **Analysis**:
        - Compares correlation matrices between original and anonymized data
        - Measures preservation of linear relationships
        - Identifies which variable pairs are most affected
        
        **Applications**:
        - Critical for regression analysis
        - Important for data mining applications
        - Essential for research studies
        
        **Calculation**: Correlation coefficient between original and anonymized correlation values
        
        #### Distribution Similarity
        **Purpose**: Assesses whether data distributions remain similar after anonymization
        
        **Methods**:
        **Numerical Columns**:
        - **Kolmogorov-Smirnov Test**: Tests if distributions come from same population
        - **Wasserstein Distance**: Measures "effort" to transform one distribution to another
        - Combined score provides robust distribution comparison
        
        **Categorical Columns**:
        - **Chi-Square Test**: Compares frequency distributions
        - **Normalized Frequency Comparison**: Direct proportion comparison
        
        **Interpretation**:
        - 1.0: Identical distributions
        - 0.8+: Very similar distributions
        - 0.6-0.8: Moderately similar
        - <0.6: Significantly different distributions
        
        #### Information Loss
        **Purpose**: Quantifies how much information content is lost during anonymization
        
        **Entropy-Based Measurement**:
        - Calculates information entropy for each column
        - Compares original vs. anonymized entropy levels
        - Higher entropy = more information content
        
        **Mutual Information Loss**:
        - Measures how much information variables share
        - Identifies relationships that are lost or weakened
        - Critical for maintaining data interdependencies
        
        **Components**:
        - **Overall Entropy Loss**: Average information loss across all columns
        - **Information Preservation**: 1 - Entropy Loss (higher is better)
        - **Mutual Information Loss**: Relationship preservation between variable pairs
        
        #### Classification Utility
        **Purpose**: Evaluates whether anonymized data maintains predictive power
        
        **Process**:
        1. Identifies potential target variables (categorical with reasonable class distribution)
        2. Trains machine learning models on original data
        3. Tests models on anonymized data
        4. Compares prediction accuracy
        
        **Models Used**:
        - Random Forest Classifier for categorical targets
        - Random Forest Regressor for numerical targets
        
        **Metrics**:
        - **Accuracy Preservation**: How well models perform on anonymized data
        - **Feature Importance**: Which variables remain most predictive
        - **Model Transferability**: Whether insights transfer to anonymized data
        
        #### Query Accuracy
        **Purpose**: Tests whether common analytical queries produce similar results
        
        **Query Types**:
        - **Aggregate Queries**: SUM, COUNT, AVERAGE across different groupings
        - **Filtering Operations**: WHERE clauses with various conditions
        - **Grouping Operations**: GROUP BY with statistical functions
        
        **Accuracy Measurement**:
        - Executes same queries on original and anonymized data
        - Compares results using relative error metrics
        - Provides query-specific utility scores
        
        ### Overall Utility Score
        
        **Calculation**: Weighted average of all selected metrics
        **Weighting**: Equal weights by default, customizable based on application needs
        
        **Interpretation Scale**:
        - **0.9-1.0**: Excellent utility (minimal impact on analysis)
        - **0.7-0.9**: Good utility (suitable for most applications)
        - **0.5-0.7**: Fair utility (may impact some analyses)
        - **0.3-0.5**: Poor utility (significant limitations)
        - **<0.3**: Very poor utility (major analytical concerns)
        
        ### Visualizations
        
        #### Utility Radar Chart
        - Displays all utility metrics on single chart
        - Easy visual comparison of different aspects
        - Helps identify strongest and weakest preservation areas
        
        #### Distribution Comparison Plots
        - Side-by-side histograms for numerical columns
        - Shows shape changes in data distributions
        - Up to 4 most important columns displayed
        
        #### Correlation Heatmaps
        - Original vs. anonymized correlation matrices
        - Color-coded to show relationship strength
        - Easy identification of lost correlations
        
        #### Utility Scores Bar Chart
        - Detailed breakdown of individual utility components
        - Helps prioritize improvement areas
        - Useful for technical reporting
        
        ### Utility Level Assessment
        
        **Automatic Classification**:
        Based on overall utility score, data is classified as:
        - **Excellent**: >0.9 - Ready for most analytical applications
        - **Good**: 0.7-0.9 - Suitable for general research and reporting
        - **Fair**: 0.5-0.7 - Acceptable for basic statistics and trends
        - **Poor**: <0.5 - Limited analytical value, consider different approach
        
        ### Recommendations System
        
        **Automatic Suggestions**:
        - **High Information Loss**: Consider synthetic data generation
        - **Poor Correlation Preservation**: Try T-closeness or adjust K values
        - **Distribution Changes**: Use local recoding instead of global
        - **Low Classification Utility**: Reduce suppression limits
        
        ### Best Practices
        
        #### Metric Selection
        - **Research Applications**: Focus on statistical similarity and correlation preservation
        - **Machine Learning**: Emphasize classification utility and information preservation
        - **Business Intelligence**: Prioritize query accuracy and distribution similarity
        - **Compliance Reporting**: Include all metrics for comprehensive assessment
        
        #### Interpretation Guidelines
        - No single metric tells the complete story
        - Consider your specific use case requirements
        - Balance privacy needs with utility requirements
        - Document trade-offs for stakeholder communication
        
        #### Optimization Strategy
        - Start with baseline measurements
        - Adjust anonymization parameters iteratively
        - Focus on metrics most critical to your application
        - Consider multiple anonymization approaches if utility is insufficient
        """)
    
    elif help_topic == "Report Generation":
        st.markdown("""
        ## Report Generation Guide
        
        ### Overview
        The report generation module creates comprehensive documentation of your privacy-utility analysis for stakeholders, compliance, and decision-making.
        
        ### Report Types
        
        #### Executive Summary
        **Target Audience**: Senior management, decision makers, non-technical stakeholders
        
        **Content Includes**:
        - **High-level Overview**: Project purpose and scope
        - **Key Findings**: Main privacy and utility results
        - **Risk Assessment Summary**: Overall risk level and critical issues
        - **Recommendations**: Actionable next steps
        - **Business Impact**: Implications for data sharing and usage
        
        **Length**: 2-4 pages, focus on insights rather than technical details
        **Language**: Business-friendly, minimal technical jargon
        
        #### Technical Report
        **Target Audience**: Data scientists, privacy engineers, technical teams
        
        **Content Includes**:
        - **Methodology Details**: Algorithms and parameters used
        - **Detailed Metrics**: Complete statistical analysis
        - **Technical Configurations**: All parameter settings and choices
        - **Implementation Notes**: Technical considerations and limitations
        - **Validation Results**: Quality assurance and testing outcomes
        
        **Length**: 10-20 pages, comprehensive technical documentation
        **Language**: Technical terminology, detailed explanations
        
        #### Comprehensive Report
        **Target Audience**: Mixed audience, compliance documentation, archival purposes
        
        **Content Includes**:
        - **Executive Summary**: High-level overview for management
        - **Technical Details**: Complete methodology and results
        - **Regulatory Compliance**: Alignment with privacy frameworks
        - **Appendices**: Raw data, detailed tables, supplementary analysis
        - **Audit Trail**: Complete record of all processing steps
        
        **Length**: 15-30 pages, complete documentation
        **Language**: Mixed levels, sections tailored to different audiences
        
        ### Output Formats
        
        #### PDF Reports
        **Advantages**:
        - Professional appearance for formal distribution
        - Consistent formatting across different systems
        - Suitable for printing and official documentation
        - Easy to share and archive
        
        **Features**:
        - **Table of Contents**: Automatic navigation
        - **Professional Layout**: Government-compliant formatting
        - **High-Quality Visuals**: Vector graphics for charts
        - **Metadata**: Document properties and creation info
        
        **Best For**: Compliance documentation, stakeholder presentations, official records
        
        #### HTML Reports
        **Advantages**:
        - Interactive visualizations and charts
        - Easy web sharing and collaboration
        - Responsive design for different screen sizes
        - Searchable content
        
        **Features**:
        - **Interactive Charts**: Hover details, zooming, filtering
        - **Collapsible Sections**: Expandable content areas
        - **Hyperlinked Navigation**: Quick section jumping
        - **Modern Styling**: Clean, professional appearance
        
        **Best For**: Internal sharing, technical review, collaborative analysis
        
        #### Both Formats
        - Provides flexibility for different use cases
        - PDF for formal distribution, HTML for working sessions
        - Ensures broad compatibility with stakeholder preferences
        
        ### Report Configuration Options
        
        #### Include Visualizations
        **Charts and Graphs**:
        - Risk assessment radar charts
        - Utility comparison plots
        - Distribution histograms
        - Correlation heatmaps
        - Before/after comparisons
        
        **Benefits**: Visual communication of complex results
        **Considerations**: Increases file size, may affect printing
        
        #### Include Recommendations
        **Recommendation Types**:
        - **Privacy Improvements**: Suggested anonymization adjustments
        - **Utility Optimization**: Ways to preserve more analytical value
        - **Implementation Guidance**: Practical next steps
        - **Risk Mitigation**: Actions to address identified vulnerabilities
        
        **AI-Generated Insights**: System provides intelligent recommendations based on analysis results
        
        ### Report Metadata
        
        #### Report Title
        - Default: "SafeData Privacy-Utility Analysis Report"
        - Customizable for specific projects or datasets
        - Should clearly identify the analysis scope
        
        #### Organization
        - Default: "Government of India - Ministry of Electronics and IT"
        - Customizable for different departments or agencies
        - Appears in header and document properties
        
        #### Author Information
        - Default: "SafeData Pipeline System"
        - Can specify individual analyst or team
        - Important for accountability and contact purposes
        
        ### Report Contents in Detail
        
        #### Dataset Information
        - **Source Details**: File name, upload date, size
        - **Structure Summary**: Number of rows, columns, data types
        - **Quality Assessment**: Completeness, consistency, validity scores
        - **Issues Identified**: Problems found and fixes applied
        
        #### Risk Assessment Results
        - **Overall Risk Score**: Numerical score and interpretation
        - **K-Anonymity Analysis**: Violations and equivalence classes
        - **Attack Scenarios**: Results from different attack simulations
        - **Vulnerability Assessment**: Specific re-identification risks
        - **Compliance Status**: Alignment with privacy requirements
        
        #### Privacy Enhancement Summary
        - **Technique Applied**: Method used and configuration
        - **Parameter Settings**: All anonymization parameters
        - **Processing Results**: Success metrics and any issues
        - **Data Transformation**: Summary of changes made
        - **Before/After Comparison**: Statistical changes documented
        
        #### Utility Measurement Results
        - **Overall Utility Score**: Composite preservation measure
        - **Individual Metrics**: Detailed breakdown by utility type
        - **Visualizations**: Charts showing utility preservation
        - **Critical Findings**: Most significant utility impacts
        - **Recommendations**: Suggestions for utility improvement
        
        #### Technical Appendices
        - **Configuration Files**: Complete parameter settings
        - **Statistical Tables**: Detailed numerical results
        - **Quality Metrics**: Comprehensive data quality assessment
        - **Processing Log**: Timeline of all operations performed
        
        ### Best Practices
        
        #### Report Planning
        - **Define Audience**: Tailor content and language appropriately
        - **Set Objectives**: Clear purpose for report generation
        - **Choose Format**: Consider distribution and usage requirements
        - **Include Context**: Explain business or research context
        
        #### Content Guidelines
        - **Executive Summary First**: Lead with key findings
        - **Progressive Detail**: Layer information by complexity
        - **Visual Communication**: Use charts to explain complex concepts
        - **Action-Oriented**: Focus on decisions and next steps
        
        #### Quality Assurance
        - **Review All Sections**: Ensure completeness and accuracy
        - **Validate Visualizations**: Check that charts support conclusions
        - **Check Formatting**: Ensure professional appearance
        - **Test Distribution**: Verify reports work on target systems
        
        #### Compliance Considerations
        - **Documentation Standards**: Follow organizational requirements
        - **Retention Policies**: Consider long-term archival needs
        - **Distribution Controls**: Manage access to sensitive analysis
        - **Audit Requirements**: Include necessary tracking information
        """)
    
    elif help_topic == "Configuration":
        st.markdown("""
        ## Configuration Guide
        
        ### Overview
        The configuration module allows customization of system settings, privacy profiles, and operational parameters for different use cases and organizational requirements.
        
        ### Privacy Profiles
        
        #### Purpose
        Privacy profiles provide pre-configured settings for common anonymization scenarios, enabling:
        - **Consistent Application**: Same privacy standards across projects
        - **Quick Setup**: Reduced configuration time for routine tasks
        - **Best Practice Templates**: Proven parameter combinations
        - **Organizational Standards**: Enforcement of institutional policies
        
        #### Default Profiles Available
        **Low Risk Profile**:
        - K-Threshold: 3
        - Risk Level: Medium tolerance
        - Privacy Technique: K-Anonymity with global recoding
        - Utility Threshold: 0.8 (prioritizes data usefulness)
        - **Use Cases**: Internal research, preliminary analysis, development
        
        **Medium Risk Profile**:
        - K-Threshold: 5
        - Risk Level: Low tolerance
        - Privacy Technique: L-Diversity
        - Utility Threshold: 0.7 (balanced approach)
        - **Use Cases**: Departmental sharing, controlled research, business intelligence
        
        **High Risk Profile**:
        - K-Threshold: 10
        - Risk Level: Very low tolerance
        - Privacy Technique: T-Closeness or Differential Privacy
        - Utility Threshold: 0.6 (privacy prioritized)
        - **Use Cases**: Public release, external partnerships, regulatory compliance
        
        #### Profile Configuration Options
        
        **K-Threshold (2-20)**:
        - **2-3**: Minimal anonymization, fastest processing
        - **4-7**: Standard protection for most internal uses
        - **8-15**: High protection for sensitive data
        - **16-20**: Maximum protection, may significantly impact utility
        
        **Risk Level Tolerance**:
        - **High**: Accept more risk for better utility (internal use)
        - **Medium**: Balanced approach for most applications
        - **Low**: Conservative approach for sensitive data
        - **Very Low**: Maximum protection for public release
        
        **Default Privacy Technique**:
        - **K-Anonymity**: Fast, simple, good for basic protection
        - **L-Diversity**: Better protection of sensitive attributes
        - **T-Closeness**: Statistical accuracy preservation
        - **Differential Privacy**: Mathematical privacy guarantees
        
        **Utility Threshold (0.0-1.0)**:
        - **0.9+**: Requires excellent utility preservation
        - **0.7-0.9**: Good utility acceptable
        - **0.5-0.7**: Fair utility acceptable
        - **<0.5**: Poor utility acceptable (maximum privacy)
        
        #### Creating Custom Profiles
        
        **Profile Creation Process**:
        1. **Name Your Profile**: Descriptive name for easy identification
        2. **Set Parameters**: Configure all privacy and utility settings
        3. **Test Configuration**: Run sample analysis to validate settings
        4. **Save Profile**: Store for future use and sharing
        5. **Document Rationale**: Record why specific settings were chosen
        
        **Profile Management**:
        - **Load Existing**: Apply saved profiles to new projects
        - **Modify Settings**: Update profiles as requirements change
        - **Share Profiles**: Export for use by other team members
        - **Version Control**: Track changes and maintain profile history
        
        ### System Configuration
        
        #### Performance Settings
        
        **Maximum File Size (1-1000 MB)**:
        - **Default**: 100 MB
        - **Small Organizations**: 50 MB (faster processing)
        - **Large Datasets**: 500+ MB (requires more memory)
        - **Considerations**: Balance capability with system resources
        
        **Processing Chunk Size (1,000-100,000 rows)**:
        - **Default**: 10,000 rows
        - **Small Memory**: 5,000 rows (reduced memory usage)
        - **Large Memory**: 50,000+ rows (faster processing)
        - **Complex Operations**: Smaller chunks for stability
        
        **Memory Management**:
        - **Conservative**: Use smaller chunks and files for stability
        - **Aggressive**: Maximize performance with larger chunks
        - **Adaptive**: System automatically adjusts based on available resources
        
        #### Security Settings
        
        **Enable Data Encryption**:
        - **Purpose**: Protects data in memory and temporary storage
        - **When to Enable**: Always for production environments
        - **Performance Impact**: Minimal overhead for strong protection
        - **Compliance**: May be required for regulatory adherence
        
        **Encryption Features**:
        - **At-Rest**: Temporary files encrypted on disk
        - **In-Memory**: Sensitive data encrypted in system memory
        - **Transport**: Secure data transfer between components
        - **Key Management**: Automatic key generation and rotation
        
        #### Logging Configuration
        
        **Enable Detailed Logging**:
        - **Purpose**: Comprehensive audit trail and debugging information
        - **Benefits**: 
          - Problem diagnosis and troubleshooting
          - Performance monitoring and optimization
          - Compliance and audit requirements
          - Security incident investigation
        
        **Log Levels**:
        - **ERROR**: Only critical issues and failures
        - **WARN**: Problems that don't stop processing
        - **INFO**: General processing information (default)
        - **DEBUG**: Detailed technical information
        
        **Log Contents**:
        - **Processing Steps**: Each operation performed
        - **Parameter Settings**: All configuration choices
        - **Performance Metrics**: Timing and resource usage
        - **Quality Results**: Data quality and utility measurements
        - **Error Details**: Complete error messages and stack traces
        
        #### Storage and Backup
        
        **Temporary File Management**:
        - **Location**: Configurable temp directory
        - **Cleanup Policy**: Automatic deletion after processing
        - **Retention**: Option to keep intermediate files for debugging
        - **Encryption**: All temporary files encrypted when security enabled
        
        **Configuration Backup**:
        - **Profile Export**: Save privacy profiles to external files
        - **System Settings**: Backup all configuration parameters
        - **Recovery**: Restore from backup files if needed
        - **Migration**: Transfer settings between systems
        
        ### Advanced Configuration
        
        #### Algorithm Parameters
        
        **Generalization Hierarchies**:
        - **Automatic**: System generates appropriate hierarchies
        - **Custom**: User-defined generalization rules
        - **Domain-Specific**: Specialized rules for healthcare, finance, etc.
        
        **Clustering Settings**:
        - **Algorithm**: K-means, hierarchical, or density-based
        - **Distance Metrics**: Euclidean, Manhattan, or custom
        - **Cluster Count**: Automatic or manually specified
        
        **Noise Parameters**:
        - **Distribution Type**: Laplace, Gaussian, or uniform
        - **Calibration Method**: Automatic sensitivity calculation
        - **Budget Allocation**: How epsilon is distributed across queries
        
        #### Integration Settings
        
        **API Configuration**:
        - **Authentication**: Token-based or certificate authentication
        - **Rate Limiting**: Request throttling for stability
        - **Response Format**: JSON, XML, or custom formats
        
        **Database Connections**:
        - **Direct Integration**: Connect to organizational databases
        - **Batch Processing**: Scheduled anonymization jobs
        - **Real-time Processing**: Stream processing capabilities
        
        ### Best Practices
        
        #### Profile Management
        - **Start with Templates**: Use provided profiles as starting points
        - **Document Decisions**: Record rationale for parameter choices
        - **Test Thoroughly**: Validate profiles with representative data
        - **Review Regularly**: Update profiles as requirements evolve
        
        #### System Optimization
        - **Monitor Performance**: Track processing times and resource usage
        - **Adjust Gradually**: Make incremental changes to find optimal settings
        - **Balance Resources**: Consider memory, CPU, and storage constraints
        - **Plan for Growth**: Configure for anticipated data volume increases
        
        #### Security Considerations
        - **Enable All Security Features**: Unless performance is critically impacted
        - **Regular Updates**: Keep security configurations current
        - **Access Controls**: Limit configuration changes to authorized personnel
        - **Audit Changes**: Log all configuration modifications
        """)
    
    elif help_topic == "API Reference":
        st.markdown("""
        ## API Reference Guide
        
        ### Core Components Overview
        
        #### DataHandler Class
        **Purpose**: Centralized data loading, validation, and repair
        
        **Key Methods**:
        ```python
        # Load data from various formats
        load_data(file_obj, file_type=None) -> pd.DataFrame
        
        # Assess data quality
        assess_data_quality(data) -> Dict[str, Any]
        
        # Apply automatic repairs
        apply_fixes(data, issues) -> pd.DataFrame
        
        # Comprehensive data repair
        repair_data(data) -> pd.DataFrame
        ```
        
        **Supported Formats**: CSV, Excel, JSON, XML, Parquet, TSV
        **Error Handling**: Automatic encoding detection, format validation
        **Performance**: Chunked processing for large files
        
        #### RiskAssessment Class
        **Purpose**: Evaluate re-identification risks and anonymity levels
        
        **Key Methods**:
        ```python
        # Main risk assessment
        assess_risk(data, quasi_identifiers, sensitive_attributes, 
                   k_threshold=3, sample_size=0.5, attack_scenarios) -> Dict
        
        # Create risk visualizations
        create_risk_visualization(results) -> plotly.Figure
        
        # Generate recommendations
        get_recommendations(results) -> List[str]
        ```
        
        **Risk Metrics**: K-anonymity violations, unique records, overall risk score
        **Attack Scenarios**: Prosecutor, Journalist, Marketer attacks
        **Visualizations**: Radar charts, distribution plots, risk matrices
        
        #### PrivacyEnhancement Class
        **Purpose**: Apply anonymization techniques to protect privacy
        
        **Available Techniques**:
        ```python
        # K-Anonymity implementation
        apply_k_anonymity(data, k, quasi_identifiers, method, suppression_limit)
        
        # L-Diversity implementation
        apply_l_diversity(data, l, quasi_identifiers, sensitive_attribute, method)
        
        # T-Closeness implementation
        apply_t_closeness(data, t, quasi_identifiers, sensitive_attribute)
        
        # Differential Privacy
        apply_differential_privacy(data, epsilon, queries)
        
        # Synthetic Data Generation
        generate_synthetic_data(data, method, parameters)
        ```
        
        **Configuration Options**: Multiple algorithms, parameter tuning, quality controls
        **Output**: Anonymized dataset with transformation metadata
        
        #### UtilityMeasurement Class
        **Purpose**: Evaluate data utility preservation after anonymization
        
        **Key Methods**:
        ```python
        # Comprehensive utility measurement
        measure_utility(original_data, processed_data, metrics) -> Dict
        
        # Individual metric calculations
        _measure_statistical_similarity(original, processed) -> Dict
        _measure_correlation_preservation(original, processed) -> Dict
        _measure_distribution_similarity(original, processed) -> Dict
        _measure_information_loss(original, processed) -> Dict
        _measure_classification_utility(original, processed) -> Dict
        ```
        
        **Utility Metrics**: Statistical similarity, correlation preservation, information loss
        **Visualizations**: Radar charts, distribution comparisons, correlation heatmaps
        **Assessment**: Automatic utility level classification and recommendations
        
        #### ReportGenerator Class
        **Purpose**: Create comprehensive privacy-utility analysis reports
        
        **Key Methods**:
        ```python
        # Generate PDF reports
        generate_pdf_report(report_data, report_type) -> bytes
        
        # Generate HTML reports
        generate_html_report(report_data, report_type) -> str
        
        # Create executive summary
        create_executive_summary(data) -> Dict
        
        # Generate technical documentation
        create_technical_report(data) -> Dict
        ```
        
        **Report Types**: Executive, Technical, Comprehensive
        **Formats**: PDF, HTML with interactive elements
        **Content**: Automated insights, visualizations, recommendations
        
        ### Utility Functions
        
        #### FileOperations Class
        **Purpose**: File handling and export operations
        
        **Methods**:
        ```python
        # Export processed data
        export_to_csv(data, filename) -> bool
        export_to_excel(data, filename) -> bool
        export_to_json(data, filename) -> bool
        export_to_parquet(data, filename) -> bool
        
        # File validation
        validate_file_format(file_obj) -> bool
        get_file_info(file_obj) -> Dict
        ```
        
        #### DataValidator Class
        **Purpose**: Comprehensive data validation and quality checks
        
        **Methods**:
        ```python
        # Main validation
        validate_data(data) -> Dict[str, Any]
        
        # Specific validations
        check_missing_values(data) -> Dict
        validate_data_types(data) -> Dict
        check_data_consistency(data) -> Dict
        identify_outliers(data) -> Dict
        ```
        
        #### DataEncryption Class
        **Purpose**: Data security and encryption operations
        
        **Methods**:
        ```python
        # Encrypt sensitive data
        encrypt_data(data, key=None) -> bytes
        
        # Decrypt data
        decrypt_data(encrypted_data, key) -> pd.DataFrame
        
        # Key management
        generate_key() -> bytes
        derive_key(password, salt) -> bytes
        ```
        
        ### Configuration Management
        
        #### Privacy Profiles
        **Structure**:
        ```json
        {
          "profile_name": {
            "k_threshold": 5,
            "risk_level": "Medium",
            "privacy_technique": "L-Diversity",
            "utility_threshold": 0.7,
            "created_date": "2024-08-01T10:30:00"
          }
        }
        ```
        
        **File Location**: `config/privacy_profiles.json`
        **Management**: Load, save, modify profiles programmatically
        
        #### System Configuration
        **Structure**:
        ```json
        {
          "max_file_size": 100,
          "chunk_size": 10000,
          "enable_encryption": true,
          "enable_logging": true,
          "log_level": "INFO"
        }
        ```
        
        **File Location**: `config/system_config.json`
        **Runtime**: Configurations loaded at system startup
        
        ### Error Handling
        
        #### Common Exceptions
        ```python
        # Data loading errors
        class DataLoadError(Exception): pass
        
        # Validation failures
        class ValidationError(Exception): pass
        
        # Privacy enhancement errors
        class PrivacyError(Exception): pass
        
        # Utility measurement errors
        class UtilityError(Exception): pass
        ```
        
        #### Error Recovery
        - **Automatic Retry**: For transient failures
        - **Graceful Degradation**: Partial results when possible
        - **Detailed Logging**: Complete error context and stack traces
        - **User Notifications**: Clear error messages and suggested actions
        
        ### Performance Considerations
        
        #### Memory Management
        - **Chunked Processing**: Large datasets processed in segments
        - **Efficient Data Types**: Automatic optimization for memory usage
        - **Garbage Collection**: Proactive memory cleanup
        - **Resource Monitoring**: Track memory and CPU usage
        
        #### Optimization Techniques
        - **Vectorized Operations**: NumPy and Pandas optimizations
        - **Parallel Processing**: Multi-core utilization where possible
        - **Caching**: Intermediate results cached for repeated operations
        - **Lazy Loading**: Data loaded only when needed
        
        ### Integration Examples
        
        #### Basic Usage Workflow
        ```python
        # Initialize components
        data_handler = DataHandler()
        risk_assessment = RiskAssessment()
        privacy_enhancement = PrivacyEnhancement()
        utility_measurement = UtilityMeasurement()
        
        # Load and validate data
        data = data_handler.load_data(file_obj)
        quality_report = data_handler.assess_data_quality(data)
        
        # Apply fixes if needed
        if quality_report['issues']:
            data = data_handler.apply_fixes(data, quality_report['issues'])
        
        # Assess risk
        risk_results = risk_assessment.assess_risk(
            data, 
            quasi_identifiers=['age', 'gender', 'zipcode'],
            sensitive_attributes=['medical_condition']
        )
        
        # Apply privacy enhancement
        processed_data = privacy_enhancement.apply_k_anonymity(
            data, k=5, quasi_identifiers=['age', 'gender', 'zipcode']
        )
        
        # Measure utility
        utility_results = utility_measurement.measure_utility(
            data, processed_data
        )
        ```
        
        #### Custom Extension
        ```python
        # Extend existing classes
        class CustomPrivacyTechnique(PrivacyEnhancement):
            def apply_custom_method(self, data, parameters):
                # Custom implementation
                return processed_data
        
        # Add custom utility metrics
        class ExtendedUtilityMeasurement(UtilityMeasurement):
            def measure_custom_utility(self, original, processed):
                # Custom utility calculation
                return utility_score
        ```
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
