import os

# Application Settings
APP_TITLE = "📈 StockPulse"
APP_SUBTITLE = "Premium Stock Market Analysis Dashboard"

# Directory configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database Settings
# Defaulting to a local, serverless SQLite database (100% free)
# Can easily be changed to a PostgreSQL connection URI here
DB_PATH = os.path.join(BASE_DIR, "stockpulse.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# Supported Default Indices for market overview
DEFAULT_INDICES = {
    "^GSPC": "S&P 500",
    "^DJI": "Dow Jones",
    "^IXIC": "Nasdaq",
    "^NSEI": "Nifty 50"
}

# Default Watchlist tickers for new users
DEFAULT_WATCHLIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

# Technical Indicator Defaults
INDICATOR_DEFAULTS = {
    "sma_periods": [20, 50, 100, 200],
    "ema_periods": [9, 21, 50, 100],
    "rsi_period": 14,
    "macd": {
        "fast": 12,
        "slow": 26,
        "signal": 9
    }
}

# Premium Dark Glassmorphism Styling Color Palette
THEME_COLORS = {
    "bg_color": "#0e1117",         # Streamlit dark background
    "card_bg": "rgba(28, 30, 42, 0.7)", # Transparent dark card background
    "border_color": "rgba(255, 255, 255, 0.1)",
    "primary": "#8a2be2",          # Neon Purple
    "secondary": "#00f5d4",        # Cyan / Neon Mint
    "success": "#00e676",          # Vibrant Emerald (Up/Bullish)
    "danger": "#ff3366",           # Neon Pink/Red (Down/Bearish)
    "warning": "#ffb703",          # Amber/Orange
    "info": "#1e90ff",             # Dodger Blue
    "text_primary": "#ffffff",
    "text_secondary": "#a0aab2",
    "grid_color": "#1f2937"        # Dark charcoal grid lines
}

# Google Font selection for UI
UI_FONTS = "Outfit, Inter, system-ui, -apple-system, sans-serif"
