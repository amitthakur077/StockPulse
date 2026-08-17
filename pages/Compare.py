import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils import inject_custom_css, render_top_navbar
import src.stock_api as api
import src.analysis as analysis
import src.charts as charts
import config


# Inject CSS and sidebar authentication state
inject_custom_css()
render_top_navbar("Compare")

st.title("⚖️ Stock Comparison Engine")
st.markdown("Enter multiple stock symbols to compare their growth trends, metrics, and price correlation.")

# Text input for multi-stocks
symbols_input = st.text_input("🔍 Enter stock symbols separated by commas (e.g. AAPL, MSFT, GOOGL, AMZN)", value="AAPL, MSFT, GOOGL")

if symbols_input:
    # Clean and split symbols
    symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]
    
    # Cap at 5 stocks to keep visual layout clean
    if len(symbols) > 5:
        st.warning("For clarity, comparisons are limited to 5 stocks. Showing the first 5 symbols.")
        symbols = symbols[:5]
        
    if len(symbols) < 2:
        st.info("Please enter at least 2 stock symbols to compare.")
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
        
        with st.spinner("Retrieving histories for comparison..."):
            for sym in symbols:
                if api.validate_ticker(sym):
                    df = api.get_stock_history(sym, period=period)
                    if not df.empty:
                        dfs_dict[sym] = df
                        valid_symbols.append(sym)
                else:
                    st.error(f"Ticker symbol '{sym}' is invalid. Skipping from comparison.")
                    
        if len(valid_symbols) < 2:
            st.warning("Not enough valid ticker symbols to perform comparison.")
        else:
            # ----------------- Relative Returns Comparison Chart -----------------
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📈 Normalized Performance Comparison")
            st.markdown(
                "This chart tracks the percentage change of each stock starting from 0% at the "
                "beginning of the period, allowing direct performance comparison."
            )
            
            fig_compare = charts.plot_comparison(dfs_dict, title=f"Cumulative Return Comparison ({period})")
            st.plotly_chart(fig_compare, use_container_width=True)
            
            # ----------------- Financial Metrics Table -----------------
            st.markdown("<br><hr style='border-color: rgba(255,255,255,0.05)'><br>", unsafe_allow_html=True)
            st.subheader("📊 Key Metrics Comparison")
            
            with st.spinner("Compiling metrics..."):
                metrics_df = analysis.generate_comparison_table(valid_symbols)
                
            if not metrics_df.empty:
                st.dataframe(metrics_df, use_container_width=True, hide_index=True)
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
                
                st.plotly_chart(fig_heat, use_container_width=True)
            else:
                st.info("Unable to calculate correlation coefficients.")
