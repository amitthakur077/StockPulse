import streamlit as st
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import SessionLocal
from src.utils import inject_custom_css, display_sidebar_auth, render_metric_card
import src.stock_api as api
import src.indicators as indicators
import src.charts as charts
import src.auth as auth
import src.watchlist as wl
import src.reports as rep

# Inject CSS and sidebar authentication state
inject_custom_css()
display_sidebar_auth()

st.title("📈 Stock Analysis Dashboard")

# Search stock ticker
ticker_input = st.text_input("🔍 Search Stock Ticker Symbol (e.g., AAPL, MSFT, TSLA, GOOGL)", value="AAPL")

if ticker_input:
    ticker = ticker_input.strip().upper()
    
    # Validate ticker
    with st.spinner(f"Verifying ticker {ticker}..."):
        valid = api.validate_ticker(ticker)
        
    if not valid:
        st.error(f"Could not load data for symbol '{ticker}'. Please verify the ticker is valid (e.g., AAPL, TSLA).")
    else:
        # Fetch stock details
        with st.spinner("Fetching stock metrics..."):
            info = api.get_stock_info(ticker)
            
        # ----------------- Watchlist Button (Logged In Only) -----------------
        if auth.is_logged_in():
            db = SessionLocal()
            user_id = auth.get_logged_in_user_id()
            try:
                is_watched = wl.is_in_watchlist(db, user_id, ticker)
                if is_watched:
                    if st.button("➖ Remove from Watchlist", key="dashboard_wl_btn"):
                        success, msg = wl.remove_from_watchlist(db, user_id, ticker)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    if st.button("➕ Add to Watchlist", key="dashboard_wl_btn"):
                        success, msg = wl.add_to_watchlist(db, user_id, ticker)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            finally:
                db.close()
                
        # ----------------- Display Core Stats -----------------
        curr_price = info.get("current_price")
        prev_close = info.get("previous_close")
        
        price_val = f"${curr_price:.2f}" if curr_price is not None else "N/A"
        change_val = "N/A"
        is_pos = True
        
        if curr_price is not None and prev_close is not None:
            change = curr_price - prev_close
            pct_change = (change / prev_close) * 100
            sign = "+" if change >= 0 else ""
            change_val = f"{sign}{change:.2f} ({sign}{pct_change:.2f}%)"
            is_pos = change >= 0

        st.subheader(f"🏢 {info.get('name', ticker)} Summary")
        
        # Grid layout for company metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            render_metric_card("Current Price", price_val, change_val, is_pos)
        with col2:
            mcap = info.get("market_cap")
            mcap_str = f"${mcap/1e9:.2f}B" if mcap and mcap >= 1e9 else (f"${mcap/1e6:.2f}M" if mcap else "N/A")
            render_metric_card("Market Cap", mcap_str)
        with col3:
            pe = info.get("pe_ratio")
            pe_str = f"{pe:.2f}" if pe is not None else "N/A"
            render_metric_card("P/E Ratio", pe_str)
        with col4:
            high_52w = info.get("fifty_two_week_high")
            high_str = f"${high_52w:.2f}" if high_52w is not None else "N/A"
            render_metric_card("52W High", high_str)
        with col5:
            low_52w = info.get("fifty_two_week_low")
            low_str = f"${low_52w:.2f}" if low_52w is not None else "N/A"
            render_metric_card("52W Low", low_str)

        # ----------------- Timeframe Selection -----------------
        st.markdown("<br>", unsafe_allow_html=True)
        col_t1, col_t2 = st.columns([1, 4])
        with col_t1:
            period = st.selectbox(
                "📅 Time Period",
                options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
                index=3
            )
        
        # Fetch historical data
        with st.spinner("Downloading price history..."):
            df = api.get_stock_history(ticker, period=period)

        if df.empty:
            st.warning("Historical data is empty for this timeframe.")
        else:
            # ----------------- Chart Overlays & Indicators -----------------
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Sub-selections for Moving Averages
            st.markdown("##### 🛠️ Chart Overlays")
            col_o1, col_o2, col_o3 = st.columns(3)
            with col_o1:
                show_sma = st.checkbox("Simple Moving Average (SMA)")
                sma_period = st.selectbox("SMA Period", options=[20, 50, 100, 200], index=1, disabled=not show_sma)
            with col_o2:
                show_ema = st.checkbox("Exponential Moving Average (EMA)")
                ema_period = st.selectbox("EMA Period", options=[9, 21, 50, 100], index=1, disabled=not show_ema)
            
            # Calculate overlay indicators
            ma_lines = {}
            if show_sma:
                ma_lines[f"SMA {sma_period}"] = indicators.calculate_sma(df, sma_period)
            if show_ema:
                ma_lines[f"EMA {ema_period}"] = indicators.calculate_ema(df, ema_period)

            # Generate and Plot Candlestick Chart
            fig_price = charts.plot_candlestick(df, ma_lines, title=f"{ticker} Price Candlestick Chart ({period})")
            st.plotly_chart(fig_price, use_container_width=True)

            # Generate and Plot Volume Chart
            fig_vol = charts.plot_volume(df, title=f"{ticker} Trading Volume")
            st.plotly_chart(fig_vol, use_container_width=True)

            # Expander panels for Technical Indicators
            tab_rsi, tab_macd = st.tabs(["📊 Relative Strength Index (RSI)", "📊 MACD Convergence"])
            
            with tab_rsi:
                st.markdown("RSI gauges momentum by evaluating overbought (>70) and oversold (<30) territories.")
                fig_rsi = charts.plot_rsi(df)
                if fig_rsi:
                    st.plotly_chart(fig_rsi, use_container_width=True)
                else:
                    st.info("Not enough data to calculate RSI.")

            with tab_macd:
                st.markdown("MACD computes trend momentum by examining exponential moving average crossovers.")
                fig_macd = charts.plot_macd(df)
                if fig_macd:
                    st.plotly_chart(fig_macd, use_container_width=True)
                else:
                    st.info("Not enough data to calculate MACD.")

            # ----------------- Business Details & Description -----------------
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="glass-card">
                    <h3>🏢 About {info.get('name', ticker)}</h3>
                    <p><b>Sector:</b> {info.get('sector', 'N/A')} | <b>Industry:</b> {info.get('industry', 'N/A')}</p>
                    <p><b>Official Website:</b> <a href="{info.get('website', '#')}" target="_blank">{info.get('website', 'N/A')}</a></p>
                    <hr style="border-color: rgba(255,255,255,0.05)">
                    <p>{info.get('summary', 'No summary description available.')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # ----------------- PDF / Markdown Report Generator -----------------
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📋 Analysis Report Exporter")
            st.write("Generate a printable summary report evaluating this stock's financials and technical posture.")
            
            report_content = rep.generate_markdown_report(ticker, info, df)
            
            st.download_button(
                label=f"📥 Download {ticker} Report (.md)",
                data=report_content,
                file_name=f"StockPulse_{ticker}_Report.md",
                mime="text/markdown"
            )
