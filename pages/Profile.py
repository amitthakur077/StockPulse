import streamlit as st
import sys
import os

# Ensure the root directory is in the path for modules import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.set_page_config(page_title="StockPulse - Profile", page_icon="👤", layout="wide")

from src.database import SessionLocal
from src.utils import inject_custom_css, render_top_navbar
import src.auth as auth

# Inject CSS and top navigation
inject_custom_css()
render_top_navbar("Profile")


st.title("👤 User Profile & Accounts")

# Get SQLAlchemy database session
db = SessionLocal()

try:
    if auth.is_logged_in():
        st.success(f"You are currently logged in as **{auth.get_logged_in_username()}**.")
        
        # Display profile card
        st.markdown(
            f"""
            <div class="glass-card">
                <h3>User Account Details</h3>
                <p><b>Username:</b> {auth.get_logged_in_username()}</p>
                <p><b>Email:</b> {st.session_state.get('email', 'N/A') or 'N/A'}</p>
                <p><b>Account Type:</b> Free Offline Tier</p>
                <p><b>Database Engine:</b> SQLite Local File (stockpulse.db)</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if st.button("Log Out of Account", type="primary"):
            auth.logout_user()
            st.success("Successfully logged out!")
            st.rerun()
            
    else:
        # Show login and register tabs
        tab_login, tab_register = st.tabs(["🔒 Log In", "📝 Create Account"])
        
        with tab_login:
            st.subheader("Login to StockPulse")
            login_user_input = st.text_input("Username", key="login_user")
            login_pass_input = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Log In", type="primary", key="login_submit"):
                if login_user_input and login_pass_input:
                    success = auth.login_user(db, login_user_input, login_pass_input)
                    if success:
                        st.success(f"Welcome back, {login_user_input}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password. Please try again.")
                else:
                    st.warning("Please fill in both fields.")
                    
        with tab_register:
            st.subheader("Create a Free Local Account")
            st.markdown(
                "Registering allows you to save stocks on your watchlist and log portfolio trades. "
                "Your password is secure and hashed locally."
            )
            
            reg_user_input = st.text_input("Choose Username", key="reg_user")
            reg_email_input = st.text_input("Email (Optional)", key="reg_email")
            reg_pass_input = st.text_input("Choose Password", type="password", key="reg_pass")
            reg_pass_conf = st.text_input("Confirm Password", type="password", key="reg_pass_conf")
            
            if st.button("Register Account", key="reg_submit"):
                if not reg_user_input or not reg_pass_input:
                    st.warning("Username and Password are required.")
                elif reg_pass_input != reg_pass_conf:
                    st.error("Passwords do not match.")
                else:
                    success, msg = auth.register_user(
                        db=db,
                        username=reg_user_input,
                        password=reg_pass_input,
                        email=reg_email_input if reg_email_input else None
                    )
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
finally:
    db.close()
