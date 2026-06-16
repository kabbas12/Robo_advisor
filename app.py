"""
AI Robo-Advisor for FinTech Thesis
With Professional Dashboard, Banking Analytics & Integrated Technical Analysis
Author: Syed Kamran Abbas
"""

# ========== IMPORT LIBRARIES ==========
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="AI Robo-Advisor - Professional Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS FOR DASHBOARD ==========
st.markdown("""
<style>
    .dashboard-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 4px solid #2E86AB;
        margin: 10px 0;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #2E86AB;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
    }
    .buy-signal {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 5px 0;
    }
    .sell-signal {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        margin: 5px 0;
    }
    .neutral-signal {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
        margin: 5px 0;
    }
    .golden-cross {
        background-color: #d4edda;
        padding: 8px;
        border-radius: 5px;
        text-align: center;
    }
    .death-cross {
        background-color: #f8d7da;
        padding: 8px;
        border-radius: 5px;
        text-align: center;
    }
    .signal-strong-buy {
        background: linear-gradient(90deg, #28a745, #20c997);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .signal-buy {
        background: linear-gradient(90deg, #5cb85c, #7ccd7c);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .signal-hold {
        background: linear-gradient(90deg, #ffc107, #ffd44d);
        color: #333;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .signal-sell {
        background: linear-gradient(90deg, #dc3545, #e74c6f);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .signal-strong-sell {
        background: linear-gradient(90deg, #c0392b, #e74c3c);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .portfolio-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .graph-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# ========== ETF DATABASE WITH REAL NAMES ==========
ETF_DATABASE = {
    "BND": {
        "name": "Vanguard Total Bond Market ETF",
        "category": "Bonds",
        "description": "Broad exposure to US investment-grade bonds",
        "expense_ratio": 0.03,
        "risk_level": "Low",
        "dividend_yield": 3.2,
        "inception_date": "2007-04-03",
        "sector": "Fixed Income"
    },
    "VTI": {
        "name": "Vanguard Total Stock Market ETF",
        "category": "US Stocks",
        "description": "Entire US stock market including small, mid, and large caps",
        "expense_ratio": 0.03,
        "risk_level": "Medium-High",
        "dividend_yield": 1.4,
        "inception_date": "2001-05-24",
        "sector": "Equity"
    },
    "VXUS": {
        "name": "Vanguard Total International Stock ETF",
        "category": "International Stocks",
        "description": "Non-US companies from developed and emerging markets",
        "expense_ratio": 0.07,
        "risk_level": "Medium-High",
        "dividend_yield": 2.9,
        "inception_date": "2011-01-26",
        "sector": "Equity"
    },
    "QQQ": {
        "name": "Invesco QQQ Trust",
        "category": "Growth Stocks",
        "description": "Nasdaq 100 - technology and innovation focus",
        "expense_ratio": 0.20,
        "risk_level": "High",
        "dividend_yield": 0.6,
        "inception_date": "1999-03-10",
        "sector": "Technology Growth"
    },
    "SHY": {
        "name": "iShares 1-3 Year Treasury Bond ETF",
        "category": "Short-term Bonds",
        "description": "Low-risk US government bonds with short maturity",
        "expense_ratio": 0.15,
        "risk_level": "Very Low",
        "dividend_yield": 4.1,
        "inception_date": "2002-07-22",
        "sector": "Fixed Income"
    },
    "SPY": {
        "name": "SPDR S&P 500 ETF Trust",
        "category": "US Large Cap",
        "description": "Tracks S&P 500 Index - 500 largest US companies",
        "expense_ratio": 0.09,
        "risk_level": "Medium",
        "dividend_yield": 1.3,
        "inception_date": "1993-01-22",
        "sector": "Equity"
    },
    "TLT": {
        "name": "iShares 20+ Year Treasury Bond ETF",
        "category": "Long-term Bonds",
        "description": "Long-term US government bonds",
        "expense_ratio": 0.15,
        "risk_level": "Medium",
        "dividend_yield": 3.8,
        "inception_date": "2002-07-22",
        "sector": "Fixed Income"
    },
    "GLD": {
        "name": "SPDR Gold Shares",
        "category": "Commodities",
        "description": "Physical gold bullion",
        "expense_ratio": 0.40,
        "risk_level": "Medium",
        "dividend_yield": 0.0,
        "inception_date": "2004-11-18",
        "sector": "Commodity"
    },
    "IWM": {
        "name": "iShares Russell 2000 ETF",
        "category": "Small Cap Stocks",
        "description": "US small-cap stocks",
        "expense_ratio": 0.19,
        "risk_level": "High",
        "dividend_yield": 1.2,
        "inception_date": "2000-05-22",
        "sector": "Equity"
    },
    "EFA": {
        "name": "iShares MSCI EAFE ETF",
        "category": "Developed International",
        "description": "Developed markets excluding US and Canada",
        "expense_ratio": 0.33,
        "risk_level": "Medium",
        "dividend_yield": 2.8,
        "inception_date": "2001-08-14",
        "sector": "Equity"
    }
}

# ========== RISK PROFILING FUNCTION ==========
def calculate_risk_profile(answers):
    total_score = sum(answers)
    
    if total_score <= 12:
        return {
            "profile": "Conservative",
            "score": total_score,
            "color": "#2E86AB",
            "description": "You prioritize capital preservation over high returns",
            "allocation_style": "Income & Safety Focused",
            "risk_tolerance": "Low",
            "typical_investor": "Retirees, near-retirement, emergency funds"
        }
    elif total_score <= 20:
        return {
            "profile": "Moderate",
            "score": total_score,
            "color": "#F18F01",
            "description": "You seek balanced growth with managed risk",
            "allocation_style": "Balanced Growth",
            "risk_tolerance": "Medium",
            "typical_investor": "Mid-career professionals, college savings"
        }
    else:
        return {
            "profile": "Aggressive",
            "score": total_score,
            "color": "#C73E1D",
            "description": "You pursue maximum growth and accept volatility",
            "allocation_style": "Growth & Wealth Building",
            "risk_tolerance": "High",
            "typical_investor": "Young professionals, long-term wealth builders"
        }

# ========== PORTFOLIO CONSTRUCTION ==========
def get_portfolio_allocation(risk_profile, total_amount):
    portfolios = {
        "Conservative": {
            "allocation": {
                "BND": 0.35,
                "SHY": 0.25,
                "VTI": 0.15,
                "VXUS": 0.10,
                "GLD": 0.05,
                "TLT": 0.10
            },
            "expected_return": 0.05,
            "expected_volatility": 0.07,
            "sharpe_ratio": 0.71,
            "max_drawdown": -0.10,
            "suitable_for": "Retirement funds, emergency savings, short-term goals (1-3 years)"
        },
        "Moderate": {
            "allocation": {
                "BND": 0.15,
                "VTI": 0.35,
                "VXUS": 0.20,
                "QQQ": 0.10,
                "SPY": 0.10,
                "IWM": 0.10
            },
            "expected_return": 0.08,
            "expected_volatility": 0.12,
            "sharpe_ratio": 0.67,
            "max_drawdown": -0.25,
            "suitable_for": "Long-term wealth building, retirement (5-10 years), college funds"
        },
        "Aggressive": {
            "allocation": {
                "VTI": 0.30,
                "QQQ": 0.20,
                "VXUS": 0.15,
                "SPY": 0.15,
                "IWM": 0.15,
                "BND": 0.05
            },
            "expected_return": 0.11,
            "expected_volatility": 0.18,
            "sharpe_ratio": 0.61,
            "max_drawdown": -0.35,
            "suitable_for": "Long-term wealth (10+ years), high-income investors, inheritance planning"
        }
    }
    
    allocation_data = portfolios[risk_profile]
    
    portfolio_details = []
    for ticker, weight in allocation_data["allocation"].items():
        etf_info = ETF_DATABASE.get(ticker, {})
        portfolio_details.append({
            "Ticker": ticker,
            "ETF Name": etf_info.get("name", ticker),
            "Category": etf_info.get("category", "Other"),
            "Sector": etf_info.get("sector", "Other"),
            "Allocation %": weight * 100,
            "Amount ($)": total_amount * weight,
            "Description": etf_info.get("description", "Diversified ETF"),
            "Expense Ratio": etf_info.get("expense_ratio", 0.10),
            "Dividend Yield": etf_info.get("dividend_yield", 0),
            "Risk Level": etf_info.get("risk_level", "Medium")
        })
    
    return portfolio_details, allocation_data

# ========== MONTE CARLO SIMULATION ==========
def run_monte_carlo(initial_amount, years, expected_return, volatility, n_sims=5000):
    daily_return = expected_return / 252
    daily_vol = volatility / np.sqrt(252)
    
    trading_days = years * 252
    np.random.seed(42)
    
    random_returns = np.random.normal(daily_return, daily_vol, (trading_days, n_sims))
    cumulative_returns = np.cumprod(1 + random_returns, axis=0)
    portfolio_values = initial_amount * cumulative_returns
    
    final_values = portfolio_values[-1, :]
    
    stats = {
        "median": np.median(final_values),
        "mean": np.mean(final_values),
        "percentile_5": np.percentile(final_values, 5),
        "percentile_10": np.percentile(final_values, 10),
        "percentile_25": np.percentile(final_values, 25),
        "percentile_75": np.percentile(final_values, 75),
        "percentile_90": np.percentile(final_values, 90),
        "percentile_95": np.percentile(final_values, 95),
        "probability_of_loss": np.mean(final_values < initial_amount) * 100,
        "probability_of_gain_50pct": np.mean(final_values > initial_amount * 1.5) * 100,
        "best_case": np.max(final_values),
        "worst_case": np.min(final_values),
        "std_dev": np.std(final_values)
    }
    
    return portfolio_values, stats

# ========== TECHNICAL ANALYSIS FUNCTIONS ==========
@st.cache_data(ttl=3600)
def fetch_stock_data(ticker, start_date, end_date):
    """Fetch stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date)
        if data.empty:
            return None
        return data
    except Exception as e:
        return None

