"""
Authentication module for SafeData Pipeline
Developed by AIRAVATA Technologies
"""

import streamlit as st
import hashlib
from datetime import datetime

class AuthManager:
    def __init__(self):
        self.credentials = {
            "admin": {
                "password": self.hash_password("admin@123"),
                "full_name": "System Administrator",
                "email": "admin@safedata.gov.in",
                "role": "Administrator",
                "department": "Ministry of Electronics and IT",
                "created_date": "2025-01-01",
                "last_login": None,
                "permissions": ["data_upload", "risk_assessment", "privacy_enhancement", "utility_measurement", "report_generation", "system_config"]
            }
        }
        
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        """Authenticate user credentials"""
        if username in self.credentials:
            hashed_password = self.hash_password(password)
            if self.credentials[username]["password"] == hashed_password:
                # Update last login
                self.credentials[username]["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return True
        return False
    
    def get_user_profile(self, username):
        """Get user profile information"""
        if username in self.credentials:
            return self.credentials[username]
        return None
    
    def login_page(self):
        """Display login page"""
        st.markdown("""
        <style>
        .login-header {
            text-align: center;
            padding: 2.5rem;
            background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 50%, #0369a1 100%);
            color: white;
            border-radius: 18px;
            margin-bottom: 2rem;
            box-shadow: 0 12px 35px rgba(14, 165, 233, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .login-form {
            max-width: 450px;
            margin: 0 auto;
            padding: 2.5rem;
            background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
            border-radius: 15px;
            box-shadow: 0 8px 30px rgba(14, 165, 233, 0.1);
            border: 1px solid rgba(14, 165, 233, 0.1);
        }
        .credentials-info {
            background: linear-gradient(145deg, #f0f9ff 0%, #e0f2fe 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 5px solid #0ea5e9;
            border: 1px solid rgba(14, 165, 233, 0.2);
            margin: 1.5rem 0;
            box-shadow: 0 4px 15px rgba(14, 165, 233, 0.1);
        }
        .airavata-brand {
            text-align: center;
            margin-top: 2rem;
            color: #6b7280;
            font-size: 0.9rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Login header with sky blue theme
        st.markdown("""
        <div class="login-header">
            <div style='display: flex; align-items: center; justify-content: center; margin-bottom: 1.5rem;'>
                <div style='background: rgba(255, 255, 255, 0.15); 
                            padding: 1rem; border-radius: 12px; margin-right: 1.5rem;
                            backdrop-filter: blur(10px);'>
                    <span style='font-size: 2.5rem;'>🛡️</span>
                </div>
                <div style='text-align: left;'>
                    <h1 style='margin: 0; font-size: 2.8rem; font-weight: 800;'>SafeData Pipeline</h1>
                    <h3 style='margin: 0.5rem 0; font-size: 1.3rem; font-weight: 600; opacity: 0.9;'>Government of India - Data Privacy Protection System</h3>
                </div>
            </div>
            <p style='font-size: 1.1rem; font-weight: 500; opacity: 0.95; margin: 0;'>Secure Login Portal</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login form
        with st.container():
            st.markdown('<div class="login-form">', unsafe_allow_html=True)
            
            # Credentials reminder with sky blue theme
            st.markdown("""
            <div class="credentials-info">
                <div style='display: flex; align-items: center; margin-bottom: 1rem;'>
                    <div style='background: linear-gradient(135deg, #0ea5e9, #0284c7); 
                                color: white; padding: 0.6rem; border-radius: 8px; margin-right: 1rem;'>
                        <span style='font-size: 1rem;'>📋</span>
                    </div>
                    <h4 style='margin: 0; color: #0c4a6e; font-weight: 700;'>Login Credentials</h4>
                </div>
                <div style='background: rgba(14, 165, 233, 0.05); padding: 1rem; border-radius: 8px; margin: 0.5rem 0;'>
                    <p style='margin: 0; color: #0c4a6e;'><strong style='color: #0369a1;'>Username:</strong> admin</p>
                </div>
                <div style='background: rgba(14, 165, 233, 0.05); padding: 1rem; border-radius: 8px; margin: 0.5rem 0;'>
                    <p style='margin: 0; color: #0c4a6e;'><strong style='color: #0369a1;'>Password:</strong> admin@123</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Login form
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    submit_button = st.form_submit_button("🔐 Login", use_container_width=True)
                
                if submit_button:
                    if self.authenticate(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_profile = self.get_user_profile(username)
                        st.success("✅ Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # AIRAVATA Technologies branding
        st.markdown("""
        <div class="airavata-brand">
            <p>🚀 Made by <strong>AIRAVATA Technologies</strong></p>
            <p>Advanced AI Solutions for Government Applications</p>
        </div>
        """, unsafe_allow_html=True)
    
    def logout(self):
        """Logout user"""
        for key in ['authenticated', 'username', 'user_profile']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)