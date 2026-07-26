import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config

@st.cache_data(ttl=3600)  # Cache stock data for 1 hour to optimize performance
def get_stock_history(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical stock data for a given ticker symbol.
    """
    symbol = symbol.strip().upper()
    if not symbol:
        return pd.DataFrame()
    
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        
        # Ensure index is a DatetimeIndex and timezone naive for compatibility
        if not df.empty:
            df.index = pd.to_datetime(df.index)
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)
        return df
    except Exception as e:
        st.error(f"Error fetching historical data for {symbol}: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)  # Cache company profile info
def get_stock_info(symbol: str) -> dict:
    """
    Fetch company profile metadata and key financial ratios.
    """
    symbol = symbol.strip().upper()
    if not symbol:
        return {}
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Extract only the necessary info safely (yfinance info can be inconsistent)
        profile = {
            "symbol": symbol,
            "name": info.get("longName", info.get("shortName", symbol)),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "summary": info.get("longBusinessSummary", "No description available."),
            "currency": info.get("currency", "USD"),
            "market_cap": info.get("marketCap", None),
            "pe_ratio": info.get("trailingPE", info.get("forwardPE", None)),
            "dividend_yield": info.get("dividendYield", 0.0),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh", None),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow", None),
            "current_price": info.get("currentPrice", info.get("regularMarketPrice", None)),
            "previous_close": info.get("regularMarketPreviousClose", None),
            "volume": info.get("volume", None),
            "website": info.get("website", "N/A")
        }
        
        # If current price is missing, try getting it from recent history
        if profile["current_price"] is None:
            history = get_stock_history(symbol, period="1d")
            if not history.empty:
                profile["current_price"] = history["Close"].iloc[-1]
                
        return profile
    except Exception as e:
        # Fallback if yfinance ticker info fails
        return {
            "symbol": symbol,
            "name": symbol,
            "sector": "N/A",
            "industry": "N/A",
            "summary": f"Could not fetch complete metadata for {symbol}.",
            "currency": "N/A",
            "market_cap": None,
            "pe_ratio": None,
            "dividend_yield": 0.0,
            "fifty_two_week_high": None,
            "fifty_two_week_low": None,
            "current_price": None,
            "previous_close": None,
            "volume": None,
            "website": "N/A"
        }

@st.cache_data(ttl=300)  # Cache index summary for 5 minutes (near live)
def get_market_summary() -> list:
    """
    Fetch current performance stats for major global market indices.
    """
    summary = []
    for ticker_symbol, name in config.DEFAULT_INDICES.items():
        try:
            ticker = yf.Ticker(ticker_symbol)
            # Get latest 5 days to ensure we get a valid trade day
            hist = ticker.history(period="5d")
            if not hist.empty:
                latest_close = hist["Close"].iloc[-1]
                prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else latest_close
                
                # Fetch ticker info for regular market previous close if history close is not matching
                # fallback calculation
                change = latest_close - prev_close
                pct_change = (change / prev_close) * 100 if prev_close != 0 else 0.0
                
                summary.append({
                    "symbol": ticker_symbol,
                    "name": name,
                    "price": latest_close,
                    "change": change,
                    "pct_change": pct_change
                })
        except Exception:
            # Silently skip indices that fail to load
            pass
    return summary

def validate_ticker(symbol: str) -> bool:
    """
    Check if a stock ticker symbol actually exists and returns data.
    """
    symbol = symbol.strip().upper()
    if not symbol:
        return False
    try:
        ticker = yf.Ticker(symbol)
        # Try fetching 1 day history to confirm validity
        hist = ticker.history(period="1d")
        return not hist.empty
    except Exception:
        return False
