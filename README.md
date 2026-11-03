📈 StockPulse

StockPulse is a Python-based Stock Market Analysis Dashboard that enables users to analyze historical stock market data, visualize trends, and gain insights using interactive charts and technical indicators. The project is built with Python and Streamlit, making it easy to explore stock performance through a simple web interface.

🚀 Features
Search stocks by ticker symbol
View historical stock price data
Interactive stock price charts
Moving Average Analysis
Daily Returns Calculation
Volume Analysis
Compare multiple stocks
Portfolio Management (Planned)
Watchlist (Planned)
User Authentication (Planned)
PostgreSQL Database Integration (Planned)
Cloud Deployment (Planned)


🛠️ Tech Stack
Frontend
Streamlit

Backend
Python

Data Analysis
Pandas
NumPy

Data Visualization
Plotly
Matplotlib
Stock Data
yfinance
Database (Upcoming)
PostgreSQL
SQLAlchemy
Version Control
Git
GitHub



Here's the complete README content. Copy and paste this into `StockPulse/README.md`:

---

# 📈 StockPulse

## Overview

**StockPulse** is a premium, modern web application for stock market analysis, visualization, and personal portfolio tracking. It is built using **Python** and **Streamlit**, providing a smooth, interactive, and beautiful dark-themed (glassmorphism) interface for exploring real-time and historical stock data.

The application pulls live market data from **Yahoo Finance** using the `yfinance` library, computes powerful technical indicators, and displays everything through interactive charts built with **Plotly**. It also supports user accounts, watchlists, and a full buy/sell portfolio tracker backed by a local **SQLite** database (with optional PostgreSQL support).

---

## 🚀 Features

### 1. Smart Stock Search & Discovery
- Search companies by **name, alias, or ticker symbol** (e.g., type "Rail nigam", "Reliance", "Tata", "Apple", or "RVNL.NS").
- Uses a **curated local catalog** of 60+ popular Indian and US stocks combined with the **Yahoo Finance search API** for infinite coverage.
- Quick-pick buttons on the dashboard for one-click loading of major stocks.

### 2. Live Market Overview Dashboard
- **Top Indices Overview**: Live prices and changes for S&P 500, Nasdaq, Nifty 50, and BSE Sensex.
- **Nifty 50 Benchmark Chart**: A beautiful area chart tracking the benchmark index over 6 months.
- **Market Breadth & Summary**: Advances, declines, unchanged counts, and a bullish/bearish breadth percentage.
- **Top Gainers & Losers**: Real-time top 5 gainers and losers for the Indian market.
- **Sector Performance**: Live performance of key NSE sectors (IT, Auto, Bank, FMCG, Pharma, Metal).
- **Market Sentiment Gauge**: A speedometer chart showing "Fear", "Greed", "Extreme Fear", or "Extreme Greed" based on index momentum.
- **Treemap Heatmap**: A visual bubble treemap of major stocks sized by market cap and colored by daily % change.
- **Market News & Insights**: Live financial news headlines fetched from Yahoo Finance for top companies.

### 3. Deep Stock Analysis (Detail View)
When you click on any stock, you get a full detail page with:
- **Current price, market cap, P/E ratio, 52-week high/low** displayed in custom metric cards.
- **Interactive Candlestick Chart** with optional overlays for **Simple Moving Average (SMA)** and **Exponential Moving Average (EMA)** across multiple periods (9, 20, 21, 50, 100, 200).
- **Volume Chart**: Color-coded bars showing buying/selling pressure per day.
- **RSI (Relative Strength Index) Chart**: With overbought (70) and oversold (30) guide lines.
- **MACD & Signal Divergence Chart**: With a color-coded histogram showing bullish/bearish momentum.
- **Company Profile Card**: Sector, industry, website, and a full business summary.
- **Automated Technical Analysis Report**: A downloadable Markdown report summarizing the stock's financials, RSI status, moving average trend posture, and overall technical health.

