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
    
    /* Hide the default left sidebar and its chevrons */
    [data-testid="stSidebar"] {{
        display: none !important;
    }}
    [data-testid="collapsedControl"] {{
        display: none !important;
    }}
    /* Optimize page padding for top nav layout */
    .stMainBlockContainer {{
        padding-top: 2.5rem !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_top_navbar(active_page: str):
    """
    Renders a premium horizontal navigation header at the top of the page.
    Handles user state display and routes via st.switch_page.
    """
    # Grid columns for top header
    col_logo, col_nav1, col_nav2, col_nav3, col_nav4, col_nav5, col_nav6, col_space, col_user = st.columns(
        [2.8, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 3.5, 2.5]
    )
    
    with col_logo:
        st.markdown(
            f"""
            <div style='display: flex; align-items: center; gap: 8px; margin-top: -2px;'>
                <span style='font-size: 1.8rem; line-height: 1;'>📈</span>
                <div style='display: flex; flex-direction: column; line-height: 1.1;'>
                    <span style='font-family: Outfit; font-weight: 800; font-size: 1.25rem; color: #00f5d4; letter-spacing: 0.5px;'>StockPulse</span>
                    <span style='font-family: Inter; font-size: 0.62rem; color: #a0aab2; font-weight: 600; letter-spacing: 0.8px;'>MARKET INSIGHTS</span>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with col_nav1:
        if st.button("Dashboard", key="nav_dash", type="primary" if active_page == "Dashboard" else "secondary", use_container_width=True):
            st.switch_page("pages/Dashboard.py")
            
    with col_nav2:
        if st.button("Compare", key="nav_comp", type="primary" if active_page == "Compare" else "secondary", use_container_width=True):
            st.switch_page("pages/Compare.py")
            
    with col_nav3:
        if st.button("Watchlist", key="nav_wl", type="primary" if active_page == "Watchlist" else "secondary", use_container_width=True):
            st.switch_page("pages/Watchlist.py")
            
    with col_nav4:
        if st.button("Portfolio", key="nav_port", type="primary" if active_page == "Portfolio" else "secondary", use_container_width=True):
            st.switch_page("pages/Portfolio.py")
            
    with col_nav5:
        if st.button("History", key="nav_hist", type="primary" if active_page == "History" else "secondary", use_container_width=True):
            st.switch_page("pages/History.py")
            
    with col_nav6:
        if st.button("Profile", key="nav_prof", type="primary" if active_page == "Profile" else "secondary", use_container_width=True):
            st.switch_page("pages/Profile.py")
            
    with col_user:
        if is_logged_in():
            username = get_logged_in_username()
            username_display = username[:12] + ".." if len(username) > 12 else username
            st.markdown(
                f"""
                <div style='text-align: right; margin-top: 2px;'>
                    <span style='color: #00e676; font-size: 0.85rem; font-weight: 700;'>👤 {username_display}</span>
                    <span style='display: block; font-size: 0.65rem; color: #a0aab2; font-weight: 500;'>Premium Plan</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            if st.button("🔐 Login", key="nav_login", use_container_width=True):
                st.switch_page("pages/Profile.py")

    st.markdown("<div style='margin-top:-5px; margin-bottom: 25px; border-bottom: 1px solid rgba(255,255,255,0.06);'></div>", unsafe_allow_html=True)

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

def get_currency_symbol(currency_code: str) -> str:
    """
    Map ISO currency codes to visual symbols.
    """
    if not currency_code:
        return "$"
    mapping = {
        "USD": "$",
        "INR": "₹",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CAD": "C$",
        "AUD": "A$",
        "CNY": "¥"
    }
    return mapping.get(currency_code.upper(), currency_code)

