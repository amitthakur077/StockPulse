import hashlib
import secrets
import streamlit as st
from sqlalchemy.orm import Session
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.models import User

def generate_salt() -> str:
    """
    Generate a cryptographically secure random salt.
    """
    return secrets.token_hex(16)

def hash_password(password: str, salt: str) -> str:
    """
    Hash a password with a salt using PBKDF2 HMAC SHA-256.
    """
    pwd_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    # 100,000 iterations is a secure standard for PBKDF2
    hashed = hashlib.pbkdf2_hmac('sha256', pwd_bytes, salt_bytes, 100000)
    return hashed.hex()

def verify_password(password: str, salt: str, password_hash: str) -> bool:
    """
    Verify if the input password matches the stored password hash.
    """
    return hash_password(password, salt) == password_hash

def register_user(db: Session, username: str, password: str, email: str = None) -> tuple[bool, str]:
    """
    Register a new user in the database.
    Returns (success_boolean, status_message).
    """
    # Clean inputs
    username = username.strip()
    if email:
        email = email.strip()
    
    if not username or not password:
        return False, "Username and password cannot be empty."

    # Check if username already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return False, "Username already exists."

    if email:
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            return False, "Email already registered."

    try:
        salt = generate_salt()
        pwd_hash = hash_password(password, salt)
        
        new_user = User(
            username=username,
            email=email if email else None,
            password_hash=pwd_hash,
            salt=salt
        )
        
        db.add(new_user)
        db.commit()
        return True, "Registration successful! You can now log in."
    except Exception as e:
        db.rollback()
        return False, f"Database error during registration: {str(e)}"

def login_user(db: Session, username: str, password: str) -> bool:
    """
    Authenticate a user. If successful, sets Streamlit session state keys.
    """
    username = username.strip()
    if not username or not password:
        return False

    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False

    if verify_password(password, user.salt, user.password_hash):
        # Set session state variables
        st.session_state["logged_in"] = True
        st.session_state["user_id"] = user.id
        st.session_state["username"] = user.username
        st.session_state["email"] = user.email
        return True
    
    return False

def logout_user():
    """
    Log out the user by clearing credentials from session state.
    """
    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None
    st.session_state["username"] = None
    st.session_state["email"] = None

def is_logged_in() -> bool:
    """
    Check if a user is currently logged in.
    """
    return st.session_state.get("logged_in", False)

def get_logged_in_user_id() -> int | None:
    """
    Get the ID of the currently logged-in user.
    """
    return st.session_state.get("user_id", None)

def get_logged_in_username() -> str | None:
    """
    Get the username of the currently logged-in user.
    """
    return st.session_state.get("username", None)
