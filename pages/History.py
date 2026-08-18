import streamlit as st
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.set_page_config(page_title="StockPulse - History", page_icon="📂", layout="wide")

from src.utils import inject_custom_css, render_top_navbar
import src.stock_api as api
import src.indicators as indicators
import src.charts as charts

# Inject CSS and top navigation
inject_custom_css()
render_top_navbar("History")


st.title("📂 Historical Stock Data Explorer")

# Search stock ticker
ticker_input = st.text_input("🔍 Search Stock Ticker Symbol", value="AAPL")

if ticker_input:
    ticker = ticker_input.strip().upper()
    
    # Validate ticker
    valid = api.validate_ticker(ticker)
    
    if not valid:
        st.error(f"Could not load data for symbol '{ticker}'. Please verify the ticker.")
    else:
        # Configuration columns
        col_c1, col_c2 = st.columns([1, 3])
        with col_c1:
            period = st.selectbox(
                "📅 Time Period",
                options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
                index=3,
                key="history_period"
            )
            
        # Download historical data
        with st.spinner("Loading historical logs..."):
            df = api.get_stock_history(ticker, period=period)
            
        if df.empty:
            st.warning("No data found for the selected symbol and timeframe.")
        else:
            # ----------------- CSV Exporter -----------------
            st.markdown("<br>", unsafe_allow_html=True)
            col_d1, col_d2 = st.columns([4, 1])
            with col_d1:
                st.subheader(f"📊 Historical Price Table: {ticker}")
            with col_d2:
                # Prepare CSV data for export
                csv_data = df.to_csv(index=True)
                st.download_button(
                    label="📥 Export to CSV",
                    data=csv_data,
                    file_name=f"StockPulse_{ticker}_{period}_history.csv",
                    mime="text/csv"
                )
                
            # Render historical table
            # We reverse the dataframe to show latest dates first in the table
            table_df = df.copy()
            table_df.index = table_df.index.strftime('%Y-%m-%d')
            st.dataframe(table_df.iloc[::-1], use_container_width=True)
            
            # ----------------- Return & Volatility Analysis -----------------
            st.markdown("<br><hr style='border-color: rgba(255,255,255,0.05)'><br>", unsafe_allow_html=True)
            st.subheader("⚡ Daily Returns & Volatility Analytics")
            
            # Compute daily returns
            daily_returns = indicators.calculate_daily_returns(df).dropna()
            
            if not daily_returns.empty:
                # Compute statistical aggregates
                mean_return = daily_returns.mean()
                std_dev = daily_returns.std()
                max_gain = daily_returns.max()
                max_loss = daily_returns.min()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Avg. Daily Return", f"{mean_return:.3f}%")
                with col2:
                    st.metric("Daily Volatility (StdDev)", f"{std_dev:.3f}%")
                with col3:
                    st.metric("Max Daily Gain", f"+{max_gain:.2f}%")
                with col4:
                    st.metric("Max Daily Loss", f"{max_loss:.2f}%")
                    
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Render Returns Histogram
                fig_dist = charts.plot_returns_dist(df, title=f"{ticker} Daily Returns Distribution Histogram")
                st.plotly_chart(fig_dist, use_container_width=True)
            else:
                st.info("Not enough data to calculate returns analysis.")
