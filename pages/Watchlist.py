import streamlit as st
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import SessionLocal
from src.utils import inject_custom_css, display_sidebar_auth
import src.auth as auth
import src.stock_api as api
import src.watchlist as wl
import src.charts as charts

# Inject CSS and sidebar authentication state
inject_custom_css()
display_sidebar_auth()

st.title("⭐ My Watchlist")

if not auth.is_logged_in():
    st.warning("🔒 Please Log In to access your Watchlist.")
    st.info("Navigate to the **Profile** page in the sidebar to log in or create a free account.")
else:
    db = SessionLocal()
    user_id = auth.get_logged_in_user_id()
    
    try:
        # Quick add ticker form
        st.subheader("➕ Quick Add Ticker")
        col_add1, col_add2 = st.columns([3, 1])
        with col_add1:
            new_ticker = st.text_input("Enter Ticker symbol", placeholder="e.g. AMZN, TSLA, NFLX", label_visibility="collapsed").strip().upper()
        with col_add2:
            if st.button("Add to List", use_container_width=True):
                if new_ticker:
                    if api.validate_ticker(new_ticker):
                        success, msg = wl.add_to_watchlist(db, user_id, new_ticker)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.error(f"'{new_ticker}' is not a valid stock ticker.")
                else:
                    st.warning("Please enter a ticker.")
                    
        st.markdown("<br><hr style='border-color: rgba(255,255,255,0.05)'><br>", unsafe_allow_html=True)
        st.subheader("📋 Tracked Securities")

        watchlist_symbols = wl.get_user_watchlist(db, user_id)

        if not watchlist_symbols:
            st.info("Your watchlist is currently empty. Add stocks above or from the main Dashboard.")
        else:
            # Loop through watchlist and fetch summary data
            for sym in watchlist_symbols:
                info = api.get_stock_info(sym)
                hist = api.get_stock_history(sym, period="5d") # 5 days for sparkline
                
                curr_price = info.get("current_price")
                prev_close = info.get("previous_close")
                
                price_str = f"${curr_price:.2f}" if curr_price is not None else "N/A"
                change_str = "N/A"
                is_pos = True
                
                if curr_price is not None and prev_close is not None:
                    change = curr_price - prev_close
                    pct_change = (change / prev_close) * 100
                    sign = "+" if change >= 0 else ""
                    change_str = f"{sign}{change:.2f} ({sign}{pct_change:.2f}%)"
                    is_pos = change >= 0
                    
                # Create a card for each stock using Streamlit columns
                # Col 1: Symbol & Name
                # Col 2: Current Price & Change
                # Col 3: Sparkline chart
                # Col 4: Action button (remove)
                
                card_container = st.container()
                with card_container:
                    col1, col2, col3, col4 = st.columns([3, 3, 4, 2])
                    
                    with col1:
                        st.markdown(f"### **{sym}**")
                        st.caption(info.get("name", sym))
                        
                    with col2:
                        color_style = "color: #00e676;" if is_pos else "color: #ff3366;"
                        st.markdown(f"#### **{price_str}**")
                        st.markdown(f"<span style='{color_style} font-size: 0.9rem; font-weight: 600;'>{change_str}</span>", unsafe_allow_html=True)
                        
                    with col3:
                        if not hist.empty:
                            fig_spark = charts.plot_sparkline(hist)
                            st.plotly_chart(fig_spark, use_container_width=True, config={'displayModeBar': False})
                        else:
                            st.caption("Sparkline unavailable")
                            
                    with col4:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🗑️ Remove", key=f"rm_{sym}", use_container_width=True):
                            success, msg = wl.remove_from_watchlist(db, user_id, sym)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                                
                    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)
                    st.markdown("<hr style='border-color: rgba(255,255,255,0.03)'>", unsafe_allow_html=True)
    finally:
        db.close()