def calculate_technical_indicators(data, ma_short=20, ma_long=50, macd_fast=12, macd_slow=26, macd_signal=9):
    """Calculate MACD and Golden Cross indicators"""
    df = data.copy()
    
    # Moving averages for Golden Cross
    df['MA_Short'] = df['Close'].rolling(window=ma_short).mean()
    df['MA_Long'] = df['Close'].rolling(window=ma_long).mean()
    
    # MACD calculation
    df['EMA_Fast'] = df['Close'].ewm(span=macd_fast, adjust=False).mean()
    df['EMA_Slow'] = df['Close'].ewm(span=macd_slow, adjust=False).mean()
    df['MACD'] = df['EMA_Fast'] - df['EMA_Slow']
    df['Signal_Line'] = df['MACD'].ewm(span=macd_signal, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']
    
    # Golden Cross signals
    df['Golden_Cross'] = (df['MA_Short'] > df['MA_Long']) & (df['MA_Short'].shift(1) <= df['MA_Long'].shift(1))
    df['Death_Cross'] = (df['MA_Short'] < df['MA_Long']) & (df['MA_Short'].shift(1) >= df['MA_Long'].shift(1))
    
    # Current trend status
    df['Trend'] = 'Bullish' if df['MA_Short'].iloc[-1] > df['MA_Long'].iloc[-1] else 'Bearish'
    
    # MACD Crossover signals
    df['MACD_Bullish_Cross'] = (df['MACD'] > df['Signal_Line']) & (df['MACD'].shift(1) <= df['Signal_Line'].shift(1))
    df['MACD_Bearish_Cross'] = (df['MACD'] < df['Signal_Line']) & (df['MACD'].shift(1) >= df['Signal_Line'].shift(1))
    
    return df

def calculate_macd_table(df):
    """Create MACD data table for recent periods"""
    macd_data = []
    for i in range(min(10, len(df))):
        idx = df.index[-i-1] if i < len(df) else None
        if idx:
            macd_data.append({
                'Date': idx.strftime('%Y-%m-%d'),
                'Close': round(df['Close'].iloc[-i-1], 2),
                'MACD': round(df['MACD'].iloc[-i-1], 4),
                'Signal Line': round(df['Signal_Line'].iloc[-i-1], 4),
                'Histogram': round(df['MACD_Histogram'].iloc[-i-1], 4),
                'Signal': 'Bullish' if df['MACD'].iloc[-i-1] > df['Signal_Line'].iloc[-i-1] else 'Bearish'
            })
    return pd.DataFrame(macd_data)

def calculate_cross_table(df):
    """Create Golden Cross and Death Cross history table"""
    golden_crosses = df[df['Golden_Cross'] == True]
    death_crosses = df[df['Death_Cross'] == True]
    
    cross_data = []
    
    for idx in golden_crosses.index:
        cross_data.append({
            'Date': idx.strftime('%Y-%m-%d'),
            'Type': '🟢 Golden Cross (BUY)',
            'Short MA': round(golden_crosses.loc[idx, 'MA_Short'], 2),
            'Long MA': round(golden_crosses.loc[idx, 'MA_Long'], 2),
            'Price at Signal': round(golden_crosses.loc[idx, 'Close'], 2),
            'Signal Strength': 'Strong Bullish'
        })
    
    for idx in death_crosses.index:
        cross_data.append({
            'Date': idx.strftime('%Y-%m-%d'),
            'Type': '🔴 Death Cross (SELL)',
            'Short MA': round(death_crosses.loc[idx, 'MA_Short'], 2),
            'Long MA': round(death_crosses.loc[idx, 'MA_Long'], 2),
            'Price at Signal': round(death_crosses.loc[idx, 'Close'], 2),
            'Signal Strength': 'Strong Bearish'
        })
    
    cross_df = pd.DataFrame(cross_data)
    if not cross_df.empty:
        cross_df = cross_df.sort_values('Date', ascending=False)
    
    return cross_df

def plot_macd_graph_enhanced(df, ticker):
    """Enhanced MACD graph with clear indicators and markers"""
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05,
                        row_heights=[0.5, 0.3, 0.2],
                        subplot_titles=(f"{ticker} - Price Chart", "MACD Line & Signal Line", "MACD Histogram"))
    
    # Row 1: Price chart with moving averages
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], 
                            mode='lines', name='Close Price', 
                            line=dict(color='#1f77b4', width=2)), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_Short'], 
                            mode='lines', name='MA 20', 
                            line=dict(color='orange', width=1.5, dash='dash')), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_Long'], 
                            mode='lines', name='MA 50', 
                            line=dict(color='red', width=1.5, dash='dash')), row=1, col=1)
    
    # Mark Golden/Death Cross on price chart
    golden_crosses = df[df['Golden_Cross'] == True]
    death_crosses = df[df['Death_Cross'] == True]
    
    fig.add_trace(go.Scatter(x=golden_crosses.index, y=golden_crosses['Close'],
                            mode='markers', name='🟢 Golden Cross',
                            marker=dict(color='green', size=12, symbol='triangle-up', 
                                       line=dict(color='darkgreen', width=2))), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=death_crosses.index, y=death_crosses['Close'],
                            mode='markers', name='🔴 Death Cross',
                            marker=dict(color='red', size=12, symbol='triangle-down',
                                       line=dict(color='darkred', width=2))), row=1, col=1)
    
    # Row 2: MACD and Signal Line
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], 
                            mode='lines', name='MACD Line', 
                            line=dict(color='#2E86AB', width=2.5)), row=2, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal_Line'], 
                            mode='lines', name='Signal Line', 
                            line=dict(color='#E74C3C', width=2.5)), row=2, col=1)
    
    # Mark MACD crossovers
    bullish_cross = df[df['MACD_Bullish_Cross'] == True]
    bearish_cross = df[df['MACD_Bearish_Cross'] == True]
    
    fig.add_trace(go.Scatter(x=bullish_cross.index, y=bullish_cross['MACD'],
                            mode='markers', name='⬆️ Bullish Crossover',
                            marker=dict(color='#27AE60', size=14, symbol='triangle-up',
                                       line=dict(color='#1E8449', width=2))), row=2, col=1)
    
    fig.add_trace(go.Scatter(x=bearish_cross.index, y=bearish_cross['MACD'],
                            mode='markers', name='⬇️ Bearish Crossover',
                            marker=dict(color='#E74C3C', size=14, symbol='triangle-down',
                                       line=dict(color='#B03A2E', width=2))), row=2, col=1)
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=2, col=1)
    
    # Row 3: MACD Histogram
    colors = ['#27AE60' if val >= 0 else '#E74C3C' for val in df['MACD_Histogram']]
    fig.add_trace(go.Bar(x=df.index, y=df['MACD_Histogram'], 
                        name='Histogram', marker_color=colors,
                        opacity=0.8), row=3, col=1)
    
    fig.add_hline(y=0, line_dash="solid", line_color="gray", opacity=0.3, row=3, col=1)
    
    # Update layout
    fig.update_layout(
        title=f"📊 {ticker} - Complete Technical Analysis",
        height=700,
        showlegend=True,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="MACD Value", row=2, col=1)
    fig.update_yaxes(title_text="Histogram", row=3, col=1)
    
    return fig

