import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.set_page_config(page_title="StockPulse - Portfolio", page_icon="💼", layout="wide")

from src.database import SessionLocal
from src.utils import inject_custom_css, render_top_navbar, render_metric_card
import src.auth as auth
import src.stock_api as api
import src.portfolio as port

# Inject CSS and top navigation
inject_custom_css()
render_top_navbar("Portfolio")


st.title("💼 Portfolio Management")

if not auth.is_logged_in():
    st.warning("🔒 Please Log In to manage your Portfolio.")
    st.info("Navigate to the **Profile** page in the sidebar to log in or create a free account.")
else:
    db = SessionLocal()
    user_id = auth.get_logged_in_user_id()
    
    try:
        # Fetch latest portfolio calculations
        with st.spinner("Calculating portfolio values..."):
            summary = port.calculate_portfolio_summary(db, user_id)
            
        holdings = summary["holdings"]
        transactions = summary["transactions"]
        
        # ----------------- Portfolio Totals Summary -----------------
        total_invested = summary["total_invested"]
        total_val = summary["total_value"]
        total_pnl = summary["total_pnl"]
        total_pnl_pct = summary["total_pnl_pct"]
        
        is_pos = total_pnl >= 0
        sign = "+" if is_pos else ""
        pnl_val_str = f"{sign}${total_pnl:,.2f}"
        pnl_pct_str = f"({sign}{total_pnl_pct:.2f}%)"
        
        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric_card("Total Invested", f"${total_invested:,.2f}")
        with col2:
            render_metric_card("Current Value", f"${total_val:,.2f}")
        with col3:
            render_metric_card("Total Profit / Loss", pnl_val_str, pnl_pct_str, is_pos)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ----------------- Transaction Logger Form (Expander) -----------------
        with st.expander("📝 Log New BUY / SELL Transaction"):
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                tx_ticker = st.text_input("Stock Ticker", placeholder="e.g. AAPL").strip().upper()
            with col_f2:
                tx_type = st.selectbox("Transaction Type", ["BUY", "SELL"])
            with col_f3:
                tx_shares = st.number_input("Shares Quantity", min_value=0.0001, step=1.0, format="%.4f")
            with col_f4:
                tx_price = st.number_input("Price per Share ($)", min_value=0.01, step=0.1, format="%.2f")
                
            if st.button("Submit Transaction", type="primary"):
                if not tx_ticker:
                    st.error("Please enter a valid stock ticker symbol.")
                elif tx_shares <= 0 or tx_price <= 0:
                    st.error("Shares and price must be greater than zero.")
                else:
                    with st.spinner("Recording transaction..."):
                        if api.validate_ticker(tx_ticker):
                            success, msg = port.add_portfolio_transaction(
                                db=db,
                                user_id=user_id,
                                symbol=tx_ticker,
                                transaction_type=tx_type,
                                shares=tx_shares,
                                price=tx_price
                            )
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                        else:
                            st.error(f"'{tx_ticker}' is not a valid stock ticker symbol.")
                            
        st.markdown("<br><hr style='border-color: rgba(255,255,255,0.05)'><br>", unsafe_allow_html=True)

        if not holdings:
            st.info("You do not hold any stocks in your portfolio. Log a BUY transaction above to get started!")
        else:
            # ----------------- Active Holdings Grid -----------------
            st.subheader("📊 Current Stock Holdings")
            
            holdings_rows = []
            for h in holdings:
                holdings_rows.append({
                    "Symbol": h["symbol"],
                    "Company": h["name"],
                    "Shares": round(h["shares"], 4),
                    "Avg Cost": f"${h['avg_price']:.2f}",
                    "Total Cost": f"${h['total_cost']:.2f}",
                    "Current Price": f"${h['current_price']:.2f}",
                    "Current Value": f"${h['current_value']:.2f}",
                    "P/L ($)": f"${h['pnl']:.2f}",
                    "P/L (%)": f"{h['pnl_pct']:.2f}%",
                    "Allocation (%)": f"{(h['current_value']/total_val)*100:.2f}%" if total_val != 0 else "0.00%"
                })
                
            holdings_df = pd.DataFrame(holdings_rows)
            st.dataframe(holdings_df, use_container_width=True, hide_index=True)
            
            # ----------------- Visual Allocation Charts -----------------
            st.markdown("<br>", unsafe_allow_html=True)
            col_chart1, col_chart2 = st.columns(2)
            
            holdings_raw_df = pd.DataFrame(holdings)
            
            with col_chart1:
                st.write("##### Asset Allocation (by Value)")
                fig_asset = px.pie(
                    holdings_raw_df,
                    values="current_value",
                    names="symbol",
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Plasma
                )
                fig_asset.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=auth.st.session_state.get("text_secondary", "#a0aab2"), family="Outfit, sans-serif")
                )
                st.plotly_chart(fig_asset, use_container_width=True)
                
            with col_chart2:
                st.write("##### Sector Allocation")
                # Group by sector
                sector_df = holdings_raw_df.groupby("sector", as_index=False)["current_value"].sum()
                fig_sector = px.pie(
                    sector_df,
                    values="current_value",
                    names="sector",
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Agsunset
                )
                fig_sector.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#a0aab2", family="Outfit, sans-serif")
                )
                st.plotly_chart(fig_sector, use_container_width=True)

        # ----------------- Transaction Log History -----------------
        if transactions:
            st.markdown("<br><hr style='border-color: rgba(255,255,255,0.05)'><br>", unsafe_allow_html=True)
            st.subheader("📜 Transaction Audit Log")
            
            log_rows = []
            for t in transactions:
                log_rows.append({
                    "Date": t.transaction_date.strftime("%Y-%m-%d %H:%M"),
                    "Symbol": t.symbol,
                    "Action": t.transaction_type,
                    "Shares": round(t.shares, 4),
                    "Price per Share": f"${t.price:.2f}",
                    "Total Amount": f"${t.shares * t.price:.2f}"
                })
                
            log_df = pd.DataFrame(log_rows)
            st.dataframe(log_df, use_container_width=True, hide_index=True)
            
    finally:
        db.close()
