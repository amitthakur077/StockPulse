import streamlit as st
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.set_page_config(page_title="StockPulse - Watchlist", page_icon="⭐", layout="wide")

from src.database import SessionLocal
from src.utils import inject_custom_css, render_top_navbar
import src.auth as auth
import src.stock_api as api
import src.watchlist as wl
import src.charts as charts

# Inject CSS and top navigation
inject_custom_css()
render_top_navbar("Watchlist")


st.title("⭐ My Watchlist")

if not auth.is_logged_in():
    st.warning("🔒 Please Log In to access your Watchlist.")
    st.info("Navigate to the **Profile** page in the sidebar to log in or create a free account.")
else:
    db = SessionLocal()
    user_id = auth.get_logged_in_user_id()

    try:
        # ---- Add Stock by Company Name ----
        st.subheader("➕ Add Stock to Watchlist")
        st.caption("Search by company name — no need to know the ticker symbol!")

        col_s1, col_s2, col_s3 = st.columns([2.5, 2, 1])
        with col_s1:
            search_q = st.text_input(
                "Search company name",
                placeholder="e.g. Rail nigam, Reliance, Tata Motors, State Bank, Apple...",
                label_visibility="collapsed",
                key="wl_search"
            )
        
        resolved_ticker = None
        if search_q:
            matches = api.search_tickers_by_name(search_q)
            if matches:
                with col_s2:
                    labels = [m["label"] for m in matches]
                    chosen = st.selectbox("💡 Recommendations:", labels, label_visibility="collapsed", key="wl_recommend")
                    if chosen:
                        idx = labels.index(chosen)
                        resolved_ticker = matches[idx]["symbol"]
            else:
                st.warning(f"No company found for '{search_q}'. Try a different name.")

        with col_s3:
            if st.button("➕ Add to Watchlist", width='stretch', type="primary"):
                if resolved_ticker:
                    if api.validate_ticker(resolved_ticker):
                        success, msg = wl.add_to_watchlist(db, user_id, resolved_ticker)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.error(f"Could not validate '{resolved_ticker}'. Please try another.")
                elif search_q:
                    st.warning("Please select a company from the dropdown first.")
                else:
                    st.warning("Please type a company name to search.")

        # Manual ticker fallback for advanced users
        with st.expander("⚙️ Advanced: Add by ticker symbol directly"):
            col_t1, col_t2 = st.columns([3, 1])
            with col_t1:
                manual_ticker = st.text_input(
                    "Ticker",
                    placeholder="e.g. RVNL.NS, AAPL, TSLA",
                    label_visibility="collapsed",
                    key="wl_manual_ticker"
                ).strip().upper()
            with col_t2:
                if st.button("Add Ticker", width='stretch'):
                    if manual_ticker:
                        if api.validate_ticker(manual_ticker):
                            success, msg = wl.add_to_watchlist(db, user_id, manual_ticker)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                        else:
                            st.error(f"'{manual_ticker}' is not a valid stock ticker.")
                    else:
                        st.warning("Please enter a ticker symbol.")

        st.markdown("<br><hr style='border-color: rgba(255,255,255,0.05)'><br>", unsafe_allow_html=True)
        st.subheader("📋 Tracked Securities")

        watchlist_symbols = wl.get_user_watchlist(db, user_id)

        if not watchlist_symbols:
            st.info("Your watchlist is currently empty. Add stocks above or from the main Dashboard.")
        else:
            # Loop through watchlist and fetch summary data
            for sym in watchlist_symbols:
                info = api.get_stock_info(sym)
                hist = api.get_stock_history(sym, period="5d")  # 5 days for sparkline

                curr_price = info.get("current_price")
                prev_close = info.get("previous_close")

                # All prices in ₹
                price_str = f"₹{curr_price:,.2f}" if curr_price is not None else "N/A"
                change_str = "N/A"
                is_pos = True

                if curr_price is not None and prev_close is not None and prev_close != 0:
                    change = curr_price - prev_close
                    pct_change = (change / prev_close) * 100
                    sign = "+" if change >= 0 else ""
                    change_str = f"{sign}₹{abs(change):,.2f} ({sign}{pct_change:.2f}%)"
                    is_pos = change >= 0

                card_container = st.container()
                with card_container:
                    col1, col2, col3, col4 = st.columns([3, 3, 4, 2])

                    with col1:
                        st.markdown(f"### **{sym}**")
                        st.caption(info.get("name", sym))

                    with col2:
                        color_style = "color: #00e676;" if is_pos else "color: #ff3366;"
                        st.markdown(f"#### **{price_str}**")
                        st.markdown(
                            f"<span style='{color_style} font-size: 0.9rem; font-weight: 600;'>{change_str}</span>",
                            unsafe_allow_html=True
                        )

                    with col3:
                        if not hist.empty:
                            fig_spark = charts.plot_sparkline(hist)
                            st.plotly_chart(fig_spark, width='stretch', config={'displayModeBar': False})
                        else:
                            st.caption("Sparkline unavailable")

                    with col4:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🗑️ Remove", key=f"rm_{sym}", width='stretch'):
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