### 4. Stock Comparison Engine
- Compare up to **5 stocks side-by-side**.
- **Normalized Performance Chart**: Tracks cumulative % return from the start of the chosen period so you can see which stock performed best.
- **Key Metrics Table**: Side-by-side comparison of current price, market cap, P/E ratio, dividend yield, 52-week range, and sector.
- **Correlation Matrix Heatmap**: A visual correlation matrix showing how the daily returns of selected stocks move relative to one another (values near 1.0 = move together; near 0 = independent).

### 5. Personal Watchlist
- Save stocks to your personal watchlist (requires free account).
- View live prices, daily changes, and a **mini sparkline chart** for each tracked stock.
- One-click add/remove from the dashboard or the dedicated Watchlist page.

### 6. Portfolio Management
- Log **BUY** and **SELL** transactions with shares quantity and price.
- Automatic portfolio calculations:
  - **Total Invested Amount**
  - **Current Market Value** (using live prices)
  - **Total Profit/Loss (P&L)** in ₹ and %
- **Holdings Table**: Shows shares held, average cost basis, current value, P&L, and portfolio allocation %.
- **Asset Allocation Pie Chart**: Visual breakdown of your portfolio by stock symbol.
- **Sector Allocation Pie Chart**: Visual breakdown by market sector.
- **Transaction Audit Log**: Complete history of all logged transactions.

### 7. Historical Data Explorer
- Search any stock and view its full historical price table (Open, High, Low, Close, Adjusted Close, Volume).
- **Export to CSV**: Download historical data for any timeframe.
- **Daily Returns & Volatility Analytics**: Statistics including average daily return, standard deviation (volatility), max daily gain, and max daily loss, plus a histogram showing the distribution of daily returns.

### 8. User Authentication & Accounts
- **Secure local registration and login**.
- Passwords are hashed using **PBKDF2-HMAC-SHA256** with a unique cryptographically random salt per user (100,000 iterations).
- Session state manages login status across all pages.

---

## 🛠️ Tech Stack & Technologies Used (Simple Explanation)

Here is a breakdown of every technology used in this project and what it does:

### Frontend / UI Framework
- **Streamlit**: The main framework. It lets us turn Python scripts into beautiful web applications without writing any HTML, CSS, or JavaScript. It handles the web server, page routing, and widgets (buttons, text inputs, dropdowns, etc.).

### Data Analysis & Manipulation
- **Pandas**: Used everywhere for handling tabular data (stock price histories, financial metrics, correlation matrices). It makes it easy to load, clean, filter, and analyze data frames.
- **NumPy**: Used under the hood by Pandas and our custom indicator calculations for fast numerical operations on arrays of prices.

### Data Visualization
- **Plotly**: The primary charting library. We use it to generate:
  - **Candlestick charts** (the classic red/green stock price bars).
  - **Line charts** (moving averages, cumulative returns).
  - **Bar charts** (trading volume, MACD histograms).
  - **Pie charts** (portfolio asset and sector allocation).
  - **Histograms** (daily returns distribution).
  - **Treemaps** (market heatmap).
  - **Gauge charts** (market sentiment speedometer).
  - **Sparklines** (tiny mini-charts on the watchlist).
- **Matplotlib**: Listed as a dependency (used by some libraries), though Plotly is our main visual engine.

### Stock Data Source
- **yfinance**: The core library that fetches all stock data from Yahoo Finance. It downloads:
  - Historical price data (Open, High, Low, Close, Volume, Adjusted Close).
  - Company profile metadata (name, sector, industry, market cap, P/E ratio, 52-week high/low, dividend yield, website, business summary).
  - Live market news headlines.
  - Market index data (S&P 500, Nasdaq, Nifty 50, Sensex, and sector indices).
- **Requests**: Used to call the Yahoo Finance search API directly for company name autocomplete/search suggestions.

