import streamlit as st
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config
from src.auth import is_logged_in, get_logged_in_username, logout_user
from src.database import get_db

COLORS = config.THEME_COLORS

def inject_custom_css():
    """
    Inject custom CSS rules to override Streamlit defaults and establish
    a premium, modern dark glassmorphism design.
    """
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    /* Global style modifications */
    html, body, [class*="css"] {{
        font-family: {config.UI_FONTS};
    }}
    
    /* Main layout modifications */
    .stApp {{
        background-color: {COLORS["bg_color"]};
        background-image: 
            radial-gradient(at 10% 10%, rgba(138, 43, 226, 0.08) 0px, transparent 50%),
            radial-gradient(at 90% 80%, rgba(0, 245, 212, 0.05) 0px, transparent 50%);
        background-attachment: fixed;
    }}
    
    /* Sidebar styling overrides */
    [data-testid="stSidebar"] {{
        background-color: rgba(14, 17, 23, 0.95);
        border-right: 1px solid {COLORS["border_color"]};
    }}
    
    /* Glassmorphism custom cards */
    .glass-card {{
        background-color: {COLORS["card_bg"]};
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid {COLORS["border_color"]};
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    
    .glass-card:hover {{
        transform: translateY(-2px);
        border-color: rgba(138, 43, 226, 0.3);
    }}
    
    /* Premium Title gradient text */
    .gradient-text {{
        background: linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["secondary"]} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
    }}
    
    .gradient-subtitle {{
        color: {COLORS["text_secondary"]};
        font-family: 'Inter', sans-serif;
        font-weight: 300;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }}
    
    /* Metric styling */
    .custom-metric {{
        display: flex;
        flex-direction: column;
        background: rgba(255, 255, 255, 0.02);
        padding: 12px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }}
    
    .metric-label {{
        color: {COLORS["text_secondary"]};
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 4px;
    }}
    
    .metric-value {{
        color: {COLORS["text_primary"]};
        font-size: 1.4rem;
        font-weight: 700;
    }}
    
    .metric-change {{
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 4px;
    }}
    
    .metric-change.up {{
        color: {COLORS["success"]};
    }}
    
    .metric-change.down {{
        color: {COLORS["danger"]};
    }}
    
    /* Table styling fixes for dark mode */
    .stTable, div[data-testid="stTable"] {{
        background-color: {COLORS["card_bg"]} !important;
        border-radius: 8px;
        border: 1px solid {COLORS["border_color"]};
    }}
    
    /* Hide default Streamlit footer & hamburger menu for cleaner layout */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{background-color: transparent !important;}}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def display_sidebar_auth():
    """
    Renders login state summary in the Streamlit sidebar.
    """
    st.sidebar.markdown("---")
    if is_logged_in():
        username = get_logged_in_username()
        st.sidebar.markdown(f"👤 **Logged in as:** `{username}`")
        if st.sidebar.button("Log Out", key="sidebar_logout_btn"):
            logout_user()
            st.rerun()
    else:
        st.sidebar.markdown("🔒 **Account Status: Guest**")
        st.sidebar.info(
            "Log in or Sign up on the **Profile** page to save your personalized Watchlist and Portfolio."
        )

def render_metric_card(label: str, value: str, change: str = None, is_positive: bool = True):
    """
    Renders a custom HTML-based metric card that looks much cleaner than
    the default Streamlit metric component.
    """
    change_html = ""
    if change:
        color_class = "up" if is_positive else "down"
        arrow = "▲" if is_positive else "▼"
        change_html = f'<div class="metric-change {color_class}">{arrow} {change}</div>'
        
    card_html = f"""
    <div class="custom-metric">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {change_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
