import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os
import re

# Ensure the root directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.set_page_config(page_title="StockPulse - Compare", page_icon="⚖️", layout="wide")

from src.utils import inject_custom_css, render_top_navbar
import src.stock_api as api
import src.analysis as analysis
import src.charts as charts
import config

# Inject CSS and top navigation
inject_custom_css()
render_top_navbar("Compare")

st.title("⚖️ Stock Comparison Engine")
st.markdown("Search and compare stocks by **Company Name** (e.g. *Rail nigam, Reliance, TCS, Apple*) to evaluate growth trends, financial metrics, and correlation.")

# Multi-stock selection by company name
popular_options = [
    "Reliance Industries (RELIANCE.NS)",
    "Tata Consultancy Services (TCS.NS)",
    "Rail Vikas Nigam Limited (RVNL.NS)",
    "Indian Railway Finance Corp (IRFC.NS)",
    "State Bank of India (SBIN.NS)",
    "HDFC Bank (HDFCBANK.NS)",
    "Infosys (INFY.NS)",
    "Tata Motors (TATAMOTORS.NS)",
    "Zomato Limited (ZOMATO.NS)",
    "Adani Ports (ADANIPORTS.NS)",
    "Apple Inc. (AAPL)",
    "Microsoft Corporation (MSFT)",
    "Alphabet / Google (GOOGL)",
    "NVIDIA Corporation (NVDA)"
]

col_s1, col_s2 = st.columns([2.5, 1.5])
with col_s1:
    selected_companies = st.multiselect(
        "🏢 Select Companies to Compare (or search from list):",
        options=popular_options,
        default=["Reliance Industries (RELIANCE.NS)", "Tata Consultancy Services (TCS.NS)"],
        key="compare_multiselect"
    )

with col_s2:
    search_more = st.text_input(
        "🔍 Search & Add Another Company",
        placeholder="Type name (e.g. Rail nigam, ITC, Tesla)...",
        key="compare_search_more"
    )

additional_symbol = None
if search_more:
    matches = api.search_tickers_by_name(search_more)
    if matches:
        labels = [m["label"] for m in matches]
        more_choice = st.selectbox("💡 Matching Recommendations:", labels, key="compare_more_select")
        if more_choice:
            idx = labels.index(more_choice)
            additional_symbol = matches[idx]["symbol"]
    else:
        st.warning(f"No matches found for '{search_more}'.")

# Gather symbols
symbols = []
for item in selected_companies:
    sym_match = re.search(r'\((.*?)\)', item)
    if sym_match:
        symbols.append(sym_match.group(1))

if additional_symbol and additional_symbol not in symbols:
    symbols.append(additional_symbol)

# Optional advanced manual entry
with st.expander("⚙️ Advanced: Enter custom tickers manually (optional)"):
    manual_input = st.text_input("Manual Tickers (comma-separated)", placeholder="e.g. RVNL.NS, IRFC.NS")
    if manual_input:
        for s in manual_input.split(","):
            s_clean = s.strip().upper()
            if s_clean and s_clean not in symbols:
                symbols.append(s_clean)

# Cap at 5 stocks to keep visual layout clean
if len(symbols) > 5:
    st.warning("For clarity, comparisons are limited to 5 stocks. Comparing the first 5 selections.")
    symbols = symbols[:5]

if len(symbols) < 2:
    st.info("💡 Please select or search at least **2 companies** above to start comparison.")
else:
    # Timeframe selector
    col_t1, col_t2 = st.columns([1, 4])
    with col_t1:
        period = st.selectbox(
            "📅 Time Period",
            options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
            index=3,
            key="compare_period"
        )
        
    # Download data for all tickers
    dfs_dict = {}
    valid_symbols = []
    
    with st.spinner("Retrieving company histories for comparison..."):
        for sym in symbols:
            if api.validate_ticker(sym):
                df = api.get_stock_history(sym, period=period)
                if not df.empty:
                    dfs_dict[sym] = df
                    valid_symbols.append(sym)
            else:
                st.error(f"Ticker symbol '{sym}' is invalid. Skipping from comparison.")
                
    if len(valid_symbols) < 2:
        st.warning("Not enough valid company data to perform comparison.")
    else:
        # ----------------- Relative Returns Comparison Chart -----------------
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📈 Normalized Performance Comparison")
        st.markdown(
            "This chart tracks the percentage change of each stock starting from 0% at the "
            "beginning of the period, allowing direct performance comparison."
        )
        
        fig_compare = charts.plot_comparison(dfs_dict, title=f"Cumulative Return Comparison ({period})")
        st.plotly_chart(fig_compare, width='stretch')
        
        # ----------------- Financial Metrics Table -----------------
        st.markdown("<br><hr style='border-color: rgba(255,255,255,0.05)'><br>", unsafe_allow_html=True)
        st.subheader("📊 Key Metrics Comparison (All Prices in ₹)")
        
        with st.spinner("Compiling company financial metrics..."):
            metrics_df = analysis.generate_comparison_table(valid_symbols)
            
        if not metrics_df.empty:
            st.dataframe(metrics_df, width='stretch', hide_index=True)
        else:
            st.info("Unable to compile comparative statistics.")
            
        # ----------------- Correlation Matrix Heatmap -----------------
        st.markdown("<br><hr style='border-color: rgba(255,255,255,0.05)'><br>", unsafe_allow_html=True)
        st.subheader("🔗 Price Return Correlation Matrix")
        st.markdown(
            "Correlation coefficients quantify how stocks move relative to one another. "
            "Values close to `1.0` imply they move in lockstep; close to `0` implies movements are independent."
        )
        
        with st.spinner("Calculating correlation coefficients..."):
            corr_matrix = analysis.calculate_correlation_matrix(valid_symbols, period=period)
            
        if not corr_matrix.empty:
            # Render Plotly Heatmap
            fig_heat = px.imshow(
                corr_matrix,
                text_auto=True,
                color_continuous_scale="Viridis",
                aspect="auto",
                labels=dict(color="Correlation")
            )
            
            # Apply custom styling to the heatmap
            fig_heat.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=charts.COLORS["text_secondary"], family=config.UI_FONTS),
                coloraxis_colorbar=dict(title="Correlation")
            )
            
            st.plotly_chart(fig_heat, width='stretch')
        else:
            st.info("Unable to calculate correlation coefficients.")
