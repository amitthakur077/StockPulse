import streamlit as st
import pandas as pd
import yfinance as yf
import sys
import os
import re

# Ensure the root directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# st.set_page_config MUST be the very first Streamlit command
st.set_page_config(
    page_title="StockPulse - Dashboard",
    page_icon="📈",
    layout="wide"
)

from src.database import SessionLocal
from src.utils import inject_custom_css, render_top_navbar, render_metric_card
import src.stock_api as api
import src.indicators as indicators
import src.charts as charts
import src.auth as auth
import src.watchlist as wl
import src.reports as rep

# Inject CSS and render top navbar
inject_custom_css()
render_top_navbar("Dashboard")

# Database session helper
db = SessionLocal()

# ----------------- Autocomplete Search Header -----------------
st.markdown(
    """
    <div style='margin-top: -15px; margin-bottom: 15px;'>
        <h4 style='font-family: Outfit; color: #a0aab2; font-weight: 500; font-size: 1.1rem; margin-bottom: 8px;'>🔍 Stock Search & Discovery (Search by Company Name or Alias)</h4>
    </div>
    """,
    unsafe_allow_html=True
)

search_col1, search_col2 = st.columns([3, 1.5])
with search_col1:
    search_query = st.text_input(
        "Search Stock by Company Name or Alias",
        placeholder="Type company name (e.g. Rail nigam, Reliance, Tata Motors, State Bank, Zomato, Apple)...",
        label_visibility="collapsed",
        key="global_stock_search"
    )

with search_col2:
    quick_options = [
        "⚡ Quick Select Stock...",
        "Rail Vikas Nigam Limited (RVNL.NS)",
        "Reliance Industries (RELIANCE.NS)",
        "Tata Consultancy Services (TCS.NS)",
        "Tata Motors (TATAMOTORS.NS)",
        "State Bank of India (SBIN.NS)",
        "HDFC Bank (HDFCBANK.NS)",
        "Infosys (INFY.NS)",
        "Zomato (ZOMATO.NS)",
        "Apple Inc. (AAPL)",
        "NVIDIA (NVDA)"
    ]
    quick_choice = st.selectbox(
        "Quick Picks",
        options=quick_options,
        label_visibility="collapsed",
        key="dash_quick_choice"
    )

selected_ticker = None

# Check if quick pick was selected
if quick_choice != "⚡ Quick Select Stock...":
    sym_match = re.search(r'\((.*?)\)', quick_choice)
    if sym_match:
        selected_ticker = sym_match.group(1)

# Check search query
if search_query:
    matches = api.search_tickers_by_name(search_query)
    if matches:
        labels = [m["label"] for m in matches]
        selected_label = st.selectbox(
            "💡 Matching Recommendations:",
            options=labels,
            index=0,
            key="dash_search_dropdown"
        )
        if selected_label:
            idx = labels.index(selected_label)
            selected_ticker = matches[idx]["symbol"]
    else:
        st.warning("No matching company found. Try searching by company name or alias (e.g. 'Rail nigam', 'Tata', 'Reliance', 'RVNL').")

