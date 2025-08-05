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
            padding: 2rem 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .login-form {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .credentials-info {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
            margin: 1rem 0;
        }
        .airavata-brand {
            text-align: center;
            margin-top: 2rem;
            color: #6b7280;
            font-size: 0.9rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Login header
        st.markdown("""
        <div class="login-header">
            <h1>🛡️ SafeData Pipeline</h1>
            <h3>Government of India - Data Privacy Protection System</h3>
            <p>Secure Login Portal</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login form
        with st.container():
            st.markdown('<div class="login-form">', unsafe_allow_html=True)
            
            # Credentials reminder
            st.markdown("""
            <div class="credentials-info">
                <h4>📋 Login Credentials</h4>
                <p><strong>Username:</strong> admin</p>
                <p><strong>Password:</strong> admin@123</p>
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