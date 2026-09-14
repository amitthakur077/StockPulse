import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import sys
import os
import requests

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
            "currency": "INR",
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
            history = get_stock_history(symbol, period="5d")
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
            "currency": "INR",
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
        hist = ticker.history(period="5d")
        return not hist.empty
    except Exception:
        return False

# Curated catalog of popular Indian and US stocks with natural language search aliases
POPULAR_STOCKS = [
    # Indian Rail & Infra
    {"symbol": "RVNL.NS", "name": "Rail Vikas Nigam Limited", "exchange": "NSE", "aliases": ["rail nigam", "rvnl", "rail vikas", "railway nigam", "railway", "rail"]},
    {"symbol": "IRFC.NS", "name": "Indian Railway Finance Corporation", "exchange": "NSE", "aliases": ["irfc", "railway finance", "indian railway finance"]},
    {"symbol": "IRCTC.NS", "name": "Indian Railway Catering & Tourism Corp", "exchange": "NSE", "aliases": ["irctc", "railway catering", "rail catering", "catering"]},
    {"symbol": "IRCON.NS", "name": "Ircon International Limited", "exchange": "NSE", "aliases": ["ircon", "railway construction"]},
    {"symbol": "RAILTEL.NS", "name": "RailTel Corporation of India", "exchange": "NSE", "aliases": ["railtel", "railway telecom"]},
    {"symbol": "BEML.NS", "name": "BEML Limited", "exchange": "NSE", "aliases": ["beml", "rail coach"]},
    {"symbol": "TITAGARH.NS", "name": "Titagarh Rail Systems", "exchange": "NSE", "aliases": ["titagarh", "rail wagon"]},

    # Major Indian Equities
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries Limited", "exchange": "NSE", "aliases": ["reliance", "ril", "jio", "mukesh ambani"]},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "exchange": "NSE", "aliases": ["tcs", "tata consultancy"]},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank Limited", "exchange": "NSE", "aliases": ["hdfc", "hdfc bank"]},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank Limited", "exchange": "NSE", "aliases": ["icici", "icici bank"]},
    {"symbol": "INFY.NS", "name": "Infosys Limited", "exchange": "NSE", "aliases": ["infosys", "infy"]},
    {"symbol": "SBIN.NS", "name": "State Bank of India", "exchange": "NSE", "aliases": ["sbi", "sbin", "state bank", "state bank of india"]},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel Limited", "exchange": "NSE", "aliases": ["airtel", "bharti airtel"]},
    {"symbol": "ITC.NS", "name": "ITC Limited", "exchange": "NSE", "aliases": ["itc"]},
    {"symbol": "LT.NS", "name": "Larsen & Toubro Limited", "exchange": "NSE", "aliases": ["l&t", "lt", "larsen", "larsen and toubro"]},
    {"symbol": "TATAMOTORS.NS", "name": "Tata Motors Limited", "exchange": "NSE", "aliases": ["tata motors", "tamo", "tatamotor"]},
    {"symbol": "TATASTEEL.NS", "name": "Tata Steel Limited", "exchange": "NSE", "aliases": ["tata steel", "tatasteel"]},
    {"symbol": "TATAPOWER.NS", "name": "Tata Power Company", "exchange": "NSE", "aliases": ["tata power", "tatapower"]},
    {"symbol": "MARUTI.NS", "name": "Maruti Suzuki India Limited", "exchange": "NSE", "aliases": ["maruti", "maruti suzuki", "suzuki"]},
    {"symbol": "M&M.NS", "name": "Mahindra & Mahindra Limited", "exchange": "NSE", "aliases": ["mahindra", "m&m", "mahindra and mahindra"]},
    {"symbol": "ADANIENT.NS", "name": "Adani Enterprises Limited", "exchange": "NSE", "aliases": ["adani enterprises", "adani ent"]},
    {"symbol": "ADANIPORTS.NS", "name": "Adani Ports and SEZ", "exchange": "NSE", "aliases": ["adani ports", "adani port"]},
    {"symbol": "ADANIPOWER.NS", "name": "Adani Power Limited", "exchange": "NSE", "aliases": ["adani power"]},
    {"symbol": "ADANIGREEN.NS", "name": "Adani Green Energy", "exchange": "NSE", "aliases": ["adani green"]},
    {"symbol": "SUNPHARMA.NS", "name": "Sun Pharmaceutical Industries", "exchange": "NSE", "aliases": ["sun pharma", "sun pharmaceutical"]},
    {"symbol": "HINDALCO.NS", "name": "Hindalco Industries Limited", "exchange": "NSE", "aliases": ["hindalco"]},
    {"symbol": "TITAN.NS", "name": "Titan Company Limited", "exchange": "NSE", "aliases": ["titan", "tanishq"]},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance Limited", "exchange": "NSE", "aliases": ["bajaj finance"]},
    {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv Limited", "exchange": "NSE", "aliases": ["bajaj finserv"]},
    {"symbol": "WIPRO.NS", "name": "Wipro Limited", "exchange": "NSE", "aliases": ["wipro"]},
    {"symbol": "HCLTECH.NS", "name": "HCL Technologies Limited", "exchange": "NSE", "aliases": ["hcl", "hcl tech"]},
    {"symbol": "NTPC.NS", "name": "NTPC Limited", "exchange": "NSE", "aliases": ["ntpc", "national thermal power"]},
    {"symbol": "ONGC.NS", "name": "Oil & Natural Gas Corporation", "exchange": "NSE", "aliases": ["ongc"]},
    {"symbol": "COALINDIA.NS", "name": "Coal India Limited", "exchange": "NSE", "aliases": ["coal india", "cil"]},
    {"symbol": "POWERGRID.NS", "name": "Power Grid Corporation of India", "exchange": "NSE", "aliases": ["power grid", "powergrid"]},
    {"symbol": "ZOMATO.NS", "name": "Zomato Limited", "exchange": "NSE", "aliases": ["zomato", "blinkit"]},
    {"symbol": "JIOFIN.NS", "name": "Jio Financial Services", "exchange": "NSE", "aliases": ["jio financial", "jiofin"]},
    {"symbol": "HAL.NS", "name": "Hindustan Aeronautics Limited", "exchange": "NSE", "aliases": ["hal", "hindustan aeronautics", "defence"]},
    {"symbol": "BEL.NS", "name": "Bharat Electronics Limited", "exchange": "NSE", "aliases": ["bel", "bharat electronics"]},
    {"symbol": "BHEL.NS", "name": "Bharat Heavy Electricals Limited", "exchange": "NSE", "aliases": ["bhel"]},
    {"symbol": "NHPC.NS", "name": "NHPC Limited", "exchange": "NSE", "aliases": ["nhpc", "hydro power"]},
    {"symbol": "SJVN.NS", "name": "SJVN Limited", "exchange": "NSE", "aliases": ["sjvn"]},
    {"symbol": "SUZLON.NS", "name": "Suzlon Energy Limited", "exchange": "NSE", "aliases": ["suzlon", "wind energy"]},
    {"symbol": "PNB.NS", "name": "Punjab National Bank", "exchange": "NSE", "aliases": ["pnb", "punjab national bank"]},
    {"symbol": "BANKBARODA.NS", "name": "Bank of Baroda", "exchange": "NSE", "aliases": ["bank of baroda", "bob"]},
    {"symbol": "YESBANK.NS", "name": "Yes Bank Limited", "exchange": "NSE", "aliases": ["yes bank", "yesbank"]},
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "exchange": "NSE", "aliases": ["kotak", "kotak bank"]},
    {"symbol": "AXISBANK.NS", "name": "Axis Bank Limited", "exchange": "NSE", "aliases": ["axis", "axis bank"]},
    {"symbol": "VEDL.NS", "name": "Vedanta Limited", "exchange": "NSE", "aliases": ["vedanta", "vedl"]},
    {"symbol": "VBL.NS", "name": "Varun Beverages Limited", "exchange": "NSE", "aliases": ["varun beverages", "vbl", "pepsi"]},
    {"symbol": "ASIANPAINT.NS", "name": "Asian Paints Limited", "exchange": "NSE", "aliases": ["asian paints", "asian paint"]},
    {"symbol": "NESTLEIND.NS", "name": "Nestle India Limited", "exchange": "NSE", "aliases": ["nestle", "maggi"]},
    {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement Limited", "exchange": "NSE", "aliases": ["ultratech", "cement"]},

    # Popular US Stocks
    {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "aliases": ["apple", "iphone", "mac"]},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ", "aliases": ["microsoft", "windows", "azure"]},
    {"symbol": "GOOGL", "name": "Alphabet Inc. (Google)", "exchange": "NASDAQ", "aliases": ["google", "alphabet", "youtube"]},
    {"symbol": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ", "aliases": ["amazon", "aws"]},
    {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ", "aliases": ["tesla", "elon musk"]},
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ", "aliases": ["nvidia", "ai chip"]},
    {"symbol": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ", "aliases": ["meta", "facebook", "instagram"]},
    {"symbol": "NFLX", "name": "Netflix Inc.", "exchange": "NASDAQ", "aliases": ["netflix"]}
]

def search_tickers_by_name(query: str) -> list[dict]:
    """
    Search for stock tickers matching a user's natural query (company name, alias, or ticker symbol).
    Combines curated instant-match recommendations with Yahoo Finance autocomplete API.
    Returns a list of dicts: [{'symbol': 'RVNL.NS', 'name': 'Rail Vikas Nigam Limited', 'exchange': 'NSE', 'label': '...'}]
    """
    query_clean = query.strip()
    if not query_clean:
        return []

    q_lower = query_clean.lower()
    results = []
    seen_symbols = set()

    # 1. First priority: Check local curated catalog for exact / alias matches
    for s in POPULAR_STOCKS:
        matched = False
        if q_lower in s["name"].lower() or q_lower in s["symbol"].lower():
            matched = True
        elif any(q_lower in a or a in q_lower for a in s.get("aliases", [])):
            matched = True
        
        if matched and s["symbol"] not in seen_symbols:
            seen_symbols.add(s["symbol"])
            results.append({
                "symbol": s["symbol"],
                "name": s["name"],
                "exchange": s["exchange"],
                "type": "EQUITY",
                "label": f"{s['name']} ({s['symbol']}) - {s['exchange']}"
            })

    # 2. Second priority: Query Yahoo Finance search API for broad coverage
    try:
        url = "https://query2.finance.yahoo.com/v1/finance/search"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        params = {"q": query_clean, "quotesCount": 10, "newsCount": 0}
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            quotes = data.get("quotes", [])
            for q in quotes:
                quote_type = q.get("quoteType", "")
                sym = q.get("symbol")
                if quote_type in ["EQUITY", "ETF", "INDEX"] and sym and sym not in seen_symbols:
                    name = q.get("shortname") or q.get("longname") or sym
                    exchange = q.get("exchange", "N/A")
                    seen_symbols.add(sym)
                    results.append({
                        "symbol": sym,
                        "name": name,
                        "exchange": exchange,
                        "type": quote_type,
                        "label": f"{name} ({sym}) - {exchange}"
                    })
    except Exception:
        pass

    return results

@st.cache_data(ttl=600)
def get_market_news() -> list[dict]:
    """
    Fetch the latest market news headlines from top market leaders.
    Supports both modern and legacy yfinance response structures.
    """
    news_items = []
    seen_titles = set()
    # Market drivers for fresh financial news
    leader_tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]
    
    for ticker_sym in leader_tickers:
        try:
            raw = yf.Ticker(ticker_sym).news
            if raw:
                for item in raw:
                    # Check new yfinance structure
                    content = item.get("content", {})
                    if content:
                        title = content.get("title")
                        pub = content.get("provider", {}).get("displayName", "Financial News")
                        url = (content.get("canonicalUrl") or {}).get("url") or (content.get("clickThroughUrl") or {}).get("url") or "#"
                    else:
                        title = item.get("title")
                        pub = item.get("publisher", "Financial News")
                        url = item.get("link", "#")
                        
                    if title and title not in seen_titles:
                        seen_titles.add(title)
                        news_items.append({
                            "title": title,
                            "publisher": pub,
                            "link": url
                        })
                    if len(news_items) >= 5:
                        return news_items
        except Exception:
            continue
            
    return news_items

@st.cache_data(ttl=600)
def get_sector_performance() -> list[dict]:
    """
    Fetch live sector performance data for major sectors on NSE.
    """
    sectors = {
        "Nifty IT": "^CNXIT",
        "Nifty Auto": "^CNXAUTO",
        "Nifty Bank": "^NSEBANK",
        "Nifty FMCG": "^CNXFMCG",
        "Nifty Pharma": "^CNXPHARMA",
        "Nifty Metal": "^CNXMETAL"
    }
    performance = []
    for name, ticker_symbol in sectors.items():
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="5d")
            if not hist.empty and len(hist) >= 2:
                latest_close = hist["Close"].iloc[-1]
                prev_close = hist["Close"].iloc[-2]
                pct_change = ((latest_close - prev_close) / prev_close) * 100
                performance.append({
                    "name": name,
                    "pct_change": pct_change
                })
            else:
                performance.append({"name": name, "pct_change": 0.0})
        except Exception:
            performance.append({"name": name, "pct_change": 0.0})
    return performance

@st.cache_data(ttl=600)
def get_top_gainers_losers(market: str = "IN") -> tuple[list[dict], list[dict]]:
    """
    Get top 5 gainers and top 5 losers for the selected market.
    Uses per-ticker individual downloads so one failure doesn't break the rest.
    """
    if market == "IN":
        tickers = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
            "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "LT.NS",
            "HINDALCO.NS", "MARUTI.NS", "NTPC.NS", "ADANIPORTS.NS",
            "TITAN.NS", "BAJFINANCE.NS", "WIPRO.NS", "NESTLEIND.NS",
            "AXISBANK.NS", "KOTAKBANK.NS", "SUNPHARMA.NS"
        ]
    else:
        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX", "AMD", "QCOM", "JPM", "V"]

    changes = []
    for t in tickers:
        try:
            hist = yf.download(t, period="5d", progress=False, auto_adjust=True)
            if hist.empty or len(hist) < 2:
                continue
            # Flatten MultiIndex columns if present
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)
            hist = hist.dropna(subset=["Close"])
            if len(hist) < 2:
                continue
            latest_close = float(hist["Close"].iloc[-1])
            prev_close = float(hist["Close"].iloc[-2])
            if prev_close == 0:
                continue
            price_change = latest_close - prev_close
            pct_change = (price_change / prev_close) * 100
            changes.append({
                "symbol": t.replace(".NS", "").replace(".BO", ""),
                "full_symbol": t,
                "price": latest_close,
                "change": price_change,
                "pct_change": pct_change
            })
        except Exception:
            continue  # Skip silently — one bad ticker shouldn't break the list

    if not changes:
        return [], []

    changes_sorted = sorted(changes, key=lambda x: x["pct_change"], reverse=True)
    gainers = changes_sorted[:5]
    losers = sorted(changes, key=lambda x: x["pct_change"])[:5]
    return gainers, losers


