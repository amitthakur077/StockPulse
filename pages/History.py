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
st.caption("Search by company name — no need to know the ticker symbol!")

# ---- Company Name Search ----
col_h1, col_h2 = st.columns([2.5, 2])
with col_h1:
    search_q = st.text_input(
        "Company name or ticker",
        placeholder="e.g. Rail nigam, Reliance, Tata Motors, Apple, RVNL.NS...",
        label_visibility="collapsed",
        key="hist_search"
    )

resolved_ticker = None
if search_q:
    matches = api.search_tickers_by_name(search_q)
    if matches:
        with col_h2:
            labels = [m["label"] for m in matches]
            chosen = st.selectbox("💡 Recommendations:", labels, label_visibility="collapsed", key="hist_dropdown")
            if chosen:
                idx = labels.index(chosen)
                resolved_ticker = matches[idx]["symbol"]
    else:
        st.warning(f"No match found for '{search_q}'. Try another company name.")

if resolved_ticker:
    ticker = resolved_ticker.strip().upper()

    # Validate ticker
    valid = api.validate_ticker(ticker)

    if not valid:
        st.error(f"Could not load data for '{ticker}'. Please try another company.")
    else:
        info = api.get_stock_info(ticker)
        company_name = info.get("name", ticker)
        st.markdown(f"### 🏢 {company_name} `({ticker})`")

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
        with st.spinner("Loading historical data..."):
            df = api.get_stock_history(ticker, period=period)

        if df.empty:
            st.warning("No data found for the selected company and timeframe.")
        else:
            # ----------------- CSV Exporter -----------------
            st.markdown("<br>", unsafe_allow_html=True)
            col_d1, col_d2 = st.columns([4, 1])
            with col_d1:
                st.subheader(f"📊 Historical Price Table: {company_name}")
            with col_d2:
                csv_data = df.to_csv(index=True)
                st.download_button(
                    label="📥 Export to CSV",
                    data=csv_data,
                    file_name=f"StockPulse_{ticker}_{period}_history.csv",
                    mime="text/csv"
                )

            # Render historical table (latest first, prices in ₹)
            table_df = df.copy()
            table_df.index = table_df.index.strftime('%Y-%m-%d')
            # Format price columns to show ₹
            for col in ["Open", "High", "Low", "Close"]:
                if col in table_df.columns:
                    table_df[col] = table_df[col].apply(lambda x: f"₹{x:,.2f}" if x else "N/A")
            st.dataframe(table_df.iloc[::-1], width='stretch')

            # ----------------- Return & Volatility Analysis -----------------
            st.markdown("<br><hr style='border-color: rgba(255,255,255,0.05)'><br>", unsafe_allow_html=True)
            st.subheader("⚡ Daily Returns & Volatility Analytics")

            # Compute daily returns
            daily_returns = indicators.calculate_daily_returns(api.get_stock_history(ticker, period=period)).dropna()

            if not daily_returns.empty:
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
                orig_df = api.get_stock_history(ticker, period=period)
                fig_dist = charts.plot_returns_dist(orig_df, title=f"{company_name} ({ticker}) Daily Returns Distribution")
                st.plotly_chart(fig_dist, width='stretch')
            else:
                st.info("Not enough data to calculate returns analysis.")
else:
    st.info("🔍 Start typing a company name above to explore its price history.")
