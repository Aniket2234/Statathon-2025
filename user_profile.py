"""
User Profile Dashboard for SafeData Pipeline
Developed by AIRAVATA Technologies
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def display_user_profile():
    """Display comprehensive user profile dashboard"""
    
    # Get user profile from session state
    user_profile = st.session_state.get('user_profile', {})
    username = st.session_state.get('username', 'Unknown')
    
    # Profile header with AIRAVATA branding
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);'>
        <div style='display: flex; align-items: center; justify-content: space-between;'>
            <div>
                <h1 style='margin: 0; font-size: 2.5rem;'>👤 User Profile</h1>
                <p style='margin: 0; opacity: 0.9; font-size: 1.1rem;'>Government of India - SafeData Pipeline</p>
            </div>
            <div style='text-align: right;'>
                <p style='margin: 0; font-size: 0.9rem; opacity: 0.8;'>🚀 Made by AIRAVATA Technologies</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Profile information cards
    col1, col2 = st.columns(2)
    
    with col1:
        # Personal Information Card
        st.markdown("""
        <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 1rem;
                    border-left: 4px solid #3b82f6;'>
            <h3 style='color: #1e293b; margin-top: 0;'>👨‍💼 Personal Information</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Profile details in a clean format
        profile_data = {
            "Full Name": user_profile.get('full_name', 'N/A'),
            "Username": username,
            "Email": user_profile.get('email', 'N/A'),
            "Role": user_profile.get('role', 'N/A'),
            "Department": user_profile.get('department', 'N/A'),
        }
        
        for key, value in profile_data.items():
            st.markdown(f"""
            <div style='background: #f8fafc; padding: 0.75rem; margin: 0.5rem 0; 
                        border-radius: 8px; border-left: 3px solid #3b82f6;'>
                <strong style='color: #374151;'>{key}:</strong> 
                <span style='color: #1f2937;'>{value}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Account Information Card
        st.markdown("""
        <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 1rem;
                    border-left: 4px solid #10b981;'>
            <h3 style='color: #1e293b; margin-top: 0;'>⚙️ Account Information</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Account details
        account_data = {
            "Account Created": user_profile.get('created_date', 'N/A'),
            "Last Login": user_profile.get('last_login', 'Never'),
            "Account Status": "Active",
            "Security Level": "High",
            "Session Duration": "8 hours"
        }
        
        for key, value in account_data.items():
            color = "#10b981" if key == "Account Status" else "#3b82f6"
            st.markdown(f"""
            <div style='background: #f8fafc; padding: 0.75rem; margin: 0.5rem 0; 
                        border-radius: 8px; border-left: 3px solid {color};'>
                <strong style='color: #374151;'>{key}:</strong> 
                <span style='color: #1f2937;'>{value}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Permissions and Access Rights
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin: 2rem 0;
                border-left: 4px solid #f59e0b;'>
        <h3 style='color: #1e293b; margin-top: 0;'>🔐 Permissions & Access Rights</h3>
    </div>
    """, unsafe_allow_html=True)
    
    permissions = user_profile.get('permissions', [])
    permission_descriptions = {
        "data_upload": "📂 Data Upload - Upload and manage data files",
        "risk_assessment": "⚠️ Risk Assessment - Perform privacy risk analysis",
        "privacy_enhancement": "🛡️ Privacy Enhancement - Apply anonymization techniques",
        "utility_measurement": "📊 Utility Measurement - Measure data quality",
        "report_generation": "📄 Report Generation - Generate compliance reports",
        "system_config": "⚙️ System Configuration - Manage system settings"
    }
    
    # Display permissions in a grid
    cols = st.columns(2)
    for i, permission in enumerate(permissions):
        with cols[i % 2]:
            description = permission_descriptions.get(permission, f"✅ {permission.replace('_', ' ').title()}")
            st.markdown(f"""
            <div style='background: #ecfdf5; padding: 1rem; margin: 0.5rem 0; 
                        border-radius: 8px; border: 1px solid #10b981;'>
                <span style='color: #059669; font-weight: 600;'>{description}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Activity Statistics
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin: 2rem 0;
                border-left: 4px solid #8b5cf6;'>
        <h3 style='color: #1e293b; margin-top: 0;'>📈 Activity Statistics</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create sample activity metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Data Files Processed",
            value="156",
            delta="12 this month"
        )
    
    with col2:
        st.metric(
            label="Risk Assessments",
            value="89",
            delta="7 this week"
        )
    
    with col3:
        st.metric(
            label="Reports Generated",
            value="34",
            delta="3 today"
        )
    
    with col4:
        st.metric(
            label="System Uptime",
            value="99.9%",
            delta="0.1% increase"
        )
    
    # Recent Activity Chart
    st.markdown("### 📊 Recent Activity Trends")
    
    # Generate sample activity data
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    activity_data = pd.DataFrame({
        'Date': dates,
        'Files Processed': np.random.randint(0, 15, len(dates)),
        'Risk Assessments': np.random.randint(0, 8, len(dates)),
        'Reports Generated': np.random.randint(0, 5, len(dates))
    })
    
    fig = px.line(activity_data, x='Date', y=['Files Processed', 'Risk Assessments', 'Reports Generated'],
                  title="30-Day Activity Overview",
                  color_discrete_map={
                      'Files Processed': '#3b82f6',
                      'Risk Assessments': '#f59e0b',
                      'Reports Generated': '#10b981'
                  })
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family='Inter',
        title_font_size=18,
        title_font_color='#1e293b'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # System Information
    st.markdown("### 🖥️ System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background: #fef3c7; padding: 1rem; border-radius: 8px; 
                    border-left: 4px solid #f59e0b; margin: 0.5rem 0;'>
            <strong style='color: #92400e;'>Server Status:</strong> 
            <span style='color: #78350f;'>🟢 Online</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: #dbeafe; padding: 1rem; border-radius: 8px; 
                    border-left: 4px solid #3b82f6; margin: 0.5rem 0;'>
            <strong style='color: #1e40af;'>Database:</strong> 
            <span style='color: #1e3a8a;'>🟢 Connected</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: #ecfdf5; padding: 1rem; border-radius: 8px; 
                    border-left: 4px solid #10b981; margin: 0.5rem 0;'>
            <strong style='color: #047857;'>Security:</strong> 
            <span style='color: #065f46;'>🔒 Secure</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: #f3e8ff; padding: 1rem; border-radius: 8px; 
                    border-left: 4px solid #8b5cf6; margin: 0.5rem 0;'>
            <strong style='color: #7c3aed;'>Version:</strong> 
            <span style='color: #6d28d9;'>v2.1.0</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer with AIRAVATA branding
    st.markdown("""
    <div style='text-align: center; margin-top: 3rem; padding: 2rem; 
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); 
                border-radius: 12px; border: 1px solid #cbd5e1;'>
        <h4 style='color: #475569; margin: 0;'>🚀 Powered by AIRAVATA Technologies</h4>
        <p style='color: #64748b; margin: 0.5rem 0 0 0;'>Advanced AI Solutions for Government Applications</p>
        <p style='color: #94a3b8; margin: 0; font-size: 0.9rem;'>© 2025 AIRAVATA Technologies - All Rights Reserved</p>
    </div>
    """, unsafe_allow_html=True)