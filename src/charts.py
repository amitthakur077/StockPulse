import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config
from src.indicators import calculate_rsi, calculate_macd

# Extract default theme colors
COLORS = config.THEME_COLORS

def _apply_dark_layout(fig, title_text, y_title=None, show_legend=True):
    """
    Private helper to apply premium dark theme layouts to all Plotly figures.
    """
    fig.update_layout(
        title={
            'text': title_text,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'color': COLORS["text_primary"], 'family': config.UI_FONTS}
        },
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper
        plot_bgcolor='rgba(15, 18, 25, 0.5)', # Semi-transparent slate plotting area
        font=dict(color=COLORS["text_secondary"], family=config.UI_FONTS),
        xaxis=dict(
            gridcolor=COLORS["grid_color"],
            linecolor=COLORS["grid_color"],
            zeroline=False,
            showgrid=True
        ),
        yaxis=dict(
            title=y_title,
            gridcolor=COLORS["grid_color"],
            linecolor=COLORS["grid_color"],
            zeroline=False,
            showgrid=True
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(0,0,0,0)',
            font=dict(size=11)
        ) if show_legend else dict(visible=False),
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode="x unified"
    )

def plot_candlestick(df: pd.DataFrame, ma_lines: dict = None, title: str = "Price Chart") -> go.Figure:
    """
    Renders an interactive Candlestick chart overlaid with selected Moving Averages.
    """
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="Price",
        increasing_line_color=COLORS["success"],
        decreasing_line_color=COLORS["danger"],
        increasing_fillcolor=COLORS["success"],
        decreasing_fillcolor=COLORS["danger"],
    ))

    # Add Moving Averages
    if ma_lines:
        color_cycle = [COLORS["primary"], COLORS["secondary"], COLORS["info"], COLORS["warning"]]
        for idx, (label, series) in enumerate(ma_lines.items()):
            if not series.empty:
                color = color_cycle[idx % len(color_cycle)]
                fig.add_trace(go.Scatter(
                    x=series.index,
                    y=series,
                    mode='lines',
                    name=label,
                    line=dict(width=1.5, color=color),
                    opacity=0.9
                ))

    # Remove rangeslider for cleaner layout
    fig.update_layout(xaxis_rangeslider_visible=False)
    _apply_dark_layout(fig, title, y_title="Price")
    return fig

def plot_volume(df: pd.DataFrame, title: str = "Volume Traded") -> go.Figure:
    """
    Renders trading volume bars, color-coded by price movement (green/red).
    """
    if df.empty or "Volume" not in df.columns:
        return go.Figure()

    # Color code: green if close >= open, red if close < open
    colors = [COLORS["success"] if close >= open else COLORS["danger"] 
              for open, close in zip(df['Open'], df['Close'])]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        name="Volume",
        marker_color=colors,
        opacity=0.8
    ))

    _apply_dark_layout(fig, title, y_title="Volume", show_legend=False)
    return fig

def plot_rsi(df: pd.DataFrame, period: int = 14) -> go.Figure:
    """
    Renders Relative Strength Index (RSI) with overbought/oversold dashed lines.
    """
    rsi = calculate_rsi(df, period)
    if rsi.empty:
        return go.Figure()

    fig = go.Figure()

    # RSI Line
    fig.add_trace(go.Scatter(
        x=rsi.index,
        y=rsi,
        mode='lines',
        name="RSI",
        line=dict(width=2, color=COLORS["secondary"])
    ))

    # Horizontal guide lines for overbought (70) and oversold (30)
    fig.add_shape(type="line", x0=rsi.index[0], y0=70, x1=rsi.index[-1], y1=70,
                  line=dict(color=COLORS["danger"], width=1, dash="dash"))
    fig.add_shape(type="line", x0=rsi.index[0], y0=30, x1=rsi.index[-1], y1=30,
                  line=dict(color=COLORS["success"], width=1, dash="dash"))

    # Highlight overbought/oversold regions
    fig.update_yaxes(range=[0, 100])
    _apply_dark_layout(fig, f"Relative Strength Index (RSI-{period})", y_title="RSI", show_legend=False)
    return fig

def plot_macd(df: pd.DataFrame) -> go.Figure:
    """
    Renders MACD and Signal line with color-coded divergence histogram.
    """
    macd, signal, hist = calculate_macd(df)
    if macd.empty:
        return go.Figure()

    fig = go.Figure()

    # MACD Line
    fig.add_trace(go.Scatter(
        x=macd.index, y=macd, mode='lines', name="MACD",
        line=dict(width=1.5, color=COLORS["info"])
    ))

    # Signal Line
    fig.add_trace(go.Scatter(
        x=signal.index, y=signal, mode='lines', name="Signal",
        line=dict(width=1.5, color=COLORS["warning"])
    ))

    # Histogram colors based on positive/negative growth
    hist_colors = [COLORS["success"] if val >= 0 else COLORS["danger"] for val in hist]

    # Histogram
    fig.add_trace(go.Bar(
        x=hist.index, y=hist, name="Divergence",
        marker_color=hist_colors, opacity=0.7
    ))

    _apply_dark_layout(fig, "MACD & Signal Divergence", y_title="Value", show_legend=True)
    return fig