### Database & Backend Storage
- **SQLite (via SQLAlchemy)**: The default local database engine. It stores all user accounts, watchlist items, and portfolio transactions in a single file called `stockpulse.db`. It requires no separate database server to run — everything is self-contained.
- **SQLAlchemy**: A Python **Object-Relational Mapper (ORM)**. Instead of writing raw SQL queries, we define Python classes (like `User`, `Watchlist`, `PortfolioTransaction`) that map to database tables. This makes database operations safe, fast, and easy to read.
- **PostgreSQL (Optional)**: The application supports switching to a cloud PostgreSQL database (like Neon or Supabase) by setting a `DATABASE_URL` environment variable. This is useful for cloud deployment or multi-user concurrent access.

### Environment Configuration
- **python-dotenv**: Loads environment variables (like database URLs or API keys) from a `.env` file into the application automatically.

### Security
- **hashlib & secrets**: Used in the authentication module to securely hash passwords using **PBKDF2-HMAC-SHA256** with unique random salts, ensuring user passwords are never stored in plain text.

---

## 📂 Project Structure (File by File Explanation)

Here is exactly what each file does:

```
StockPulse/
│
├── app.py                    # The main entry point. Redirects the root URL to the Dashboard page.
├── config.py                 # Central configuration: app title, theme colors, fonts, default indices, database path, indicator defaults.
├── requirements.txt          # List of all Python packages required to run the app.
├── stockpulse.db             # The local SQLite database file (auto-created on first run).
├── .env                      # Your local environment variables (database URL, etc.). Keep this private!
├── .env.example              # A template showing what variables can be set.
├── .gitignore                # Ignores the .env file and database from version control.
├── README.md                 # This file.
│
├── assets/                   # Static assets folder.
│   ├── logo.png              # Application logo (currently a placeholder).
│   └── styles.css            # Custom CSS overrides (not heavily used since CSS is injected dynamically).
│
├── src/                      # Core backend Python modules (the "engine" of the app).
│   ├── __init__.py           # Makes the folder a Python package.
│   ├── database.py           # Sets up the SQLAlchemy database engine, session factory, and a helper to initialize tables.
│   ├── models.py             # Defines the database table schemas: User, Watchlist, and PortfolioTransaction.
│   ├── auth.py               # Handles user registration, login, logout, password hashing, and session state management.
│   ├── stock_api.py          # All data-fetching functions: get stock history, company info, market summary, news, gainers/losers, sector performance, and stock search.
│   ├── indicators.py         # Mathematical calculations for technical indicators: SMA, EMA, RSI, MACD, daily returns, and cumulative returns.
│   ├── charts.py             # Generates all Plotly figures: candlesticks, volume, RSI, MACD, comparison charts, sparklines, area charts, sentiment gauges, and treemaps.
│   ├── analysis.py           # High-level analysis: generates comparison tables and calculates correlation matrices between stocks.
│   ├── portfolio.py          # Handles portfolio logic: logging buy/sell transactions, calculating holdings, total value, P&L, and cost basis.
│   ├── watchlist.py          # Handles watchlist logic: adding, removing, and checking if stocks are tracked.
│   ├── reports.py            # Generates downloadable Markdown technical analysis reports for any stock.
│   └── utils.py              # Shared UI helpers: injects custom CSS for the dark glassmorphism theme, renders the top navigation bar, metric cards, and the stock search bar.
│
└── pages/                    # Streamlit multi-page application pages (each file is a page).
    ├── Dashboard.py          # The main landing page. Shows market overview, stock search, detail view, indices, gainers/losers, news, and watchlist summary.
    ├── Compare.py            # The stock comparison engine page with performance charts, metrics tables, and correlation heatmaps.
    ├── Watchlist.py          # The personal watchlist management page (add, view, remove stocks).
    ├── Portfolio.py          # The portfolio tracker page (log transactions, view holdings, P&L, allocation charts, and transaction history).
    ├── History.py            # The historical data explorer page (view price tables, export CSV, and daily returns/volatility stats).
    └── Profile.py            # The user account page (login, register, view profile, logout).
```

---

## 🎨 UI / UX Design Details

