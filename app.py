import streamlit as st
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.dirname(__file__))

# Configure page settings BEFORE importing other packages that might render elements
st.set_page_config(
    page_title="StockPulse - Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.database import init_db
from src.utils import inject_custom_css, display_sidebar_auth, render_metric_card
from src.stock_api import get_market_summary

# Initialize the local SQLite database
init_db()

# Inject modern dark glassmorphism styling
inject_custom_css()

# Render Auth Widget in the sidebar
display_sidebar_auth()

# Main page layout
st.markdown('<div class="gradient-text">StockPulse</div>', unsafe_allow_html=True)
st.markdown('<div class="gradient-subtitle">Your Premium, Serverless Stock Market Analysis & Portfolio Dashboard</div>', unsafe_allow_html=True)

# ----------------- Market Summary Header -----------------
st.subheader("🌍 Global Market Overview")
indices_data = get_market_summary()

if not indices_data:
    st.info("Unable to fetch live market summaries. Check your internet connection.")
else:
    cols = st.columns(len(indices_data))
    for col, idx_info in zip(cols, indices_data):
        with col:
            # Custom styled metric card
            is_pos = idx_info["change"] >= 0
            change_sign = "+" if is_pos else ""
            change_str = f"{change_sign}{idx_info['change']:.2f} ({change_sign}{idx_info['pct_change']:.2f}%)"
            
            render_metric_card(
                label=idx_info["name"],
                value=f"{idx_info['price']:,.2f}",
                change=change_str,
                is_positive=is_pos
            )

st.markdown("<br><br>", unsafe_allow_html=True)

# ----------------- Dashboard Feature Presentation -----------------
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown(
        """
        <div class="glass-card">
            <h3>🚀 Welcome to StockPulse</h3>
            <p>StockPulse is a lightweight, local-first stock intelligence tool. By utilizing cached public queries, 
            it provides live technical analysis, interactive visualizations, and account tracking—all completely free of cost.</p>
            
            <h4>✨ Core Capabilities:</h4>
            <ul>
                <li><b>Market Dashboard</b>: Real-time stock querying with interactive candlestick charts, volumes, and standard overlays (SMA/EMA).</li>
                <li><b>Technical Indicators</b>: In-depth charts for <b>RSI</b> and <b>MACD</b> convergence, giving you insight into momentum and trends.</li>
                <li><b>Historical Exporter</b>: Review tabular price logs and instantly download historical stock logs in raw CSV formats.</li>
                <li><b>Comparative Analysis</b>: Chart normalized percentage returns of up to 5 stocks concurrently to compare index-beating performances.</li>
                <li><b>Watchlist Sparklines</b>: Build stock watchlists showing recent 5-day mini-trends inside clean cards.</li>
                <li><b>Portfolio Manager</b>: Record simulated BUY/SELL transactions to automatically compute live profits/losses, returns on investment, and sector allocations.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="glass-card">
            <h3>🔒 Secure, Local-First Account Management</h3>
            <p>To use personalization features like your custom <b>Watchlist</b> or <b>Portfolio Tracker</b>, 
            you need a free local account. Creating an account is easy:</p>
            <ol>
                <li>Navigate to the <b>Profile</b> page in the sidebar.</li>
                <li>Register a new username and password.</li>
                <li>Log in! Your settings, transactions, and tickers will save inside your local database.</li>
            </ol>
            <p><i>Your credentials are fully secure and hashed locally on your computer—never sent to any external server.</i></p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.info("💡 Pro Tip: Select a page from the sidebar (e.g., 'Dashboard' or 'Profile') to get started!")