def plot_comparison(dfs_dict: dict, title: str = "Relative Cumulative Performance (%)") -> go.Figure:
    """
    Renders normalized returns comparison chart for multiple tickers.
    """
    fig = go.Figure()
    color_palette = [COLORS["secondary"], COLORS["primary"], COLORS["info"], COLORS["warning"], "#ff007f", "#39ff14"]

    for idx, (symbol, df) in enumerate(dfs_dict.items()):
        if df.empty or "Close" not in df.columns:
            continue
        
        # Calculate cumulative returns
        daily_pct = df["Close"].pct_change()
        cum_returns = (1 + daily_pct.fillna(0)).cumprod() - 1
        cum_returns_pct = cum_returns * 100
        
        color = color_palette[idx % len(color_palette)]
        fig.add_trace(go.Scatter(
            x=cum_returns_pct.index,
            y=cum_returns_pct,
            mode='lines',
            name=symbol,
            line=dict(width=2, color=color)
        ))

    _apply_dark_layout(fig, title, y_title="Cumulative Return (%)", show_legend=True)
    return fig

def plot_returns_dist(df: pd.DataFrame, title: str = "Daily Returns Distribution") -> go.Figure:
    """
    Renders a histogram of daily percent changes.
    """
    if df.empty or "Close" not in df.columns:
        return go.Figure()
    
    daily_returns = df["Close"].pct_change().dropna() * 100
    
    fig = px.histogram(
        daily_returns,
        nbins=50,
        labels={'value': 'Daily Return (%)'},
        color_discrete_sequence=[COLORS["primary"]]
    )
    
    _apply_dark_layout(fig, title, y_title="Frequency", show_legend=False)
    fig.update_traces(opacity=0.75, marker_line_color=COLORS["bg_color"], marker_line_width=0.5)
    return fig

def plot_sparkline(df: pd.DataFrame) -> go.Figure:
    """
    Creates a tiny, clean sparkline for watchlist widgets.
    """
    if df.empty or len(df) < 2:
        return go.Figure()
        
    prices = df["Close"].tolist()
    is_up = prices[-1] >= prices[0]
    line_color = COLORS["success"] if is_up else COLORS["danger"]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Close"],
        mode="lines",
        line=dict(color=line_color, width=1.5),
        fill='tozeroy',
        fillcolor=f"rgba(0, 230, 118, 0.05)" if is_up else f"rgba(255, 51, 102, 0.05)",
        hoverinfo="none"
    ))
    
    fig.update_layout(
        xaxis=dict(visible=False, showgrid=False),
        yaxis=dict(visible=False, showgrid=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        height=40,
        width=120
    )
    return fig

def plot_area_chart(df: pd.DataFrame, title: str = "Market Performance") -> go.Figure:
    """
    Renders a premium Area Chart with translucent color gradient filling.
    """
    if df.empty or "Close" not in df.columns:
        return go.Figure()
        
    prices = df["Close"].tolist()
    is_up = prices[-1] >= prices[0]
    line_color = COLORS["success"] if is_up else COLORS["danger"]
    fill_color = "rgba(0, 230, 118, 0.08)" if is_up else "rgba(255, 51, 102, 0.08)"
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Close"],
        mode="lines",
        name="Price",
        line=dict(color=line_color, width=2.5),
        fill='tozeroy',
        fillcolor=fill_color
    ))
    
    _apply_dark_layout(fig, title, y_title="Value", show_legend=False)
    fig.update_layout(
        xaxis=dict(showgrid=True, gridcolor="rgba(255, 255, 255, 0.03)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255, 255, 255, 0.03)")
    )
    return fig

def plot_sentiment_gauge(value: int) -> go.Figure:
    """
    Renders a premium speedometer gauge indicating market sentiment.
    """
    status = "Neutral"
    color = COLORS["warning"]
    if value >= 70:
        status = "Extreme Greed"
        color = COLORS["success"]
    elif value >= 55:
        status = "Greed / Bullish"
        color = COLORS["success"]
    elif value <= 30:
        status = "Extreme Fear"
        color = COLORS["danger"]
    elif value <= 45:
        status = "Fear / Bearish"
        color = COLORS["danger"]
        
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': COLORS["text_secondary"], 'nticks': 5},
            'bar': {'color': color, 'thickness': 0.25},
            'bgcolor': 'rgba(255, 255, 255, 0.02)',
            'borderwidth': 1,
            'bordercolor': COLORS["border_color"],
            'steps': [
                {'range': [0, 30], 'color': 'rgba(255, 51, 102, 0.1)'},
                {'range': [30, 70], 'color': 'rgba(255, 183, 3, 0.1)'},
                {'range': [70, 100], 'color': 'rgba(0, 230, 118, 0.1)'}
            ],
            'threshold': {
                'line': {'color': "#ffffff", 'width': 3},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        title={
            'text': f"Sentiment: <b>{status}</b>",
            'y': 0.15,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 14, 'color': '#ffffff', 'family': config.UI_FONTS}
        },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS["text_primary"], family=config.UI_FONTS),
        height=180,
        margin=dict(l=20, r=20, t=10, b=40)
    )
    return fig

def plot_market_heatmap(df_data: pd.DataFrame) -> go.Figure:
    """
    Renders a custom Plotly treemap representing market performance of major stocks.
    """
    if df_data.empty:
        return go.Figure()
        
    df_data = df_data.copy()
    df_data["label"] = df_data["symbol"] + "<br>" + df_data["pct_change"].apply(lambda x: f"+{x:.2f}%" if x >= 0 else f"{x:.2f}%")
    
    fig = px.treemap(
        df_data,
        path=['label'],
        values='market_cap',
        color='pct_change',
        color_continuous_scale=[
            [0, '#ff3366'],
            [0.5, '#161b26'],
            [1, '#00e676']
        ],
        color_continuous_midpoint=0.0
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#ffffff", family=config.UI_FONTS),
        margin=dict(l=5, r=5, t=5, b=5),
        coloraxis_showscale=False
    )
    
    fig.update_traces(
        textinfo="label",
        hoverinfo="none",
        marker=dict(cornerradius=4)
    )
    return fig

