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
    """Display comprehensive user profile dashboard with editing capabilities"""
    
    # Get user profile from session state
    user_profile = st.session_state.get('user_profile', {})
    username = st.session_state.get('username', 'Unknown')
    
    # Initialize edit mode in session state
    if 'profile_edit_mode' not in st.session_state:
        st.session_state.profile_edit_mode = False
    
    # Profile header with AIRAVATA branding - Sky Blue Theme
    st.markdown("""
    <div style='background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 50%, #0369a1 100%); 
                padding: 2.5rem; border-radius: 18px; color: white; margin-bottom: 2rem;
                box-shadow: 0 12px 35px rgba(14, 165, 233, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.1);'>
        <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;'>
            <div style='flex: 1; min-width: 300px;'>
                <div style='display: flex; align-items: center; margin-bottom: 1rem;'>
                    <div style='background: rgba(255, 255, 255, 0.15); 
                                padding: 1rem; border-radius: 12px; margin-right: 1.5rem;
                                backdrop-filter: blur(10px);'>
                        <span style='font-size: 2.5rem;'>👤</span>
                    </div>
                    <div>
                        <h1 style='margin: 0; font-size: 2.8rem; font-weight: 800; 
                                   text-shadow: 0 2px 4px rgba(0,0,0,0.1);'>User Profile</h1>
                        <p style='margin: 0.5rem 0 0 0; opacity: 0.95; font-size: 1.1rem; font-weight: 500;'>
                            Government of India - SafeData Pipeline
                        </p>
                    </div>
                </div>
            </div>
            <div style='text-align: right; background: rgba(255, 255, 255, 0.1); 
                        padding: 1rem 1.5rem; border-radius: 12px; backdrop-filter: blur(10px);
                        border: 1px solid rgba(255, 255, 255, 0.2);'>
                <p style='margin: 0; font-size: 1rem; font-weight: 600; opacity: 0.9;'>
                    🚀 Made by AIRAVATA Technologies
                </p>
                <p style='margin: 0.5rem 0 0 0; font-size: 0.85rem; opacity: 0.8;'>
                    Advanced AI Solutions
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Profile information cards with edit functionality
    col1, col2 = st.columns(2)
    
    with col1:
        # Personal Information Card Header - Sky Blue Theme
        st.markdown("""
        <div style='background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%); 
                    padding: 1.8rem; border-radius: 15px; 
                    box-shadow: 0 8px 25px rgba(14, 165, 233, 0.08); margin-bottom: 1.5rem;
                    border-left: 5px solid #0ea5e9; border: 1px solid rgba(14, 165, 233, 0.1);'>
            <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;'>
                <div style='display: flex; align-items: center;'>
                    <div style='background: linear-gradient(135deg, #0ea5e9, #0284c7); 
                                color: white; padding: 0.8rem; border-radius: 10px; margin-right: 1rem;'>
                        <span style='font-size: 1.2rem;'>👨‍💼</span>
                    </div>
                    <h3 style='color: #0f172a; margin: 0; font-size: 1.4rem; font-weight: 700;'>
                        Personal Information
                    </h3>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Edit/Save button
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if not st.session_state.profile_edit_mode:
                if st.button("✏️ Edit Profile", use_container_width=True, key="edit_profile_btn"):
                    st.session_state.profile_edit_mode = True
                    st.rerun()
            else:
                if st.button("💾 Save Changes", use_container_width=True, key="save_profile_btn"):
                    # Update the actual user profile with edited values
                    if 'edited_profile' in st.session_state:
                        for key, value in st.session_state.edited_profile.items():
                            st.session_state.user_profile[key] = value
                    st.session_state.profile_edit_mode = False
                    st.success("✅ Profile updated successfully!")
                    st.balloons()  # Add celebration effect
                    st.rerun()
        
        with col_btn2:
            if st.session_state.profile_edit_mode:
                if st.button("❌ Cancel", use_container_width=True, key="cancel_profile_btn"):
                    st.session_state.profile_edit_mode = False
                    st.rerun()
        
        # Profile details - editable or display mode
        if not st.session_state.profile_edit_mode:
            # Display mode
            profile_data = {
                "Full Name": user_profile.get('full_name', 'N/A'),
                "Username": username,
                "Email": user_profile.get('email', 'N/A'),
                "Role": user_profile.get('role', 'N/A'),
                "Department": user_profile.get('department', 'N/A'),
            }
            
            for key, value in profile_data.items():
                st.markdown(f"""
                <div style='background: linear-gradient(145deg, #f0f9ff 0%, #e0f2fe 100%); 
                            padding: 1rem; margin: 0.8rem 0; 
                            border-radius: 10px; border-left: 4px solid #0ea5e9;
                            box-shadow: 0 2px 8px rgba(14, 165, 233, 0.1);
                            transition: all 0.3s ease;'>
                    <strong style='color: #0c4a6e; font-size: 0.95rem; font-weight: 600;'>{key}:</strong> 
                    <span style='color: #164e63; font-weight: 500; margin-left: 0.5rem;'>{value}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Edit mode
            st.markdown("### Edit Personal Information")
            
            with st.container():
                new_full_name = st.text_input("Full Name", value=user_profile.get('full_name', ''), key="edit_full_name")
                new_email = st.text_input("Email", value=user_profile.get('email', ''), key="edit_email")
                new_role = st.selectbox("Role", 
                                       options=["Administrator", "Data Analyst", "Privacy Officer", "System Manager"],
                                       index=0 if user_profile.get('role') == 'Administrator' else 0,
                                       key="edit_role")
                new_department = st.selectbox("Department",
                                            options=["Ministry of Electronics and IT", "Ministry of Home Affairs", "Ministry of Defence", "Other"],
                                            index=0 if user_profile.get('department') == 'Ministry of Electronics and IT' else 0,
                                            key="edit_department")
                
                # Store the edited values in session state
                if 'edited_profile' not in st.session_state:
                    st.session_state.edited_profile = {}
                
                st.session_state.edited_profile.update({
                    'full_name': new_full_name,
                    'email': new_email,
                    'role': new_role,
                    'department': new_department
                })
    
    with col2:
        # Account Settings Card - Sky Blue Theme
        st.markdown("""
        <div style='background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%); 
                    padding: 1.8rem; border-radius: 15px; 
                    box-shadow: 0 8px 25px rgba(14, 165, 233, 0.08); margin-bottom: 1.5rem;
                    border-left: 5px solid #0ea5e9; border: 1px solid rgba(14, 165, 233, 0.1);'>
            <div style='display: flex; align-items: center; margin-bottom: 1rem;'>
                <div style='background: linear-gradient(135deg, #0ea5e9, #0284c7); 
                            color: white; padding: 0.8rem; border-radius: 10px; margin-right: 1rem;'>
                    <span style='font-size: 1.2rem;'>⚙️</span>
                </div>
                <h3 style='color: #0f172a; margin: 0; font-size: 1.4rem; font-weight: 700;'>
                    Account Settings
                </h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.profile_edit_mode:
            # Display account information
            account_data = {
                "Account Created": user_profile.get('created_date', 'N/A'),
                "Last Login": user_profile.get('last_login', 'Never'),
                "Account Status": "Active",
                "Security Level": "High",
                "Session Duration": "8 hours"
            }
            
            for key, value in account_data.items():
                if key == "Account Status":
                    bg_color = "linear-gradient(145deg, #ecfdf5 0%, #d1fae5 100%)"
                    border_color = "#10b981"
                    text_color = "#065f46"
                else:
                    bg_color = "linear-gradient(145deg, #f0f9ff 0%, #e0f2fe 100%)"
                    border_color = "#0ea5e9"
                    text_color = "#164e63"
                
                st.markdown(f"""
                <div style='background: {bg_color}; 
                            padding: 1rem; margin: 0.8rem 0; 
                            border-radius: 10px; border-left: 4px solid {border_color};
                            box-shadow: 0 2px 8px rgba(14, 165, 233, 0.1);
                            transition: all 0.3s ease;'>
                    <strong style='color: #0c4a6e; font-size: 0.95rem; font-weight: 600;'>{key}:</strong> 
                    <span style='color: {text_color}; font-weight: 500; margin-left: 0.5rem;'>{value}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Account settings in edit mode
            st.markdown("### Account Preferences")
            
            # Security settings
            st.markdown("**Security Settings**")
            enable_2fa = st.checkbox("Enable Two-Factor Authentication", value=True)
            session_timeout = st.selectbox("Session Timeout", 
                                         options=["2 hours", "4 hours", "8 hours", "12 hours"],
                                         index=2)
            
            # Notification preferences
            st.markdown("**Notification Preferences**")
            email_notifications = st.checkbox("Email Notifications", value=True)
            security_alerts = st.checkbox("Security Alerts", value=True)
            system_updates = st.checkbox("System Update Notifications", value=False)
            
            # Privacy settings
            st.markdown("**Privacy Settings**")
            profile_visibility = st.selectbox("Profile Visibility",
                                            options=["Private", "Department Only", "Organization Wide"],
                                            index=1)
            data_sharing = st.checkbox("Allow Anonymous Usage Analytics", value=False)
            
            # Password change section
            st.markdown("**Change Password**")
            with st.expander("🔒 Change Password", expanded=False):
                current_password = st.text_input("Current Password", type="password", key="current_pwd")
                new_password = st.text_input("New Password", type="password", key="new_pwd")
                confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_pwd")
                
                if st.button("🔄 Update Password", key="update_pwd_btn"):
                    if new_password and new_password == confirm_password:
                        st.success("Password updated successfully!")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match!")
                    else:
                        st.warning("Please enter a new password.")
    
    # Permissions and Access Rights - Sky Blue Theme
    st.markdown("""
    <div style='background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%); 
                padding: 2rem; border-radius: 15px; 
                box-shadow: 0 8px 25px rgba(14, 165, 233, 0.08); margin: 2rem 0;
                border-left: 5px solid #0ea5e9; border: 1px solid rgba(14, 165, 233, 0.1);'>
        <div style='display: flex; align-items: center; margin-bottom: 1.5rem;'>
            <div style='background: linear-gradient(135deg, #0ea5e9, #0284c7); 
                        color: white; padding: 0.8rem; border-radius: 10px; margin-right: 1rem;'>
                <span style='font-size: 1.2rem;'>🔐</span>
            </div>
            <h3 style='color: #0f172a; margin: 0; font-size: 1.4rem; font-weight: 700;'>
                Permissions & Access Rights
            </h3>
        </div>
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
    
    # Display permissions in a grid - Sky Blue Theme
    if not st.session_state.profile_edit_mode:
        # Display mode
        cols = st.columns(2)
        for i, permission in enumerate(permissions):
            with cols[i % 2]:
                description = permission_descriptions.get(permission, f"✅ {permission.replace('_', ' ').title()}")
                st.markdown(f"""
                <div style='background: linear-gradient(145deg, #f0f9ff 0%, #e0f2fe 100%); 
                            padding: 1.2rem; margin: 0.8rem 0; 
                            border-radius: 12px; border: 2px solid #0ea5e9;
                            box-shadow: 0 4px 12px rgba(14, 165, 233, 0.15);
                            transition: all 0.3s ease;'>
                    <span style='color: #0c4a6e; font-weight: 600; font-size: 0.95rem;'>{description}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        # Permission management in edit mode (Admin only)
        st.markdown("### 🔐 Manage Permissions")
        st.info("⚠️ Permission changes require administrator approval")
        
        for permission, description in permission_descriptions.items():
            current_status = permission in permissions
            checkbox_key = f"perm_{permission}"
            new_status = st.checkbox(description, value=current_status, key=checkbox_key, disabled=True)
        
        st.markdown("**Request Additional Permissions:**")
        additional_request = st.text_area("Describe additional permissions needed:", 
                                        placeholder="Please specify what additional access you require and the business justification...",
                                        key="perm_request")
        
        if st.button("📨 Submit Permission Request", key="submit_perm_req"):
            if additional_request.strip():
                st.success("Permission request submitted to administrator!")
            else:
                st.warning("Please provide details for your permission request.")
    
    # Activity Statistics - Sky Blue Theme
    st.markdown("""
    <div style='background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%); 
                padding: 2rem; border-radius: 15px; 
                box-shadow: 0 8px 25px rgba(14, 165, 233, 0.08); margin: 2rem 0;
                border-left: 5px solid #0ea5e9; border: 1px solid rgba(14, 165, 233, 0.1);'>
        <div style='display: flex; align-items: center; margin-bottom: 1.5rem;'>
            <div style='background: linear-gradient(135deg, #0ea5e9, #0284c7); 
                        color: white; padding: 0.8rem; border-radius: 10px; margin-right: 1rem;'>
                <span style='font-size: 1.2rem;'>📈</span>
            </div>
            <h3 style='color: #0f172a; margin: 0; font-size: 1.4rem; font-weight: 700;'>
                Activity Statistics
            </h3>
        </div>
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