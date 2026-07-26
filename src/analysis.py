import pandas as pd
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.stock_api import get_stock_info, get_stock_history

def generate_comparison_table(symbols: list[str]) -> pd.DataFrame:
    """
    Generate a comparative DataFrame of key financial stats for a list of tickers.
    """
    data = []
    for sym in symbols:
        info = get_stock_info(sym)
        if not info:
            continue
            
        # Format values nicely
        mcap = info.get("market_cap")
        if mcap:
            if mcap >= 1e12:
                mcap_str = f"${mcap / 1e12:.2f}T"
            elif mcap >= 1e9:
                mcap_str = f"${mcap / 1e9:.2f}B"
            else:
                mcap_str = f"${mcap / 1e6:.2f}M"
        else:
            mcap_str = "N/A"
            
        pe = info.get("pe_ratio")
        pe_str = f"{pe:.2f}" if pe is not None else "N/A"
        
        div = info.get("dividend_yield")
        div_str = f"{div * 100:.2f}%" if div else "0.00%"
        
        curr_price = info.get("current_price")
        curr_price_str = f"${curr_price:.2f}" if curr_price is not None else "N/A"
        
        high_52w = info.get("fifty_two_week_high")
        high_str = f"${high_52w:.2f}" if high_52w is not None else "N/A"
        
        low_52w = info.get("fifty_two_week_low")
        low_str = f"${low_52w:.2f}" if low_52w is not None else "N/A"
        
        data.append({
            "Ticker": sym.upper(),
            "Company Name": info.get("name", sym),
            "Current Price": curr_price_str,
            "Market Cap": mcap_str,
            "P/E Ratio": pe_str,
            "Div. Yield": div_str,
            "52W High": high_str,
            "52W Low": low_str,
            "Sector": info.get("sector", "N/A")
        })
        
    return pd.DataFrame(data)

def calculate_correlation_matrix(symbols: list[str], period: str = "1y") -> pd.DataFrame:
    """
    Download price history and calculate the correlation matrix of daily returns.
    """
    returns_dict = {}
    
    for sym in symbols:
        sym = sym.strip().upper()
        df = get_stock_history(sym, period=period)
        if not df.empty and "Close" in df.columns:
            # Calculate daily returns
            returns_dict[sym] = df["Close"].pct_change()
            
    if not returns_dict:
        return pd.DataFrame()
        
    # Combine returns into a single DataFrame
    combined_df = pd.DataFrame(returns_dict)
    
    # Calculate Pearson correlation matrix
    return combined_df.corr().round(3)