def plot_golden_death_cross_graph_enhanced(df, ticker):
    """Enhanced Golden Cross vs Death Cross graph with clear indicators"""
    fig = go.Figure()
    
    # Price line
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], 
                            mode='lines', name='Close Price', 
                            line=dict(color='#1f77b4', width=2)))
    
    # Short MA
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_Short'], 
                            mode='lines', name='MA 20 (Short)', 
                            line=dict(color='#F39C12', width=2.5, dash='dash')))
    
    # Long MA
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_Long'], 
                            mode='lines', name='MA 50 (Long)', 
                            line=dict(color='#8E44AD', width=2.5, dash='dash')))
    
    # Golden Cross markers with annotations
    golden_crosses = df[df['Golden_Cross'] == True]
    death_crosses = df[df['Death_Cross'] == True]
    
    fig.add_trace(go.Scatter(x=golden_crosses.index, y=golden_crosses['Close'],
                            mode='markers+text', name='🟢 Golden Cross (BUY)',
                            marker=dict(color='#27AE60', size=18, symbol='star',
                                       line=dict(color='#1E8449', width=3)),
                            text=['🟢' for _ in range(len(golden_crosses))],
                            textposition='top center',
                            textfont=dict(size=16)))
    
    fig.add_trace(go.Scatter(x=death_crosses.index, y=death_crosses['Close'],
                            mode='markers+text', name='🔴 Death Cross (SELL)',
                            marker=dict(color='#E74C3C', size=18, symbol='star',
                                       line=dict(color='#B03A2E', width=3)),
                            text=['🔴' for _ in range(len(death_crosses))],
                            textposition='bottom center',
                            textfont=dict(size=16)))
    
    # Add shaded regions for bullish/bearish zones
    # Bullish zone (MA20 > MA50)
    bullish_df = df[df['MA_Short'] > df['MA_Long']]
    if not bullish_df.empty:
        # Find continuous bullish periods
        bullish_periods = []
        start_idx = None
        for i in range(len(bullish_df)):
            if i == 0 or (bullish_df.index[i] - bullish_df.index[i-1]).days > 1:
                if start_idx is not None:
                    bullish_periods.append((start_idx, bullish_df.index[i-1]))
                start_idx = bullish_df.index[i]
        if start_idx is not None:
            bullish_periods.append((start_idx, bullish_df.index[-1]))
        
        for start, end in bullish_periods:
            fig.add_vrect(x0=start, x1=end, fillcolor="rgba(46, 204, 113, 0.15)",
                         layer="below", line_width=0)
    
    # Bearish zone (MA20 < MA50)
    bearish_df = df[df['MA_Short'] < df['MA_Long']]
    if not bearish_df.empty:
        bearish_periods = []
        start_idx = None
        for i in range(len(bearish_df)):
            if i == 0 or (bearish_df.index[i] - bearish_df.index[i-1]).days > 1:
                if start_idx is not None:
                    bearish_periods.append((start_idx, bearish_df.index[i-1]))
                start_idx = bearish_df.index[i]
        if start_idx is not None:
            bearish_periods.append((start_idx, bearish_df.index[-1]))
        
        for start, end in bearish_periods:
            fig.add_vrect(x0=start, x1=end, fillcolor="rgba(231, 76, 60, 0.15)",
                         layer="below", line_width=0)
    
    fig.update_layout(
        title=f"🟡 {ticker} - Golden Cross vs 🔴 Death Cross Analysis",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        shapes=[
            dict(
                type="rect",
                xref="paper", yref="paper",
                x0=0, y0=0, x1=1, y1=1,
                line=dict(width=0),
            )
        ]
    )
    
    # Add annotations for signal interpretation
    current_trend = "Bullish (Golden Cross Active)" if df['MA_Short'].iloc[-1] > df['MA_Long'].iloc[-1] else "Bearish (Death Cross Active)"
    fig.add_annotation(
        x=0.02, y=0.98,
        xref="paper", yref="paper",
        text=f"<b>Current Trend: {current_trend}</b>",
        showarrow=False,
        font=dict(size=12, color="white"),
        bgcolor="#2C3E50",
        opacity=0.8,
        bordercolor="black",
        borderwidth=1
    )
    
    return fig

def get_macd_analysis_summary(df):
    """Get MACD analysis summary"""
    current_macd = df['MACD'].iloc[-1]
    current_signal = df['Signal_Line'].iloc[-1]
    current_hist = df['MACD_Histogram'].iloc[-1]
    
    macd_status = "Bullish" if current_macd > current_signal else "Bearish"
    hist_status = "Increasing" if current_hist > df['MACD_Histogram'].iloc[-2] else "Decreasing"
    
    # Calculate signal strength
    if macd_status == "Bullish" and hist_status == "Increasing":
        strength = "Strong Bullish"
    elif macd_status == "Bullish" and hist_status == "Decreasing":
        strength = "Weak Bullish"
    elif macd_status == "Bearish" and hist_status == "Decreasing":
        strength = "Strong Bearish"
    else:
        strength = "Weak Bearish"
    
    return {
        'macd_value': current_macd,
        'signal_value': current_signal,
        'histogram': current_hist,
        'status': macd_status,
        'histogram_trend': hist_status,
        'strength': strength,
        'recent_cross': "Bullish" if df['MACD_Bullish_Cross'].iloc[-5:].any() else "Bearish" if df['MACD_Bearish_Cross'].iloc[-5:].any() else "None"
    }

def get_cross_analysis_summary(df):
    """Get Golden/Death Cross analysis summary"""
    current_short_ma = df['MA_Short'].iloc[-1]
    current_long_ma = df['MA_Long'].iloc[-1]
    
    golden_crosses = df[df['Golden_Cross'] == True]
    death_crosses = df[df['Death_Cross'] == True]
    
    # Calculate days since last crossover
    days_since_last = 0
    if len(golden_crosses) > 0 or len(death_crosses) > 0:
        last_cross = max(golden_crosses.index[-1] if len(golden_crosses) > 0 else df.index[0],
                        death_crosses.index[-1] if len(death_crosses) > 0 else df.index[0])
        days_since_last = (df.index[-1] - last_cross).days
    
    return {
        'short_ma': current_short_ma,
        'long_ma': current_long_ma,
        'relationship': "Bullish (Golden Cross active)" if current_short_ma > current_long_ma else "Bearish (Death Cross active)",
        'difference': abs(current_short_ma - current_long_ma),
        'total_golden': len(golden_crosses),
        'total_death': len(death_crosses),
        'last_golden': golden_crosses.index[-1] if len(golden_crosses) > 0 else None,
        'last_death': death_crosses.index[-1] if len(death_crosses) > 0 else None,
        'days_since_last': days_since_last,
        'golden_ratio': len(golden_crosses) / (len(golden_crosses) + len(death_crosses)) if (len(golden_crosses) + len(death_crosses)) > 0 else 0
    }

def get_combined_signal(macd_summary, cross_summary):
    """Get combined technical signal"""
    macd_bullish = macd_summary['status'] == "Bullish"
    cross_bullish = "Bullish" in cross_summary['relationship']
    
    # Calculate signal strength score (1-10)
    score = 5  # Neutral
    if macd_bullish:
        score += 2
    if cross_bullish:
        score += 2
    if macd_summary['strength'] == "Strong Bullish":
        score += 1
    if macd_summary['strength'] == "Strong Bearish":
        score -= 1
    if cross_summary['golden_ratio'] > 0.6:
        score += 1
    elif cross_summary['golden_ratio'] < 0.4:
        score -= 1
    
    # Clamp score
    score = max(1, min(10, score))
    
    # Determine signal
    if score >= 8:
        signal = "Strong BUY"
        css_class = "signal-strong-buy"
    elif score >= 6:
        signal = "BUY"
        css_class = "signal-buy"
    elif score >= 4:
        signal = "HOLD"
        css_class = "signal-hold"
    elif score >= 2:
        signal = "SELL"
        css_class = "signal-sell"
    else:
        signal = "Strong SELL"
        css_class = "signal-strong-sell"
    
    return {
        'score': score,
        'signal': signal,
        'css_class': css_class,
        'macd_bullish': macd_bullish,
        'cross_bullish': cross_bullish,
        'recommendation': signal
    }

