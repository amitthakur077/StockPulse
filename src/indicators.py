import pandas as pd
import numpy as np

def calculate_sma(df: pd.DataFrame, period: int) -> pd.Series:
    """
    Calculate the Simple Moving Average (SMA) for a given period.
    """
    if "Close" not in df.columns or len(df) < period:
        return pd.Series(index=df.index, dtype="float64")
    return df["Close"].rolling(window=period).mean()

def calculate_ema(df: pd.DataFrame, period: int) -> pd.Series:
    """
    Calculate the Exponential Moving Average (EMA) for a given period.
    """
    if "Close" not in df.columns or len(df) < period:
        return pd.Series(index=df.index, dtype="float64")
    return df["Close"].ewm(span=period, adjust=False).mean()

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate the Relative Strength Index (RSI) for a given period.
    """
    if "Close" not in df.columns or len(df) <= period:
        return pd.Series(index=df.index, dtype="float64")
    
    close_delta = df["Close"].diff()
    
    # Make two series: one for gain and one for loss
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    
    # Calculate exponential moving average of gains and losses
    ma_up = up.ewm(com=period - 1, adjust=False).mean()
    ma_down = down.ewm(com=period - 1, adjust=False).mean()
    
    # Calculate RS
    rs = ma_up / ma_down
    
    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate MACD, Signal Line, and MACD Histogram.
    """
    empty_series = pd.Series(index=df.index, dtype="float64")
    if "Close" not in df.columns or len(df) < slow:
        return empty_series, empty_series, empty_series
        
    ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    macd_hist = macd_line - signal_line
    
    return macd_line, signal_line, macd_hist

def calculate_daily_returns(df: pd.DataFrame) -> pd.Series:
    """
    Calculate the Daily Percentage Returns.
    """
    if "Close" not in df.columns or df.empty:
        return pd.Series(index=df.index, dtype="float64")
    return df["Close"].pct_change() * 100

def calculate_cumulative_returns(df: pd.DataFrame) -> pd.Series:
    """
    Calculate Cumulative Percentage Returns over the period.
    """
    if "Close" not in df.columns or df.empty:
        return pd.Series(index=df.index, dtype="float64")
    
    daily_pct = df["Close"].pct_change()
    # Cumulate return: (1 + r1)*(1 + r2)*... - 1
    cum_returns = (1 + daily_pct.fillna(0) / 100).cumprod() - 1
    return cum_returns * 100
