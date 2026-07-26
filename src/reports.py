from datetime import datetime
import pandas as pd
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.indicators import calculate_rsi, calculate_sma

def generate_markdown_report(symbol: str, info: dict, df: pd.DataFrame) -> str:
    """
    Generate a markdown formatted report summarizing stock details and technical metrics.
    """
    symbol = symbol.upper()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Extract indicators
    rsi = calculate_rsi(df).iloc[-1] if not df.empty else None
    sma_50 = calculate_sma(df, 50).iloc[-1] if not df.empty and len(df) >= 50 else None
    sma_200 = calculate_sma(df, 200).iloc[-1] if not df.empty and len(df) >= 200 else None
    
    current_price = info.get("current_price", df["Close"].iloc[-1] if not df.empty else 0.0)
    
    # Assess technical posture
    rsi_status = "Neutral"
    if rsi:
        if rsi >= 70:
            rsi_status = "🔴 Overbought (Possible pullback risk)"
        elif rsi <= 30:
            rsi_status = "🟢 Oversold (Possible bounce opportunity)"
        else:
            rsi_status = "⚪ Neutral"
            
    trend_status = "Neutral"
    if sma_50 and sma_200:
        if current_price > sma_50 > sma_200:
            trend_status = "🚀 Strong Bullish (Price is above 50-day and 200-day SMAs)"
        elif current_price < sma_50 < sma_200:
            trend_status = "📉 Strong Bearish (Price is below 50-day and 200-day SMAs)"
        elif current_price > sma_50:
            trend_status = "🟡 Moderately Bullish (Price is above 50-day SMA)"
        else:
            trend_status = "🟡 Moderately Bearish (Price is below 50-day SMA)"

    report = f"""# StockPulse analysis Report: {symbol}
**Generated on:** {now_str}
**Company Name:** {info.get("name", symbol)}
**Sector / Industry:** {info.get("sector", "N/A")} / {info.get("industry", "N/A")}

---

## 📈 Financial Overview
- **Current Trading Price:** {info.get("currency", "USD")} {current_price:.2f}
- **Market Capitalization:** {info.get("market_cap", 0.0):,}
- **Price-to-Earnings (P/E) Ratio:** {info.get("pe_ratio") if info.get("pe_ratio") is not None else "N/A"}
- **Dividend Yield:** {info.get("dividend_yield", 0.0) * 100:.2f}%
- **52-Week Range:** ${info.get("fifty_two_week_low", 0.0):.2f} - ${info.get("fifty_two_week_high", 0.0):.2f}

---

## 🛠️ Technical Indicator Summary
- **Relative Strength Index (RSI - 14):** {f"{rsi:.2f}" if rsi else "N/A"} -> **{rsi_status}**
- **50-Day Simple Moving Average (SMA):** {f"${sma_50:.2f}" if sma_50 else "N/A"}
- **200-Day Simple Moving Average (SMA):** {f"${sma_200:.2f}" if sma_200 else "N/A"}
- **Overall Trend Posture:** {trend_status}

---

## 🏢 Business Description
{info.get("summary", "No description available.")}

---
*Disclaimer: This report was generated automatically by StockPulse using Yahoo Finance data for informational purposes only. It does not constitute financial advice.*
"""
    return report