# ========== TECHNICAL ANALYSIS TAB (INTEGRATED) ==========
def technical_analysis_tab():
    """Display integrated Technical Analysis tab content"""
    st.header("📈 Technical Analysis")
    st.caption("Complete MACD and Golden/Death Cross analysis for your portfolio securities")
    st.write("---")
    
    # Check if portfolio exists
    portfolio_exists = st.session_state.get('portfolio_generated', False) and st.session_state.get('portfolio_details') is not None
    
    # Display portfolio context if available
    if portfolio_exists:
        portfolio_details = st.session_state.portfolio_details
        total_investment = st.session_state.initial_amount
        
        # Portfolio header
        st.markdown(f"""
        <div class="portfolio-header">
            <h3>💼 Your Portfolio Context</h3>
            <p>Total Investment: <strong>${total_investment:,.0f}</strong> | 
            Holdings: <strong>{len(portfolio_details)}</strong> ETFs |
            Risk Profile: <strong>{st.session_state.risk_profile}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show portfolio summary table
        with st.expander("📊 View Your Portfolio Holdings", expanded=False):
            summary_df = pd.DataFrame(portfolio_details)
            display_cols = ["Ticker", "ETF Name", "Category", "Allocation %", "Amount ($)", "Risk Level"]
            display_df = summary_df[display_cols].copy()
            display_df["Allocation %"] = display_df["Allocation %"].apply(lambda x: f"{x:.1f}%")
            display_df["Amount ($)"] = display_df["Amount ($)"].apply(lambda x: f"${x:,.0f}")
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Get portfolio tickers
        portfolio_tickers = [item['Ticker'] for item in portfolio_details]
        ticker_to_allocation = {item['Ticker']: item['Allocation %'] for item in portfolio_details}
        
        st.write("---")
        
        # Analysis mode selector
        analysis_mode = st.radio(
            "📌 Select Analysis Mode",
            ["🔍 Individual Security Analysis", "📊 Portfolio-Wide Technical Overview"],
            horizontal=True,
            help="Analyze a single security in depth OR get an overview of all portfolio holdings"
        )
        
        st.write("---")
        
        if analysis_mode == "🔍 Individual Security Analysis":
            # Individual security analysis
            display_individual_analysis(portfolio_tickers, ticker_to_allocation)
        else:
            # Portfolio-wide analysis
            display_portfolio_wide_analysis(portfolio_details)
            
    else:
        # No portfolio exists - show all ETFs
        st.warning("⚠️ No portfolio generated yet. Please go to the 'Portfolio Advisor' tab first to create your portfolio.")
        st.info("💡 You can still analyze individual securities from our database below.")
        
        # Show all ETFs for analysis
        etf_options = []
        for ticker, info in ETF_DATABASE.items():
            etf_options.append(f"{ticker} - {info['name']}")
        
        selected_etf = st.selectbox(
            "Select Security to Analyze",
            options=etf_options,
            index=1,
            help="Choose from our curated list of ETFs"
        )
        
        ticker = selected_etf.split(" - ")[0]
        
        if st.button("🔍 Analyze Security", type="primary"):
            analyze_single_security(ticker, None)

def display_individual_analysis(portfolio_tickers, ticker_to_allocation):
    """Display individual security analysis with portfolio context"""
    
    # Create options with portfolio context
    etf_options = []
    for ticker in portfolio_tickers:
        info = ETF_DATABASE.get(ticker, {})
        allocation = ticker_to_allocation.get(ticker, 0)
        etf_options.append(f"{ticker} - {info.get('name', ticker)} ({allocation:.0f}% of portfolio)")
    
    # Add option to analyze all ETFs (including non-portfolio)
    etf_options.append("--- Show All Available ETFs ---")
    
    selected_option = st.selectbox(
        "🔍 Select Security to Analyze",
        options=etf_options,
        help="Securities from your portfolio are shown with their allocation percentage"
    )
    
    # Determine if user wants to see all ETFs
    if selected_option == "--- Show All Available ETFs ---":
        all_etf_options = []
        for ticker, info in ETF_DATABASE.items():
            all_etf_options.append(f"{ticker} - {info['name']}")
        
        selected_etf = st.selectbox(
            "Select Security from Full Database",
            options=all_etf_options,
            index=1
        )
        ticker = selected_etf.split(" - ")[0]
        portfolio_context = None
    else:
        # Extract ticker from selection
        ticker = selected_option.split(" - ")[0]
        portfolio_context = {
            'allocation': ticker_to_allocation.get(ticker, 0),
            'is_in_portfolio': True
        }
    
    # Period selector
    col1, col2 = st.columns([2, 1])
    with col1:
        period_options = {
            "1 Month": 30,
            "3 Months": 90,
            "6 Months": 180,
            "1 Year": 365,
            "2 Years": 730,
            "3 Years": 1095,
            "5 Years": 1825
        }
        selected_period = st.selectbox("📅 Analysis Period", list(period_options.keys()), index=3)
        days = period_options[selected_period]
    
    with col2:
        st.write("")
        st.write("")
        analyze_clicked = st.button("🔍 Run Analysis", type="primary", use_container_width=True)
    
    if analyze_clicked:
        analyze_single_security(ticker, portfolio_context, days)

def analyze_single_security(ticker, portfolio_context, days=365):
    """Run complete technical analysis for a single security with enhanced graphs"""
    
    with st.spinner(f"📊 Analyzing {ticker}..."):
        # Fetch data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        data = fetch_stock_data(ticker, start_date, end_date)
        
        if data is None or data.empty:
            st.error(f"❌ Failed to fetch data for {ticker}. Please try again later.")
            return
        
        # Calculate indicators
        df = calculate_technical_indicators(data)
        
        # Get ETF info
        etf_info = ETF_DATABASE.get(ticker, {})
        
        # Display security header with portfolio context
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            st.subheader(f"📊 {ticker} - {etf_info.get('name', ticker)}")
            if portfolio_context and portfolio_context.get('is_in_portfolio', False):
                st.caption(f"💼 Portfolio Allocation: {portfolio_context['allocation']:.1f}%")
        
        with col2:
            st.metric("Current Price", f"${df['Close'].iloc[-1]:.2f}")
        with col3:
            st.metric("Trend", df['Trend'].iloc[-1])
        with col4:
            volume = df['Volume'].iloc[-1]
            st.metric("Volume", f"{volume:,.0f}")
        
        st.write("---")
        
        # Get analysis summaries
        macd_summary = get_macd_analysis_summary(df)
        cross_summary = get_cross_analysis_summary(df)
        combined_signal = get_combined_signal(macd_summary, cross_summary)
        
        # Display combined signal prominently
        st.markdown(f"""
        <div class="{combined_signal['css_class']}" style="margin: 20px 0;">
            <h2>🎯 Overall Technical Signal: {combined_signal['signal']}</h2>
            <p>Signal Strength Score: {combined_signal['score']}/10</p>
            <p>MACD: {'Bullish ✅' if combined_signal['macd_bullish'] else 'Bearish ❌'} | 
            Moving Average: {'Bullish ✅' if combined_signal['cross_bullish'] else 'Bearish ❌'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # ===== ENHANCED MACD GRAPH =====
        st.markdown("## 📈 MACD Analysis")
        st.write("Moving Average Convergence Divergence - momentum indicator showing trend strength and direction")
        
        # Display enhanced MACD graph
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        macd_fig = plot_macd_graph_enhanced(df, ticker)
        st.plotly_chart(macd_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # MACD Summary side by side
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("**🔍 Current MACD Status**")
            
            if macd_summary['status'] == "Bullish":
                st.markdown("""
                <div class="buy-signal">
                    <strong>✅ Bullish Momentum</strong><br>
                    MACD above Signal Line
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="sell-signal">
                    <strong>❌ Bearish Momentum</strong><br>
                    MACD below Signal Line
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"**MACD Value:** {macd_summary['macd_value']:.4f}")
            st.markdown(f"**Signal Line:** {macd_summary['signal_value']:.4f}")
            st.markdown(f"**Histogram:** {macd_summary['histogram']:.4f}")
        
        with col2:
            st.markdown(f"**Histogram Trend:** {macd_summary['histogram_trend']}")
            st.markdown(f"**Signal Strength:** {macd_summary['strength']}")
            
            if macd_summary['recent_cross'] != "None":
                st.markdown(f"**Recent Crossover:** {macd_summary['recent_cross']} 📌")
            
            # Show crossover counts
            bullish_crosses = len(df[df['MACD_Bullish_Cross'] == True])
            bearish_crosses = len(df[df['MACD_Bearish_Cross'] == True])
            st.markdown(f"**Bullish Crossovers:** {bullish_crosses}")
            st.markdown(f"**Bearish Crossovers:** {bearish_crosses}")
        
        # MACD Table
        with st.expander("📋 View MACD Calculations (Last 10 Days)", expanded=False):
            macd_table = calculate_macd_table(df)
            if not macd_table.empty:
                st.dataframe(macd_table, use_container_width=True, hide_index=True)
        
        st.write("---")
        
        # ===== ENHANCED GOLDEN CROSS vs DEATH CROSS GRAPH =====
        st.markdown("## 🟡 Golden Cross vs 🔴 Death Cross Analysis")
        st.write("Moving average crossovers help identify long-term trend reversals and significant price movements")
        
        # Display enhanced cross graph
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        cross_fig = plot_golden_death_cross_graph_enhanced(df, ticker)
        st.plotly_chart(cross_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Cross Summary side by side
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("**🔍 Current MA Status**")
            
            if "Bullish" in cross_summary['relationship']:
                st.markdown(f"""
                <div class="golden-cross">
                    <strong>🟢 GOLDEN CROSS ACTIVE</strong><br>
                    MA20 (${cross_summary['short_ma']:.2f}) > MA50 (${cross_summary['long_ma']:.2f})<br>
                    Difference: ${cross_summary['difference']:.2f}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="death-cross">
                    <strong>🔴 DEATH CROSS ACTIVE</strong><br>
                    MA20 (${cross_summary['short_ma']:.2f}) < MA50 (${cross_summary['long_ma']:.2f})<br>
                    Difference: ${cross_summary['difference']:.2f}
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"**Total Golden Crosses:** {cross_summary['total_golden']}")
            st.markdown(f"**Total Death Crosses:** {cross_summary['total_death']}")
            st.markdown(f"**Days Since Last Crossover:** {cross_summary['days_since_last']}")
            
            if cross_summary['total_golden'] > cross_summary['total_death']:
                st.success("✅ More Golden Cross signals - bullish bias")
            elif cross_summary['total_death'] > cross_summary['total_golden']:
                st.error("❌ More Death Cross signals - bearish bias")
            else:
                st.warning("⚖️ Equal bullish and bearish signals")
        
        # Cross Table
        with st.expander("📋 View Crossover History", expanded=False):
            cross_table = calculate_cross_table(df)
            if not cross_table.empty:
                st.dataframe(cross_table, use_container_width=True, hide_index=True)
            else:
                st.info("No Golden Cross or Death Cross events detected in the analysis period.")
        
        st.write("---")
        
        # ===== PORTFOLIO CONTEXT RECOMMENDATION =====
        if portfolio_context and portfolio_context.get('is_in_portfolio', False):
            st.markdown("## 💼 Portfolio Context Recommendation")
            
            allocation = portfolio_context['allocation']
            signal = combined_signal['signal']
            
            if "BUY" in signal:
                if allocation < 15:
                    st.success(f"""
                    ✅ **Consider Increasing Position**  
                    Current allocation: {allocation:.1f}%  
                    Technical signal is bullish ({signal}) - consider increasing this position in your portfolio.
                    """)
                else:
                    st.info(f"""
                    ℹ️ **Maintain Current Position**  
                    Current allocation: {allocation:.1f}%  
                    Technical signal is bullish ({signal}) - your position is already well-sized.
                    """)
            elif "SELL" in signal:
                if allocation > 10:
                    st.warning(f"""
                    ⚠️ **Consider Reducing Position**  
                    Current allocation: {allocation:.1f}%  
                    Technical signal is bearish ({signal}) - consider trimming this position.
                    """)
                else:
                    st.info(f"""
                    ℹ️ **Monitor Closely**  
                    Current allocation: {allocation:.1f}%  
                    Technical signal is bearish ({signal}) but position is small - consider holding.
                    """)
            else:
                st.info(f"""
                ℹ️ **Hold Current Position**  
                Current allocation: {allocation:.1f}%  
                Technical signal is neutral ({signal}) - maintain current allocation.
                """)

def display_portfolio_wide_analysis(portfolio_details):
    """Display technical analysis for entire portfolio with enhanced graphs"""
    st.subheader("📊 Portfolio-Wide Technical Overview")
    st.write("Analyzing technical signals across all your portfolio holdings")
    
    # Period selector for portfolio analysis
    period_options = {
        "1 Month": 30,
        "3 Months": 90,
        "6 Months": 180,
        "1 Year": 365,
        "2 Years": 730
    }
    selected_period = st.selectbox("📅 Analysis Period", list(period_options.keys()), index=3)
    days = period_options[selected_period]
    
    analyze_portfolio_clicked = st.button("📊 Analyze Entire Portfolio", type="primary")
    
    if analyze_portfolio_clicked:
        with st.spinner("📊 Analyzing all portfolio holdings..."):
            # Collect data for all holdings
            results = []
            all_macd_data = []
            all_cross_data = []
            progress_bar = st.progress(0)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            for idx, holding in enumerate(portfolio_details):
                ticker = holding['Ticker']
                allocation = holding['Allocation %']
                amount = holding['Amount ($)']
                
                # Fetch data
                data = fetch_stock_data(ticker, start_date, end_date)
                
                if data is not None and not data.empty:
                    df = calculate_technical_indicators(data)
                    macd_summary = get_macd_analysis_summary(df)
                    cross_summary = get_cross_analysis_summary(df)
                    combined = get_combined_signal(macd_summary, cross_summary)
                    
                    # Store results
                    results.append({
                        'Ticker': ticker,
                        'ETF Name': holding['ETF Name'],
                        'Allocation %': allocation,
                        'Amount ($)': amount,
                        'Category': holding['Category'],
                        'Current Price': df['Close'].iloc[-1],
                        'Trend': df['Trend'].iloc[-1],
                        'MACD Status': macd_summary['status'],
                        'MACD Strength': macd_summary['strength'],
                        'MA Status': 'Bullish' if "Bullish" in cross_summary['relationship'] else 'Bearish',
                        'Golden Crosses': cross_summary['total_golden'],
                        'Death Crosses': cross_summary['total_death'],
                        'Signal Score': combined['score'],
                        'Signal': combined['signal'],
                        'Recommendation': combined['signal'],
                        'MACD Value': macd_summary['macd_value'],
                        'Signal Value': macd_summary['signal_value'],
                        'Histogram': macd_summary['histogram']
                    })
                    
                    # Store MACD data for aggregated view
                    macd_table = calculate_macd_table(df)
                    if not macd_table.empty:
                        macd_table['Ticker'] = ticker
                        all_macd_data.append(macd_table)
                    
                    # Store Cross data for aggregated view
                    cross_table = calculate_cross_table(df)
                    if not cross_table.empty:
                        cross_table['Ticker'] = ticker
                        all_cross_data.append(cross_table)
                
                progress_bar.progress((idx + 1) / len(portfolio_details))
            
            progress_bar.empty()
            
            if results:
                # Convert to DataFrame
                results_df = pd.DataFrame(results)
                
                # ===== Portfolio Signal Dashboard =====
                st.markdown("### 🎯 Portfolio Signal Dashboard")
                
                # Summary metrics
                bullish_count = len(results_df[results_df['Signal'].str.contains('BUY')])
                bearish_count = len(results_df[results_df['Signal'].str.contains('SELL')])
                hold_count = len(results_df[results_df['Signal'] == 'HOLD'])
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📈 Bullish Signals", bullish_count, delta=f"{bullish_count/len(results)*100:.0f}%")
                with col2:
                    st.metric("📉 Bearish Signals", bearish_count, delta=f"{bearish_count/len(results)*100:.0f}%")
                with col3:
                    st.metric("⚖️ Hold Signals", hold_count, delta=f"{hold_count/len(results)*100:.0f}%")
                with col4:
                    avg_score = results_df['Signal Score'].mean()
                    st.metric("📊 Avg Signal Score", f"{avg_score:.1f}/10")
                
                st.write("---")
                
                # ===== PORTFOLIO MACD COMPARISON GRAPH =====
                if all_macd_data:
                    st.markdown("### 📈 Portfolio MACD Comparison")
                    st.write("Comparing MACD values across all portfolio holdings")
                    
                    # Combine all MACD data
                    combined_macd = pd.concat(all_macd_data, ignore_index=True)
                    
                    # Create MACD comparison graph
                    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
                    
                    fig_macd_portfolio = go.Figure()
                    
                    # Get unique tickers for color mapping
                    unique_tickers = combined_macd['Ticker'].unique()
                    colors = px.colors.qualitative.Set3[:len(unique_tickers)]
                    color_map = {ticker: colors[i] for i, ticker in enumerate(unique_tickers)}
                    
                    for ticker in unique_tickers:
                        ticker_data = combined_macd[combined_macd['Ticker'] == ticker].sort_values('Date').tail(60)
                        if not ticker_data.empty:
                            fig_macd_portfolio.add_trace(go.Scatter(
                                x=ticker_data['Date'],
                                y=ticker_data['MACD'],
                                mode='lines+markers',
                                name=f"{ticker} MACD",
                                line=dict(color=color_map[ticker], width=2.5),
                                marker=dict(size=4),
                                hovertemplate=f"<b>{ticker}</b><br>Date: %{{x}}<br>MACD: %{{y:.4f}}<extra></extra>"
                            ))
                    
                    # Add zero line
                    fig_macd_portfolio.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
                    
                    fig_macd_portfolio.update_layout(
                        title="MACD Values Comparison Across Portfolio",
                        xaxis_title="Date",
                        yaxis_title="MACD Value",
                        height=450,
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig_macd_portfolio, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # ===== Aggregated MACD Table =====
                    with st.expander("📊 View Aggregated MACD Table", expanded=False):
                        # Get the latest MACD for each ticker
                        latest_macd = combined_macd.groupby('Ticker').first().reset_index()
                        
                        # Merge with portfolio allocation info
                        macd_display = latest_macd[['Ticker', 'Date', 'Close', 'MACD', 'Signal Line', 'Histogram', 'Signal']].copy()
                        
                        # Add allocation info
                        allocation_dict = {h['Ticker']: f"{h['Allocation %']:.1f}%" for h in portfolio_details}
                        macd_display['Allocation'] = macd_display['Ticker'].map(allocation_dict)
                        
                        # Reorder columns
                        macd_display = macd_display[['Ticker', 'Allocation', 'Date', 'Close', 'MACD', 'Signal Line', 'Histogram', 'Signal']]
                        
                        # Add emoji indicators
                        def add_macd_indicator(val):
                            if val == 'Bullish':
                                return '🟢 Bullish'
                            else:
                                return '🔴 Bearish'
                        
                        macd_display['Signal'] = macd_display['Signal'].apply(add_macd_indicator)
                        
                        st.dataframe(macd_display, use_container_width=True, hide_index=True)
                    
                    st.write("---")
                
                # ===== PORTFOLIO CROSS COMPARISON GRAPH =====
                if all_cross_data:
                    st.markdown("### 🟡 Golden vs 🔴 Death Cross Portfolio Summary")
                    st.write("Crossover distribution across all portfolio holdings")
                    
                    # Combine all cross data
                    combined_cross = pd.concat(all_cross_data, ignore_index=True)
                    
                    if not combined_cross.empty:
                        # Create cross summary graph
                        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
                        
                        # Count crossovers per ticker
                        cross_counts = combined_cross.groupby(['Ticker', 'Type']).size().reset_index(name='Count')
                        
                        fig_cross_portfolio = px.bar(
                            cross_counts, 
                            x='Ticker', 
                            y='Count', 
                            color='Type',
                            title='Golden vs Death Cross Counts by Security',
                            color_discrete_map={
                                '🟢 Golden Cross (BUY)': '#27AE60',
                                '🔴 Death Cross (SELL)': '#E74C3C'
                            },
                            barmode='group',
                            text='Count'
                        )
                        
                        fig_cross_portfolio.update_traces(textposition='outside')
                        fig_cross_portfolio.update_layout(
                            height=400,
                            xaxis_title="Security",
                            yaxis_title="Number of Crossovers",
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            )
                        )
                        
                        st.plotly_chart(fig_cross_portfolio, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # ===== Aggregated Cross Table =====
                        with st.expander("📋 View Crossover History for All Securities", expanded=False):
                            cross_display = combined_cross[['Ticker', 'Date', 'Type', 'Short MA', 'Long MA', 'Price at Signal', 'Signal Strength']].copy()
                            cross_display = cross_display.sort_values(['Ticker', 'Date'], ascending=[True, False])
                            st.dataframe(cross_display, use_container_width=True, hide_index=True)
                    else:
                        st.info("No Golden Cross or Death Cross events detected in the analysis period for any security.")
                    
                    st.write("---")
                
                # ===== Signal Summary Table =====
                st.markdown("### 📋 Portfolio Technical Signals Summary")
                
                display_cols = ['Ticker', 'ETF Name', 'Allocation %', 'Current Price', 'Trend', 
                              'MACD Status', 'MA Status', 'Signal Score', 'Signal']
                
                display_df = results_df[display_cols].copy()
                display_df['Allocation %'] = display_df['Allocation %'].apply(lambda x: f"{x:.1f}%")
                display_df['Current Price'] = display_df['Current Price'].apply(lambda x: f"${x:.2f}")
                display_df['Signal Score'] = display_df['Signal Score'].apply(lambda x: f"{x:.1f}/10")
                
                # Add emoji indicators for signals
                def add_signal_indicator(val):
                    if 'BUY' in val:
                        return f"🟢 {val}"
                    elif 'SELL' in val:
                        return f"🔴 {val}"
                    else:
                        return f"🟡 {val}"
                
                display_df['Signal'] = display_df['Signal'].apply(add_signal_indicator)
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                st.write("---")
                
                # ===== Asset Class Analysis =====
                st.markdown("### 🏷️ Analysis by Asset Class")
                
                # Group by category
                category_analysis = results_df.groupby('Category').agg({
                    'Signal Score': 'mean',
                    'Signal': lambda x: max(x, key=x.value_counts().get)
                }).reset_index()
                
                category_analysis['Signal Score'] = category_analysis['Signal Score'].apply(lambda x: f"{x:.1f}/10")
                
                col1, col2 = st.columns(2)
                with col1:
                    # Bar chart of signal scores by category
                    fig = px.bar(category_analysis, x='Category', y='Signal Score', 
                                title='Average Signal Score by Asset Class',
                                color='Category', 
                                color_discrete_sequence=px.colors.qualitative.Set2)
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Sunburst chart of signals by category
                    category_counts = results_df.groupby(['Category', 'Signal']).size().reset_index(name='Count')
                    fig = px.sunburst(category_counts, path=['Category', 'Signal'], values='Count',
                                     title='Signal Distribution by Asset Class')
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.write("---")
                
                # ===== Rebalancing Suggestions =====
                st.markdown("### 🔄 Rebalancing Suggestions")
                
                suggestions = []
                
                for _, row in results_df.iterrows():
                    ticker = row['Ticker']
                    signal = row['Signal']
                    allocation = row['Allocation %']
                    score = row['Signal Score']
                    
                    if 'BUY' in signal:
                        if allocation < 15:
                            suggestions.append({
                                'Ticker': ticker,
                                'Action': '🟢 Increase',
                                'Current Allocation': f"{allocation:.1f}%",
                                'Suggested Change': f"+{min(5, 15 - allocation):.1f}%",
                                'Reason': f"Bullish signal (score: {score})"
                            })
                    elif 'SELL' in signal:
                        if allocation > 10:
                            suggestions.append({
                                'Ticker': ticker,
                                'Action': '🔴 Decrease',
                                'Current Allocation': f"{allocation:.1f}%",
                                'Suggested Change': f"-{min(5, allocation - 10):.1f}%",
                                'Reason': f"Bearish signal (score: {score})"
                            })
                
                if suggestions:
                    suggestion_df = pd.DataFrame(suggestions)
                    st.dataframe(suggestion_df, use_container_width=True, hide_index=True)
                    
                    st.info("💡 **Note:** These are suggested adjustments based on technical signals. Always consider your risk tolerance and investment goals.")
                else:
                    st.success("✅ Your portfolio is well-aligned with current technical signals. No major rebalancing needed.")
                
                st.write("---")
                
                # ===== Download Report =====
                st.markdown("### 📥 Export Technical Analysis")
                
                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="📊 Download Full Technical Analysis Report (CSV)",
                    data=csv,
                    file_name=f"portfolio_technical_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
            else:
                st.error("❌ Failed to analyze portfolio holdings. Please try again.")

# ========== DASHBOARD FUNCTIONS ==========
def create_dashboard(portfolio_details, allocation_data, sim_stats, initial_amount, investment_years, risk_profile):
    """Create comprehensive dashboard with key metrics"""
    
    st.header("📊 Investment Dashboard")
    st.write("---")
    
    # Row 1: Key Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="metric-label">Portfolio Value (Median)</div>
            <div class="metric-value">${sim_stats['median']:,.0f}</div>
            <div class="metric-label">in {investment_years} years</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_return = (sim_stats['median'] - initial_amount) / initial_amount * 100
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="metric-label">Expected Return</div>
            <div class="metric-value">{total_return:.1f}%</div>
            <div class="metric-label">over {investment_years} years</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        cagr = ((sim_stats['median'] / initial_amount) ** (1/investment_years) - 1) * 100
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="metric-label">CAGR (Annualized)</div>
            <div class="metric-value">{cagr:.1f}%</div>
            <div class="metric-label">per year</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="metric-label">Risk of Loss</div>
            <div class="metric-value">{sim_stats['probability_of_loss']:.1f}%</div>
            <div class="metric-label">probability</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("---")
    
    # Row 2: Risk & Performance Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📉 Risk Analytics")
        st.write(f"**Volatility (Annual):** {allocation_data['expected_volatility']*100:.1f}%")
        st.write(f"**Maximum Drawdown:** {allocation_data['max_drawdown']*100:.1f}%")
        st.write(f"**Sharpe Ratio:** {allocation_data['sharpe_ratio']:.2f}")
        st.write(f"**VaR (95% confidence):** -{((initial_amount - sim_stats['percentile_5'])/initial_amount)*100:.1f}%")
    
    with col2:
        st.subheader("📈 Return Scenarios")
        st.write(f"**Best Case (95th %):** +{((sim_stats['percentile_95']-initial_amount)/initial_amount)*100:.0f}%")
        st.write(f"**Optimistic (75th %):** +{((sim_stats['percentile_75']-initial_amount)/initial_amount)*100:.0f}%")
        st.write(f"**Base Case (Median):** +{((sim_stats['median']-initial_amount)/initial_amount)*100:.0f}%")
        st.write(f"**Pessimistic (25th %):** +{((sim_stats['percentile_25']-initial_amount)/initial_amount)*100:.0f}%")
        st.write(f"**Worst Case (5th %):** +{((sim_stats['percentile_5']-initial_amount)/initial_amount)*100:.0f}%")
    
    with col3:
        st.subheader("💰 Income Projection")
        total_dividends = sum([etf['Amount ($)'] * (etf['Dividend Yield']/100) for etf in portfolio_details])
        st.write(f"**Annual Dividend Income:** ${total_dividends:,.0f}")
        st.write(f"**Monthly Dividend Income:** ${total_dividends/12:,.0f}")
        st.write(f"**Dividend Yield (Portfolio):** {(total_dividends/initial_amount)*100:.1f}%")
        
        total_fees = sum([etf['Amount ($)'] * (etf['Expense Ratio']/100) for etf in portfolio_details])
        st.write(f"**Annual Fees:** ${total_fees:.0f}")
        st.write(f"**10-Year Fee Cost:** ${total_fees*10:.0f}")
    
    st.write("---")
    
    # Row 3: Confidence Intervals Chart
    st.subheader("📊 Confidence Interval Analysis")
    
    confidence_data = pd.DataFrame({
        'Confidence Level': ['90%', '80%', '50%'],
        'Lower Bound': [sim_stats['percentile_5'], sim_stats['percentile_10'], sim_stats['percentile_25']],
        'Upper Bound': [sim_stats['percentile_95'], sim_stats['percentile_90'], sim_stats['percentile_75']]
    })
    
    fig = go.Figure()
    
    for i, row in confidence_data.iterrows():
        fig.add_trace(go.Bar(
            name=f"{row['Confidence Level']} Confidence",
            x=[f"{row['Confidence Level']} Range"],
            y=[row['Upper Bound'] - row['Lower Bound']],
            base=row['Lower Bound'],
            text=[f"${row['Lower Bound']:,.0f} - ${row['Upper Bound']:,.0f}"],
            textposition='inside',
            hovertemplate=f"Range: ${row['Lower Bound']:,.0f} to ${row['Upper Bound']:,.0f}<extra></extra>"
        ))
    
    fig.add_hline(y=initial_amount, line_dash="dash", line_color="green", 
                 annotation_text=f"Initial: ${initial_amount:,.0f}")
    
    fig.update_layout(
        title="Portfolio Value Ranges by Confidence Level",
        xaxis_title="Confidence Level",
        yaxis_title="Portfolio Value ($)",
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("---")
    
    # Row 4: Banking Insights
    st.subheader("🏦 Banking & Institutional Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Portfolio Construction Methodology**")
        st.write("""
        - Based on Modern Portfolio Theory (Markowitz, 1952)
        - Optimized for risk-adjusted returns (Sharpe Ratio)
        - Uses institutional-grade ETFs from Vanguard, BlackRock, Invesco
        - Rebalancing recommended: Annually
        """)
    
    with col2:
        st.write("**Risk Management Framework**")
        st.write(f"""
        - Risk Profile: **{risk_profile}**
        - Maximum Drawdown: **{allocation_data['max_drawdown']*100:.0f}%**
        - Stop-loss recommendation: {allocation_data['max_drawdown']*100:.0f}%
        - Hedge recommendation: {'Increase bonds' if risk_profile == 'Aggressive' else 'Maintain allocation'}
        """)
    
    st.write("---")
    
    # Row 5: Comparison with Benchmarks
    st.subheader("📈 Benchmark Comparison")
    
    sAndP_return = 0.10
    bond_return = 0.04
    
    portfolio_final = sim_stats['median']
    sp500_final = initial_amount * (1 + sAndP_return) ** investment_years
    bond_final = initial_amount * (1 + bond_return) ** investment_years
    
    comparison_df = pd.DataFrame({
        'Strategy': ['Your Portfolio', 'S&P 500 Index', 'Bond Market Index'],
        'Expected Value ($)': [portfolio_final, sp500_final, bond_final],
        'Return (%)': [
            ((portfolio_final - initial_amount) / initial_amount * 100),
            ((sp500_final - initial_amount) / initial_amount * 100),
            ((bond_final - initial_amount) / initial_amount * 100)
        ]
    })
    
    fig = px.bar(comparison_df, x='Strategy', y='Return (%)', 
                 title=f'Performance Comparison vs Market Benchmarks ({investment_years} years)',
                 color='Strategy',
                 color_discrete_sequence=['#2E86AB', '#F18F01', '#28a745'])
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    fig.update_layout(height=400)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Row 6: Probability Distribution
    st.subheader("📊 Probability Distribution of Returns")
    
    final_values_sim = np.random.normal(sim_stats['mean'], sim_stats['std_dev'], 10000)
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=final_values_sim,
        nbinsx=50,
        marker_color='#2E86AB',
        opacity=0.7,
        name='Distribution'
    ))
    
    fig.add_vline(x=initial_amount, line_dash="dash", line_color="red",
                 annotation_text="Break-even")
    fig.add_vline(x=sim_stats['median'], line_dash="dash", line_color="green",
                 annotation_text="Median")
    
    fig.update_layout(
        title="Distribution of Possible Portfolio Values",
        xaxis_title="Portfolio Value ($)",
        yaxis_title="Frequency",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ========== MAIN APPLICATION ==========
def main():
    # Header
    st.title("🤖 AI Robo-Advisor")
    st.caption("Professional Portfolio Construction with Real-Time Analytics Dashboard & Integrated Technical Analysis")
    st.write("---")
    
    # Initialize session state for portfolio data
    if 'portfolio_generated' not in st.session_state:
        st.session_state.portfolio_generated = False
        st.session_state.portfolio_details = None
        st.session_state.risk_profile = None
        st.session_state.investment_years = None
        st.session_state.initial_amount = None
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📊 Portfolio Advisor", "📈 Technical Analysis", "📚 Education & Resources"])
    
    # Tab 1: Portfolio Advisor
    with tab1:
        # Sidebar - Risk Assessment
        with st.sidebar:
            st.header("📋 Step 1: Risk Assessment")
            st.write("Answer these 5 questions honestly:")
            st.write("---")
            
            q1 = st.slider(
                "**1. Investment Time Horizon**",
                min_value=1, max_value=30, value=10,
                help="Longer horizons allow more risk and potential growth"
            )
            q1_score = min(5, q1 // 6 + 1)
            
            q2 = st.select_slider(
                "**2. Reaction to Market Drop (20%)**",
                options=["Sell everything", "Get nervous", "Do nothing", "Buy more", "Aggressively buy more"],
                value="Do nothing",
                help="How would you emotionally react to a market crash?"
            )
            q2_scores = {"Sell everything": 1, "Get nervous": 2, "Do nothing": 3, 
                        "Buy more": 4, "Aggressively buy more": 5}
            q2_score = q2_scores[q2]
            
            q3 = st.radio(
                "**3. Primary Investment Goal**",
                ["Capital preservation", "Income generation", "Balanced growth", 
                 "Long-term wealth", "Maximum growth"],
                index=2,
                help="What matters most to you?"
            )
            q3_scores = {"Capital preservation": 1, "Income generation": 2, 
                        "Balanced growth": 3, "Long-term wealth": 4, "Maximum growth": 5}
            q3_score = q3_scores[q3]
            
            q4 = st.slider(
                "**4. Risk Capacity (% of savings)**",
                min_value=0, max_value=100, value=50,
                help="What percentage of your total savings are you investing?"
            )
            q4_score = min(5, q4 // 20 + 1)
            
            q5 = st.select_slider(
                "**5. Expected Annual Return**",
                options=["3-4% (Very safe)", "5-6% (Conservative)", "7-8% (Moderate)", 
                        "9-10% (Growth)", "11%+ (Aggressive)"],
                value="7-8% (Moderate)",
                help="Higher returns require accepting higher risk"
            )
            q5_scores = {"3-4% (Very safe)": 1, "5-6% (Conservative)": 2, 
                        "7-8% (Moderate)": 3, "9-10% (Growth)": 4, "11%+ (Aggressive)": 5}
            q5_score = q5_scores[q5]
            
            st.write("---")
            
            st.header("💰 Step 2: Investment Details")
            initial_amount = st.number_input(
                "Investment Amount ($)",
                min_value=1000,
                max_value=1000000,
                value=10000,
                step=1000,
                help="Minimum $1,000 recommended for diversified portfolio"
            )
            
            investment_years = st.slider(
                "Investment Period (Years)",
                min_value=1,
                max_value=30,
                value=10,
                help="How long will you stay invested?"
            )
            
            st.write("---")
            show_dashboard = st.checkbox("📊 Show Detailed Dashboard", value=True)
            st.write("---")
            submit = st.button("🎯 Generate Portfolio", type="primary", use_container_width=True)
        
        # Main content - Results
        if submit:
            answers = [q1_score, q2_score, q3_score, q4_score, q5_score]
            risk_result = calculate_risk_profile(answers)
            risk_profile = risk_result["profile"]
            
            # Store in session state
            st.session_state.portfolio_generated = True
            st.session_state.risk_profile = risk_profile
            st.session_state.investment_years = investment_years
            st.session_state.initial_amount = initial_amount
            
            portfolio_details, allocation_data = get_portfolio_allocation(risk_profile, initial_amount)
            st.session_state.portfolio_details = portfolio_details
            st.session_state.allocation_data = allocation_data
            
            st.success(f"""
            ### ✅ Your Risk Profile: **{risk_profile}**
            {risk_result['description']}
            **Style**: {risk_result['allocation_style']} | **Score**: {risk_result['score']}/25 | **Risk Tolerance**: {risk_result['risk_tolerance']}
            """)
            
            st.write("---")
            st.header("📊 Your Personalized Portfolio")
            st.write(f"Based on your {risk_profile} profile, we recommend this ETF portfolio:")
            
            portfolio_df = pd.DataFrame(portfolio_details)
            col1, col2 = st.columns([1.5, 1])
            
            with col1:
                display_df = portfolio_df[["Ticker", "ETF Name", "Category", "Allocation %", "Amount ($)", "Expense Ratio", "Dividend Yield"]]
                display_df["Allocation %"] = display_df["Allocation %"].apply(lambda x: f"{x:.0f}%")
                display_df["Amount ($)"] = display_df["Amount ($)"].apply(lambda x: f"${x:,.0f}")
                display_df["Expense Ratio"] = display_df["Expense Ratio"].apply(lambda x: f"{x:.2f}%")
                display_df["Dividend Yield"] = display_df["Dividend Yield"].apply(lambda x: f"{x:.1f}%")
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                st.write("---")
                st.write("**📈 Portfolio Characteristics:**")
                st.write(f"• Expected Annual Return: **{allocation_data['expected_return']*100:.0f}%**")
                st.write(f"• Expected Volatility: **{allocation_data['expected_volatility']*100:.0f}%**")
                st.write(f"• Sharpe Ratio: **{allocation_data['sharpe_ratio']:.2f}**")
                st.write(f"• Suitable For: **{allocation_data['suitable_for']}**")
            
            with col2:
                fig = px.pie(portfolio_df, values="Allocation %", names=portfolio_df["Ticker"],
                            title="Asset Allocation", color_discrete_sequence=px.colors.qualitative.Set2, hole=0.3)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.write("---")
            st.header("📈 Monte Carlo Simulation")
            st.write(f"Projecting ${initial_amount:,} over {investment_years} years with {allocation_data['expected_return']*100:.0f}% expected return")
            
            with st.spinner(f"Running 5,000 market simulations..."):
                sim_results, sim_stats = run_monte_carlo(initial_amount, investment_years, 
                                                        allocation_data['expected_return'],
                                                        allocation_data['expected_volatility'], n_sims=5000)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Median Outcome", f"${sim_stats['median']:,.0f}")
            with col2:
                st.metric("Expected Range", f"${sim_stats['percentile_25']:,.0f} - ${sim_stats['percentile_75']:,.0f}")
            with col3:
                st.metric("Risk of Loss", f"{sim_stats['probability_of_loss']:.1f}%")
            with col4:
                st.metric("Gain >50% Probability", f"{sim_stats['probability_of_gain_50pct']:.1f}%")
            
            days = np.arange(len(sim_results))
            median_path = np.median(sim_results, axis=1)
            percentile_25 = np.percentile(sim_results, 25, axis=1)
            percentile_75 = np.percentile(sim_results, 75, axis=1)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=np.concatenate([days, days[::-1]]), y=np.concatenate([percentile_75, percentile_25[::-1]]),
                                    fill='toself', fillcolor='rgba(128, 128, 128, 0.2)',
                                    line=dict(color='rgba(255,255,255,0)'), name='25th-75th Percentile'))
            fig.add_trace(go.Scatter(x=days, y=median_path, mode='lines', line=dict(color='red', width=2), name='Median Path'))
            fig.add_hline(y=initial_amount, line_dash="dash", line_color="green", annotation_text="Initial Investment")
            fig.update_layout(title=f"Portfolio Value Over {investment_years} Years (5,000 Simulations)",
                            xaxis_title="Trading Days", yaxis_title="Portfolio Value ($)", hovermode='x unified', height=500)
            st.plotly_chart(fig, use_container_width=True)
            st.write("---")
            
            if show_dashboard:
                create_dashboard(portfolio_details, allocation_data, sim_stats, initial_amount, investment_years, risk_profile)
            
            st.header("📚 Understanding Your Portfolio")
            with st.expander("🔍 What are these ETFs? (Click to expand)"):
                for etf in portfolio_details:
                    st.write(f"**{etf['Ticker']} - {etf['ETF Name']}**")
                    st.write(f"*{etf['Description']}*")
                    st.write(f"Category: {etf['Category']} | Expense Ratio: {etf['Expense Ratio']:.2f}% | Dividend Yield: {etf['Dividend Yield']:.1f}%")
                    st.write("---")
            
            with st.expander("⚠️ Important Disclosures & Ethics"):
                st.write("""
                **Regulatory & Ethical Considerations:**
                1. Past performance does not guarantee future results
                2. All investments carry risk of loss
                3. Monte Carlo simulations are probabilistic, not certainties
                4. Not personalized financial advice - consult a licensed advisor
                """)
        
        else:
            st.info("### 👈 Complete the risk assessment in the left sidebar to get your personalized portfolio")
            st.write("""
            **This tool will:**
            - ✅ Assess your risk tolerance using 5 professional questions
            - ✅ Build a diversified ETF portfolio using real funds
            - ✅ Run 5,000 Monte Carlo simulations to project outcomes
            - ✅ Show detailed dashboard with risk analytics
            - ✅ Provide integrated technical analysis for all holdings
            """)
    
    # Tab 2: Technical Analysis (Integrated)
    with tab2:
        technical_analysis_tab()
    
    # Tab 3: Education & Resources
    with tab3:
        st.header("📚 Educational Resources")
        st.write("---")
        
        st.subheader("🎓 Understanding Technical Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("📈 What is MACD?", expanded=True):
                st.write("""
                **Moving Average Convergence Divergence (MACD)** is a momentum indicator showing the relationship between two moving averages.
                
                **Components:**
                - **MACD Line**: Fast EMA - Slow EMA (12-day - 26-day)
                - **Signal Line**: 9-day EMA of MACD line
                - **Histogram**: MACD - Signal Line
                
                **How to Use:**
                - **Bullish**: MACD crosses above Signal line
                - **Bearish**: MACD crosses below Signal line
                - **Momentum**: Histogram turning from negative to positive indicates building bullish momentum
                
                **Our Calculation Method:**
                We use standard parameters (12, 26, 9) for consistent analysis across all securities.
                """)
            
            with st.expander("🟡 Golden Cross vs Death Cross", expanded=True):
                st.write("""
                **Golden Cross (Bullish):**
                - 50-day MA crosses ABOVE 200-day MA
                - Indicates long-term bullish reversal
                - Historically leads to significant uptrends
                - **Our implementation:** MA 20 crossing above MA 50 for more responsive signals
                
                **Death Cross (Bearish):**
                - 50-day MA crosses BELOW 200-day MA
                - Indicates long-term bearish reversal
                - Often precedes market corrections
                - **Our implementation:** MA 20 crossing below MA 50
                
                **For portfolio management:** Use crossovers to adjust exposure to different asset classes.
                """)
        
        with col2:
            with st.expander("📊 How We Calculate Technical Indicators"):
                st.write("""
                **MACD Calculation Steps:**
                1. Calculate 12-day EMA of closing prices
                2. Calculate 26-day EMA of closing prices
                3. MACD Line = 12-day EMA - 26-day EMA
                4. Signal Line = 9-day EMA of MACD Line
                5. Histogram = MACD Line - Signal Line
                
                **Golden/Death Cross Calculation:**
                1. Calculate 20-day Simple Moving Average
                2. Calculate 50-day Simple Moving Average
                3. Golden Cross = 20 MA crosses above 50 MA
                4. Death Cross = 20 MA crosses below 50 MA
                
                **Data Source:** Yahoo Finance (real-time market data)
                **Update Frequency:** Daily (cached for performance)
                """)
            
            with st.expander("⚠️ Limitations & Best Practices"):
                st.write("""
                **Important Caveats:**
                - Not 100% accurate - false signals occur
                - Works best in trending markets, not sideways
                - Should complement fundamental analysis
                - Past patterns don't guarantee future results
                - Best for short to medium-term decisions
                
                **Best Practices for Your Portfolio:**
                1. Use MACD for timing entries/exits
                2. Use Golden/Death Cross for trend direction
                3. Combine with your risk profile for position sizing
                4. Rebalance quarterly, not on every signal
                5. Maintain strategic allocation for long-term success
                """)
        
        st.write("---")
        st.subheader("📖 Recommended Reading")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Technical Analysis**")
            st.write("• Technical Analysis of Financial Markets - John Murphy")
            st.write("• Japanese Candlestick Charting - Steve Nison")
            st.write("• Encyclopedia of Chart Patterns - Thomas Bulkowski")
        
        with col2:
            st.markdown("**Portfolio Management**")
            st.write("• The Intelligent Asset Allocator - William Bernstein")
            st.write("• Adaptive Asset Allocation - Adam Butler")
            st.write("• The Ivy Portfolio - Meb Faber")
        
        with col3:
            st.markdown("**Behavioral Finance**")
            st.write("• Thinking, Fast and Slow - Daniel Kahneman")
            st.write("• Misbehaving - Richard Thaler")
            st.write("• The Psychology of Money - Morgan Housel")
        
        st.write("---")
        st.info("💡 **Pro Tip:** Combine technical analysis with fundamental research. Use technicals for timing and fundamentals for selection. Always maintain alignment with your long-term investment goals and risk tolerance.")

# ========== RUN APPLICATION ==========
if __name__ == "__main__":
    main()