- **Theme**: Premium **Dark Glassmorphism**. Semi-transparent cards with a `backdrop-filter: blur` effect, subtle neon purple (#8a2be2) and cyan (#00f5d4) gradients, and dark charcoal backgrounds.
- **Typography**: Uses the **Outfit** font for headings and titles (bold, modern) and **Inter** for body text and secondary labels (clean, highly readable).
- **Color Coding**:
  - **Green (#00e676)**: Up days, bullish indicators, gains.
  - **Red/Pink (#ff3366)**: Down days, bearish indicators, losses.
  - **Purple & Cyan**: Accents, active navigation states, and logo branding.
- **Layout**: Fully responsive wide-grid layout using Streamlit columns. A custom top navigation bar replaces the default Streamlit sidebar for a clean, app-like feel.

---

## 📥 How to Run This Project

### Prerequisites
- **Python 3.10 or higher** installed on your machine.
- **pip** (Python's package manager).

### Step-by-Step Instructions

1. **Open a terminal** (Command Prompt, PowerShell, or any terminal) and navigate to the project directory:
   ```bash
   cd D:\1_Study\Minor-Project\StockPulse
   ```

2. **Install the required Python packages** from the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```
   This will install Streamlit, Pandas, Plotly, yfinance, SQLAlchemy, and all other dependencies.

3. **Run the Streamlit application**:
   ```bash
   streamlit run app.py
   ```

4. **Open your web browser** and go to the URL that Streamlit prints (usually `http://localhost:8501`).

The application is now running locally and ready to use. No internet setup or cloud keys are required for basic use (it will use the local SQLite database automatically).

---

## 🚢 Optional: Cloud Deployment & PostgreSQL

The application is designed to be highly portable. If you want to run it on a server or deploy it publicly:

1. Set a `DATABASE_URL` environment variable pointing to a cloud PostgreSQL database (e.g., from **Neon**, **Supabase**, or **AWS RDS**).
2. The application will automatically detect the `DATABASE_URL` and use PostgreSQL instead of SQLite.
3. You can containerize the app using Docker and deploy it on platforms like **Render**, **Railway**, **AWS ECS**, or **Google Cloud Run**.

---

## Disclaimer

*StockPulse is built for educational and informational purposes only. The stock market data, news, and financial metrics are fetched from Yahoo Finance and third-party APIs. The technical indicators and automated reports generated by this application do not constitute financial advice. Always do your own research (DYOR) before making any investment decisions.*


Detailed breakdown of every technology and API used in StockPulse:

---

## Core Framework

### Streamlit
- **What it is**: A Python framework that turns scripts into web apps.
- **What it does here**: Handles the entire web UI — page routing (multi-page app via the `pages/` folder), widgets (buttons, text inputs, dropdowns), the web server, and session state management. You write Python, and Streamlit renders it in the browser.

---

## Data Analysis & Manipulation

### Pandas
- **What it is**: The standard Python library for tabular data.
- **What it does here**: Loads, cleans, filters, and manipulates stock price histories (DataFrames). Used to calculate daily returns, align dates, handle missing data, merge multiple stock histories for correlation matrices, and format tables for display.

### NumPy
- **What it is**: A library for fast numerical computing with arrays.
- **What it does here**: Powers Pandas under the hood and is used directly in mathematical operations for technical indicators (rolling averages, exponential smoothing, clipping gains/losses for RSI).

---

## Data Visualization

### Plotly
- **What it is**: An interactive charting library.
- **What it does here**: Generates every chart in the app:
  - **Candlestick charts** (stock price bars)
  - **Line charts** (moving averages, cumulative returns)
  - **Bar charts** (volume, MACD histogram)
  - **Pie charts** (portfolio allocation)
  - **Histograms** (daily returns distribution)
  - **Treemaps** (market heatmap)
  - **Gauge charts** (sentiment speedometer)
  - **Sparklines** (mini trend lines on watchlist)

### Matplotlib
- **What it is**: A lower-level plotting library.
- **What it does here**: Listed as a dependency; Plotly can optionally use it for some backend rendering, but it's not directly called in this codebase.

---

## Stock Data API

### yfinance
- **What it is**: A Python library that wraps the **Yahoo Finance** public APIs.
- **What it does here**: This is the primary data source. It fetches:
  - **Historical price data** (Open, High, Low, Close, Volume, Adjusted Close) for any ticker over custom timeframes (1 month to max history).
  - **Company profile metadata** — name, sector, industry, market cap, P/E ratio, dividend yield, 52-week high/low, current price, website, and business summary.
  - **Market index data** — S&P 500 (^GSPC), Nasdaq (^IXIC), Nifty 50 (^NSEI), BSE Sensex (^BSESN), and sector indices (Nifty IT, Auto, Bank, etc.).
  - **Market news headlines** — recent news articles for major stocks (Reliance, TCS, Infosys, HDFC Bank).

### Requests
- **What it is**: A simple HTTP library for making web requests.
- **What it does here**: Directly calls the **Yahoo Finance Search API** (`https://query2.finance.yahoo.com/v1/finance/search`) to power the company name autocomplete — letting users type "Rail nigam" and find "RVNL.NS" without knowing the ticker.

---

## Database & Backend

### SQLAlchemy
- **What it is**: A Python **Object-Relational Mapper (ORM)**.
- **What it does here**: Maps Python classes to database tables. Instead of writing raw SQL, you define classes like `User`, `Watchlist`, and `PortfolioTransaction`, and SQLAlchemy handles the queries, relationships, and table creation automatically.

### SQLite
- **What it is**: A serverless, file-based database engine.
- **What it does here**: The default database. Stores all user accounts, watchlist entries, and portfolio buy/sell transactions in a single file (`stockpulse.db`). No database server needs to be installed or running — it just works out of the box.

### PostgreSQL (Optional)
- **What it is**: A powerful, server-based relational database.
- **What it does here**: Supported as an alternative. If you set a `DATABASE_URL` environment variable (e.g., from **Neon**, **Supabase**, or **AWS RDS**), the app switches from SQLite to PostgreSQL for cloud deployment or multi-user access.

---

## Environment Configuration

### python-dotenv
- **What it is**: A library that loads environment variables from a `.env` file.
- **What it does here**: Reads the `.env` file at startup and loads settings like `DATABASE_URL` into the application's configuration, so you don't have to set system environment variables manually.

---

## Security

### hashlib (PBKDF2-HMAC-SHA256)
- **What it is**: Python's built-in cryptographic hashing library.
- **What it does here**: Passwords are never stored in plain text. Each user gets a unique random **salt** (via the `secrets` module), and their password is hashed using **PBKDF2 with HMAC-SHA256** over **100,000 iterations**. This is a secure, industry-standard way to protect user passwords.

### secrets
- **What it is**: Python's built-in library for cryptographically secure random numbers.
- **What it does here**: Generates a unique 16-byte random salt for each user during registration, ensuring that even if two users have the same password, their stored hashes are completely different.

---

## Summary Table

| Technology / API | Category | What It Does |
|---|---|---|
| **Streamlit** | Web Framework | Builds the web UI, pages, widgets, and routing |
| **Pandas** | Data Analysis | Manipulates stock price data, calculates returns |
| **NumPy** | Numerical Computing | Powers fast math for indicators |
| **Plotly** | Data Visualization | Generates all interactive charts |
| **Matplotlib** | Visualization | Backup renderer (dependency only) |
| **yfinance** | Stock Data API | Fetches prices, company info, indices, and news from Yahoo Finance |
| **Requests** | HTTP Library | Calls Yahoo Finance search API for company name search |
| **SQLAlchemy** | Database ORM | Maps Python objects to database tables |
| **SQLite** | Database | Local file-based storage for users, watchlists, portfolios |
| **PostgreSQL** | Database (Optional) | Cloud database alternative via `DATABASE_URL` |
| **python-dotenv** | Config | Loads `.env` file for environment variables |
| **hashlib** | Security | Hashes passwords with PBKDF2-HMAC-SHA256 |
| **secrets** | Security | Generates cryptographically random salts |