# ------------------------------------------------------------------
# VIEW 1: Stock Details (Activated when a ticker is selected)
# ------------------------------------------------------------------
if selected_ticker:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("◀ Back to Market Overview", type="secondary"):
        st.rerun()
        
    ticker = selected_ticker.strip().upper()
    
    with st.spinner(f"Loading {ticker} profile..."):
        info = api.get_stock_info(ticker)
        
    # Check Watchlist actions
    if auth.is_logged_in():
        user_id = auth.get_logged_in_user_id()
        is_watched = wl.is_in_watchlist(db, user_id, ticker)
        
        col_wl1, col_wl2 = st.columns([4, 1])
        with col_wl1:
            st.title(f"{info.get('name', ticker)} ({ticker})")
        with col_wl2:
            if is_watched:
                if st.button("➖ Remove from Watchlist", width='stretch'):
                    success, msg = wl.remove_from_watchlist(db, user_id, ticker)
                    if success:
                        st.success(msg)
                        st.rerun()
            else:
                if st.button("➕ Add to Watchlist", width='stretch'):
                    success, msg = wl.add_to_watchlist(db, user_id, ticker)
                    if success:
                        st.success(msg)
                        st.rerun()
    else:
        st.title(f"{info.get('name', ticker)} ({ticker})")
        
    # Stats layout - Standardized to Indian Rupees (₹)
    curr_price = info.get("current_price")
    prev_close = info.get("previous_close")
    price_val = "N/A"
    change_val = "N/A"
    is_pos = True
    
    if curr_price is not None:
        price_val = f"₹{curr_price:,.2f}"
        if prev_close is not None and prev_close != 0:
            change = curr_price - prev_close
            pct_change = (change / prev_close) * 100
            sign = "+" if change >= 0 else ""
            change_val = f"{sign}₹{abs(change):,.2f} ({sign}{pct_change:.2f}%)"
            is_pos = change >= 0

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        render_metric_card("Current Price", price_val, change_val, is_pos)
    with col2:
        mcap = info.get("market_cap")
        mcap_str = f"₹{mcap/1e7:,.2f} Cr" if mcap else "N/A"
        render_metric_card("Market Cap", mcap_str)
    with col3:
        pe = info.get("pe_ratio")
        pe_str = f"{pe:.2f}" if pe is not None else "N/A"
        render_metric_card("P/E Ratio", pe_str)
    with col4:
        high_52w = info.get("fifty_two_week_high")
        high_str = f"₹{high_52w:,.2f}" if high_52w is not None else "N/A"
        render_metric_card("52W High", high_str)
    with col5:
        low_52w = info.get("fifty_two_week_low")
        low_str = f"₹{low_52w:,.2f}" if low_52w is not None else "N/A"
        render_metric_card("52W Low", low_str)

    # Timeframe selection
    st.markdown("<br>", unsafe_allow_html=True)
    col_t1, col_t2 = st.columns([1, 4])
    with col_t1:
        period = st.selectbox("📅 Time Period", options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3, key="stock_detail_period")
        
    with st.spinner("Downloading price history..."):
        df = api.get_stock_history(ticker, period=period)

    if df.empty:
        st.warning("Historical price history is empty.")
    else:
        st.markdown("##### 🛠️ Chart Overlays")
        col_o1, col_o2 = st.columns(2)
        with col_o1:
            show_sma = st.checkbox("Simple Moving Average (SMA)")
            sma_period = st.selectbox("SMA Period", options=[20, 50, 100, 200], index=1, disabled=not show_sma)
        with col_o2:
            show_ema = st.checkbox("Exponential Moving Average (EMA)")
            ema_period = st.selectbox("EMA Period", options=[9, 21, 50, 100], index=1, disabled=not show_ema)

        ma_lines = {}
        if show_sma:
            ma_lines[f"SMA {sma_period}"] = indicators.calculate_sma(df, sma_period)
        if show_ema:
            ma_lines[f"EMA {ema_period}"] = indicators.calculate_ema(df, ema_period)

        fig_price = charts.plot_candlestick(df, ma_lines, title=f"{info.get('name', ticker)} ({ticker}) Price Chart")
        st.plotly_chart(fig_price, width='stretch')

        fig_vol = charts.plot_volume(df, title=f"{ticker} Volume")
        st.plotly_chart(fig_vol, width='stretch')

        tab_rsi, tab_macd = st.tabs(["📊 RSI Analysis", "📊 MACD Indicators"])
        with tab_rsi:
            fig_rsi = charts.plot_rsi(df)
            if fig_rsi:
                st.plotly_chart(fig_rsi, width='stretch')
        with tab_macd:
            fig_macd = charts.plot_macd(df)
            if fig_macd:
                st.plotly_chart(fig_macd, width='stretch')

        st.markdown(
            f"""
            <div class="glass-card">
                <h3>🏢 Profile: {info.get('name', ticker)}</h3>
                <p><b>Sector:</b> {info.get('sector', 'N/A')} | <b>Industry:</b> {info.get('industry', 'N/A')}</p>
                <p><b>Website:</b> <a href="{info.get('website', '#')}" target="_blank">{info.get('website', 'N/A')}</a></p>
                <hr style="border-color: rgba(255,255,255,0.05)">
                <p>{info.get('summary', 'No summary description available.')}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader("📋 Technical Analysis Report")
        report_content = rep.generate_markdown_report(ticker, info, df)
        st.download_button(
            label=f"📥 Download {ticker} Summary Report",
            data=report_content,
            file_name=f"StockPulse_{ticker}_Report.md",
            mime="text/markdown"
        )

# ------------------------------------------------------------------
# VIEW 2: Premium Market Overview (Default Grid Layout)
# ------------------------------------------------------------------
else:
    # ----------------- 1. Top Indices Ticker -----------------
    st.markdown("<h4 style='font-family: Outfit; font-weight: 700; color: #ffffff; margin-bottom:-5px;'>🌍 Indices Overview</h4>", unsafe_allow_html=True)
    
    with st.spinner("Loading index feeds..."):
        indices_data = api.get_market_summary()
        
    if indices_data:
        cols = st.columns(len(indices_data))
        for col, idx in zip(cols, indices_data):
            with col:
                is_pos = idx["change"] >= 0
                sign = "+" if is_pos else ""
                change_str = f"{sign}₹{abs(idx['change']):,.2f} ({sign}{idx['pct_change']:.2f}%)"
                render_metric_card(idx["name"], f"₹{idx['price']:,.2f}", change_str, is_pos)
    else:
        st.info("Market indices are currently offline.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------- 2. Main Row: Nifty Chart & Market Summary -----------------
    col_chart, col_summary = st.columns([3, 1.2])
    
    with col_chart:
        st.markdown(
            """
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <h4 style='font-family: Outfit; font-weight: 700; color: #ffffff; margin: 0;'>📈 NIFTY 50 Benchmark</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Download Nifty data for plotting
        with st.spinner("Downloading Nifty 50 data..."):
            nifty_df = api.get_stock_history("^NSEI", period="6mo")
            
        if not nifty_df.empty:
            fig_nifty = charts.plot_area_chart(nifty_df, title="")
            st.plotly_chart(fig_nifty, width='stretch')
        else:
            st.warning("Nifty 50 historical data is unavailable.")
            
    with col_summary:
        st.markdown("<h4 style='font-family: Outfit; font-weight: 700; color: #ffffff; margin-bottom:5px;'>📊 Market Summary</h4>", unsafe_allow_html=True)
        
        # Advances / Declines simulation based on Nifty return
        nifty_change = 0.5  # Default fallback
        if not nifty_df.empty:
            latest = nifty_df["Close"].iloc[-1]
            prev = nifty_df["Close"].iloc[-2]
            nifty_change = ((latest - prev) / prev) * 100
            
        is_up = nifty_change >= 0
        advances = int(1200 + nifty_change * 300)
        declines = int(800 - nifty_change * 300)
        unchanged = 120
        # Bounds check
        advances = max(100, min(1900, advances))
        declines = max(100, min(1900, declines))
        total_breadth = int((advances / (advances + declines)) * 100) if (advances + declines) > 0 else 50

        with st.container(border=True):
            r1, r2 = st.columns([1, 1])
            with r1:
                st.markdown("<span style='color:#a0aab2;font-size:0.9rem'>🟢 Advances</span>", unsafe_allow_html=True)
            with r2:
                st.markdown(f"<div style='text-align:right;color:#00e676;font-weight:700;font-size:1.05rem'>{advances}</div>", unsafe_allow_html=True)

            r3, r4 = st.columns([1, 1])
            with r3:
                st.markdown("<span style='color:#a0aab2;font-size:0.9rem'>🔴 Declines</span>", unsafe_allow_html=True)
            with r4:
                st.markdown(f"<div style='text-align:right;color:#ff3366;font-weight:700;font-size:1.05rem'>{declines}</div>", unsafe_allow_html=True)

            r5, r6 = st.columns([1, 1])
            with r5:
                st.markdown("<span style='color:#a0aab2;font-size:0.9rem'>⚪ Unchanged</span>", unsafe_allow_html=True)
            with r6:
                st.markdown(f"<div style='text-align:right;color:#ffffff;font-weight:700;font-size:1.05rem'>{unchanged}</div>", unsafe_allow_html=True)

            st.divider()

            r7, r8 = st.columns([1, 1])
            with r7:
                st.markdown("<span style='color:#a0aab2;font-size:0.85rem'>Market Breadth</span>", unsafe_allow_html=True)
            with r8:
                st.markdown(f"<div style='text-align:right;color:#00e676;font-weight:600;font-size:0.85rem'>{total_breadth}% Bullish</div>", unsafe_allow_html=True)

            st.progress(total_breadth / 100.0)

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------- 3. Middle Row: Gainers, Losers, Sectors, Sentiment -----------------
    col_gain, col_lose, col_sect, col_sent = st.columns(4)
    
    # Load gainers/losers
    with st.spinner("Downloading real-time gainers and losers..."):
        gainers, losers = api.get_top_gainers_losers(market="IN")
        
    with col_gain:
        st.markdown("<h5 style='color:#00e676; font-family:Outfit; font-weight:700;'>🚀 Top Gainers</h5>", unsafe_allow_html=True)
        with st.container(border=True):
            if not gainers:
                st.caption("No data available")
            for stock in gainers:
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.markdown(f"**{stock['symbol']}**")
                with c2:
                    price = stock['price']
                    pct = stock['pct_change']
                    st.markdown(f"<div style='text-align:right'>₹{price:,.2f}<br><span style='color:#00e676;font-size:0.75rem;font-weight:600'>+{pct:.2f}%</span></div>", unsafe_allow_html=True)

    with col_lose:
        st.markdown("<h5 style='color:#ff3366; font-family:Outfit; font-weight:700;'>📉 Top Losers</h5>", unsafe_allow_html=True)
        with st.container(border=True):
            if not losers:
                st.caption("No data available")
            for stock in losers:
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.markdown(f"**{stock['symbol']}**")
                with c2:
                    price = stock['price']
                    pct = stock['pct_change']
                    st.markdown(f"<div style='text-align:right'>₹{price:,.2f}<br><span style='color:#ff3366;font-size:0.75rem;font-weight:600'>{pct:.2f}%</span></div>", unsafe_allow_html=True)

    with col_sect:
        st.markdown("<h5 style='color:#ffffff; font-family:Outfit; font-weight:700;'>📊 Sector Performance</h5>", unsafe_allow_html=True)
        with st.spinner("Downloading sector indexes..."):
            sectors = api.get_sector_performance()
        with st.container(border=True):
            for s in sectors:
                change = s["pct_change"]
                sign = "+" if change >= 0 else ""
                color = "#00e676" if change >= 0 else "#ff3366"
                norm_val = min(1.0, max(0.0, (50 + change * 10) / 100))
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;font-size:0.8rem;margin-bottom:2px'>"
                    f"<span style='color:#a0aab2'>{s['name']}</span>"
                    f"<span style='color:{color};font-weight:600'>{sign}{change:.2f}%</span></div>",
                    unsafe_allow_html=True
                )
                st.progress(norm_val)

    with col_sent:
        st.markdown("<h5 style='color:#ffffff; font-family:Outfit; font-weight:700;'>🎯 Sentiment Gauge</h5>", unsafe_allow_html=True)
        sentiment_score = int(50 + nifty_change * 15)
        sentiment_score = max(5, min(95, sentiment_score))
        fig_gauge = charts.plot_sentiment_gauge(sentiment_score)
        st.plotly_chart(fig_gauge, width='stretch')

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------- 4. Bottom Row: Heatmap, News & Watchlist -----------------
    col_heat, col_news, col_wl = st.columns([2.3, 1.9, 1.8])
    
    with col_heat:
        st.markdown("<h5 style='color:#ffffff; font-family:Outfit; font-weight:700;'>🗺️ Treemap Heatmap</h5>", unsafe_allow_html=True)
        
        # Combine gainers & losers list into a single df with mockup market caps
        heatmap_data = []
        mock_caps = {
            "RELIANCE": 19e12, "TCS": 15e12, "HDFCBANK": 12e12, "ICICIBANK": 9e12, "INFY": 6e12,
            "SBIN": 5.5e12, "BHARTIARTL": 5e12, "ITC": 4.8e12, "LT": 4.5e12, "TATAMOTORS": 3.8e12
        }
        for item in gainers + losers:
            sym = item["symbol"]
            heatmap_data.append({
                "symbol": sym,
                "pct_change": item["pct_change"],
                "market_cap": mock_caps.get(sym, 1.5e12)
            })
            
        if heatmap_data:
            df_heat = pd.DataFrame(heatmap_data).drop_duplicates(subset=["symbol"])
            fig_heat = charts.plot_market_heatmap(df_heat)
            st.plotly_chart(fig_heat, width='stretch')
        else:
            st.info("Heatmap is currently loading...")
            
    with col_news:
        st.markdown("<h5 style='color:#ffffff; font-family:Outfit; font-weight:700;'>📰 News & Insights</h5>", unsafe_allow_html=True)
        with st.container(border=True):
            news_items = api.get_market_news()
            if news_items:
                for article in news_items:
                    st.markdown(
                        f"**[{article['title']}]({article['link']})**  \n"
                        f"<span style='font-size:0.75rem; color:#a0aab2;'>{article['publisher']}</span>",
                        unsafe_allow_html=True
                    )
                    st.divider()
            else:
                st.caption("Live financial news is refreshing...")
        
    with col_wl:
        st.markdown("<h5 style='color:#ffffff; font-family:Outfit; font-weight:700;'>⭐ Watchlist Summary</h5>", unsafe_allow_html=True)
        with st.container(border=True):
            if not auth.is_logged_in():
                st.markdown("<div style='text-align:center;padding-top:30px'>🔒<br><span style='color:#a0aab2;font-size:0.85rem'>Log in to view watchlist</span></div>", unsafe_allow_html=True)
            else:
                user_id = auth.get_logged_in_user_id()
                watchlist_items = wl.get_user_watchlist(db, user_id)
                if not watchlist_items:
                    st.caption("Watchlist empty. Search and add stocks!")
                else:
                    for sym in watchlist_items[:6]:
                        info_wl = api.get_stock_info(sym)
                        price   = info_wl.get("current_price") or 0.0
                        close   = info_wl.get("previous_close") or 0.0
                        chg     = price - close
                        chg_pct = (chg / close) * 100 if close > 0 else 0.0
                        color   = "#00e676" if chg >= 0 else "#ff3366"
                        sign    = "+" if chg >= 0 else ""
                        c1, c2 = st.columns([1, 1])
                        with c1:
                            st.markdown(f"**{sym}**  \n<span style='font-size:0.7rem;color:#a0aab2'>{info_wl.get('name', sym)[:18]}</span>", unsafe_allow_html=True)
                        with c2:
                            st.markdown(f"<div style='text-align:right'>₹{price:,.2f}<br><span style='color:{color};font-size:0.75rem;font-weight:600'>{sign}{chg_pct:.2f}%</span></div>", unsafe_allow_html=True)
                        st.divider()

# Close database session
db.close()
