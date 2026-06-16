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

def plot_macd_graph(df, ticker):
    """Plot MACD graph with price and MACD indicator"""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.08, 
                        row_heights=[0.5, 0.5],
                        subplot_titles=(f"{ticker} - Price Chart", "MACD Indicator"))
    
    # Price chart
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], 
                            mode='lines', name='Close Price', 
                            line=dict(color='black', width=1.5)), row=1, col=1)
    
    # MACD and Signal Line
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], 
                            mode='lines', name='MACD Line', 
                            line=dict(color='blue', width=2)), row=2, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal_Line'], 
                            mode='lines', name='Signal Line', 
                            line=dict(color='red', width=2)), row=2, col=1)
    
    # MACD Histogram
    colors = ['green' if val >= 0 else 'red' for val in df['MACD_Histogram']]
    fig.add_trace(go.Bar(x=df.index, y=df['MACD_Histogram'], 
                        name='MACD Histogram', marker_color=colors), row=2, col=1)
    
    # Mark MACD crossovers
    bullish_cross = df[df['MACD_Bullish_Cross'] == True]
    bearish_cross = df[df['MACD_Bearish_Cross'] == True]
    
    fig.add_trace(go.Scatter(x=bullish_cross.index, y=bullish_cross['MACD'],
                            mode='markers', name='Bullish Crossover',
                            marker=dict(color='green', size=10, symbol='triangle-up')), row=2, col=1)
    
    fig.add_trace(go.Scatter(x=bearish_cross.index, y=bearish_cross['MACD'],
                            mode='markers', name='Bearish Crossover',
                            marker=dict(color='red', size=10, symbol='triangle-down')), row=2, col=1)
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
    
    fig.update_layout(title=f"{ticker} - MACD Analysis",
                     height=600,
                     showlegend=True,
                     xaxis_title="Date")
    
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="MACD Value", row=2, col=1)
    
    return fig

def plot_golden_death_cross_graph(df, ticker):
    """Plot Golden Cross vs Death Cross graph"""
    fig = go.Figure()
    
    # Price line
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], 
                            mode='lines', name='Close Price', 
                            line=dict(color='gray', width=1, dash='dot')))
    
    # Short MA
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_Short'], 
                            mode='lines', name=f'MA 20 (Short)', 
                            line=dict(color='orange', width=2)))
    
    # Long MA
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_Long'], 
                            mode='lines', name=f'MA 50 (Long)', 
                            line=dict(color='blue', width=2)))
    
    # Golden Cross markers
    golden_crosses = df[df['Golden_Cross'] == True]
    death_crosses = df[df['Death_Cross'] == True]
    
    fig.add_trace(go.Scatter(x=golden_crosses.index, y=golden_crosses['Close'],
                            mode='markers', name='🟢 Golden Cross (BUY)',
                            marker=dict(color='green', size=14, symbol='triangle-up', 
                                       line=dict(color='darkgreen', width=2))))
    
    fig.add_trace(go.Scatter(x=death_crosses.index, y=death_crosses['Close'],
                            mode='markers', name='🔴 Death Cross (SELL)',
                            marker=dict(color='red', size=14, symbol='triangle-down',
                                       line=dict(color='darkred', width=2))))
    
    # Add filled area between MAs when bullish
    bullish_periods = df[df['MA_Short'] > df['MA_Long']]
    if not bullish_periods.empty:
        fig.add_trace(go.Scatter(x=bullish_periods.index, y=bullish_periods['MA_Short'],
                                fill='tonexty', mode='none',
                                fillcolor='rgba(0, 255, 0, 0.1)',
                                name='Bullish Zone'))
    
    fig.update_layout(title=f"{ticker} - Golden Cross vs Death Cross Analysis",
                     xaxis_title="Date",
                     yaxis_title="Price ($)",
                     height=500,
                     hovermode='x unified',
                     legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    
    return fig

def get_macd_analysis_summary(df):
    """Get MACD analysis summary"""
    current_macd = df['MACD'].iloc[-1]
    current_signal = df['Signal_Line'].iloc[-1]
    current_hist = df['MACD_Histogram'].iloc[-1]
    
    macd_status = "Bullish" if current_macd > current_signal else "Bearish"
    hist_status = "Increasing" if current_hist > df['MACD_Histogram'].iloc[-2] else "Decreasing"
    
    return {
        'macd_value': current_macd,
        'signal_value': current_signal,
        'histogram': current_hist,
        'status': macd_status,
        'histogram_trend': hist_status,
        'recent_cross': "Bullish" if df['MACD_Bullish_Cross'].iloc[-5:].any() else "Bearish" if df['MACD_Bearish_Cross'].iloc[-5:].any() else "None"
    }

def get_cross_analysis_summary(df):
    """Get Golden/Death Cross analysis summary"""
    current_short_ma = df['MA_Short'].iloc[-1]
    current_long_ma = df['MA_Long'].iloc[-1]
    
    golden_crosses = df[df['Golden_Cross'] == True]
    death_crosses = df[df['Death_Cross'] == True]
    
    return {
        'short_ma': current_short_ma,
        'long_ma': current_long_ma,
        'relationship': "Bullish (Golden Cross active)" if current_short_ma > current_long_ma else "Bearish (Death Cross active)",
        'difference': abs(current_short_ma - current_long_ma),
        'total_golden': len(golden_crosses),
        'total_death': len(death_crosses),
        'last_golden': golden_crosses.index[-1] if len(golden_crosses) > 0 else None,
        'last_death': death_crosses.index[-1] if len(death_crosses) > 0 else None
    }

# ========== TECHNICAL ANALYSIS TAB ==========
def technical_analysis_tab():
    """Display Technical Analysis tab content"""
    st.header("📈 Technical Analysis")
    st.caption("Complete MACD and Golden/Death Cross analysis with calculations, tables, and graphs")
    st.write("---")
    
    # Security Selection
    col1, col2 = st.columns([2, 1])
    with col1:
        ticker_input = st.text_input("Enter Stock Ticker", value="AAPL", help="e.g., AAPL, MSFT, TSLA, SPY")
    with col2:
        period_options = {
            "1 Month": 30,
            "3 Months": 90,
            "6 Months": 180,
            "1 Year": 365,
            "2 Years": 730,
            "3 Years": 1095,
            "5 Years": 1825
        }
        selected_period = st.selectbox("Analysis Period", list(period_options.keys()), index=3)
        days = period_options[selected_period]
    
    analyze_clicked = st.button("🔍 Analyze Security", type="primary", use_container_width=False)
    
    st.write("---")
    
    if analyze_clicked:
        ticker = ticker_input.upper().strip()
        
        with st.spinner(f"Fetching and analyzing {ticker}..."):
            # Fetch data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            data = fetch_stock_data(ticker, start_date, end_date)
            
            if data is not None and not data.empty:
                # Calculate indicators
                df = calculate_technical_indicators(data)
                
                # Display current price and basic info
                st.subheader(f"📊 {ticker} - Current Market Data")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Current Price", f"${df['Close'].iloc[-1]:.2f}")
                with col2:
                    st.metric("Volume", f"{df['Volume'].iloc[-1]:,.0f}")
                with col3:
                    st.metric("Trend", df['Trend'].iloc[-1])
                with col4:
                    high_low = df['High'].iloc[-1] - df['Low'].iloc[-1]
                    st.metric("Day Range", f"${df['Low'].iloc[-1]:.2f} - ${df['High'].iloc[-1]:.2f}")
                
                st.write("---")
                
                # Get summaries
                macd_summary = get_macd_analysis_summary(df)
                cross_summary = get_cross_analysis_summary(df)
                
                # ===== MACD SECTION =====
                st.markdown("## 📈 MACD (Moving Average Convergence Divergence) Analysis")
                st.write("MACD helps identify momentum and trend direction through the relationship between moving averages.")
                
                # MACD Graph
                st.subheader("📊 MACD Chart")
                macd_fig = plot_macd_graph(df, ticker)
                st.plotly_chart(macd_fig, use_container_width=True)
                
                # MACD Calculations Table
                st.subheader("📋 MACD Recent Calculations (Last 10 Days)")
                macd_table = calculate_macd_table(df)
                if not macd_table.empty:
                    st.dataframe(macd_table, use_container_width=True, hide_index=True)
                
                # MACD Interpretation
                st.subheader("🔍 MACD Interpretation")
                col_m1, col_m2 = st.columns(2)
                
                with col_m1:
                    if macd_summary['status'] == "Bullish":
                        st.markdown("""
                        <div class="buy-signal">
                            <strong>✅ MACD Bullish Signal</strong><br>
                            MACD line is above the Signal line, indicating upward momentum.
                            This suggests potential price appreciation in the near term.
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="sell-signal">
                            <strong>❌ MACD Bearish Signal</strong><br>
                            MACD line is below the Signal line, indicating downward momentum.
                            This suggests potential price depreciation in the near term.
                        </div>
                        """, unsafe_allow_html=True)
                
                with col_m2:
                    if macd_summary['histogram_trend'] == "Increasing" and macd_summary['status'] == "Bullish":
                        st.markdown("""
                        <div class="buy-signal">
                            <strong>📈 Increasing Bullish Momentum</strong><br>
                            Histogram is positive and increasing, confirming strong bullish momentum.
                        </div>
                        """, unsafe_allow_html=True)
                    elif macd_summary['histogram_trend'] == "Decreasing" and macd_summary['status'] == "Bearish":
                        st.markdown("""
                        <div class="sell-signal">
                            <strong>📉 Increasing Bearish Momentum</strong><br>
                            Histogram is negative and decreasing, confirming strong bearish momentum.
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="neutral-signal">
                            <strong>⚠️ Mixed Momentum Signals</strong><br>
                            Monitor for clearer trend confirmation before making decisions.
                        </div>
                        """, unsafe_allow_html=True)
                
                st.write("---")
                
                # ===== GOLDEN CROSS vs DEATH CROSS SECTION =====
                st.markdown("## 🟡 Golden Cross vs 🔴 Death Cross Analysis")
                st.write("Moving Average crossovers help identify long-term trend reversals and significant price movements.")
                
                # Golden/Death Cross Graph
                st.subheader("📊 Golden Cross vs Death Cross Chart")
                cross_fig = plot_golden_death_cross_graph(df, ticker)
                st.plotly_chart(cross_fig, use_container_width=True)
                
                # Cross History Table
                st.subheader("📋 Crossover History")
                cross_table = calculate_cross_table(df)
                if not cross_table.empty:
                    st.dataframe(cross_table, use_container_width=True, hide_index=True)
                else:
                    st.info("No Golden Cross or Death Cross events detected in the analysis period.")
                
                # Cross Interpretation
                st.subheader("🔍 Crossover Interpretation")
                
                col_c1, col_c2 = st.columns(2)
                
                with col_c1:
                    st.markdown("**Current MA Status:**")
                    if "Bullish" in cross_summary['relationship']:
                        st.markdown(f"""
                        <div class="golden-cross">
                            <strong>🟢 GOLDEN CROSS ACTIVE</strong><br>
                            Short MA (${cross_summary['short_ma']:.2f}) > Long MA (${cross_summary['long_ma']:.2f})<br>
                            Difference: ${cross_summary['difference']:.2f}<br>
                            <strong>Signal:</strong> Bullish - Consider increasing exposure
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="death-cross">
                            <strong>🔴 DEATH CROSS ACTIVE</strong><br>
                            Short MA (${cross_summary['short_ma']:.2f}) < Long MA (${cross_summary['long_ma']:.2f})<br>
                            Difference: ${cross_summary['difference']:.2f}<br>
                            <strong>Signal:</strong> Bearish - Consider reducing exposure
                        </div>
                        """, unsafe_allow_html=True)
                
                with col_c2:
                    st.markdown("**Historical Crossovers:**")
                    st.write(f"• **Golden Crosses:** {cross_summary['total_golden']} occurrences")
                    st.write(f"• **Death Crosses:** {cross_summary['total_death']} occurrences")
                    
                    if cross_summary['total_golden'] > cross_summary['total_death']:
                        st.success("More Golden Cross signals indicate overall bullish bias")
                    elif cross_summary['total_death'] > cross_summary['total_golden']:
                        st.error("More Death Cross signals indicate overall bearish bias")
                    else:
                        st.warning("Equal number of bullish and bearish signals")
                
                st.write("---")
                
                # ===== COMBINED RECOMMENDATION =====
                st.subheader("🎯 Combined Technical Recommendation")
                
                # Calculate overall signal
                macd_bullish = macd_summary['status'] == "Bullish"
                cross_bullish = "Bullish" in cross_summary['relationship']
                
                if macd_bullish and cross_bullish:
                    st.success(f"""
                    ### ✅ STRONG BULLISH SIGNAL - {ticker}
                    
                    **Recommendation:** BUY / ACCUMULATE
                    
                    **Rationale:**
                    - MACD indicates bullish momentum
                    - Golden Cross active (bullish MA crossover)
                    - Both primary indicators align positively
                    
                    **Action:** Consider adding to position with stop-loss below recent support.
                    """)
                elif macd_bullish or cross_bullish:
                    st.warning(f"""
                    ### ⚠️ MODERATE BULLISH SIGNAL - {ticker}
                    
                    **Recommendation:** HOLD / ACCUMULATE CAUTIOUSLY
                    
                    **Rationale:**
                    - Mixed signals between MACD and MA crossovers
                    - One indicator shows bullishness while other is neutral/bearish
                    - Wait for confirmation before increasing exposure
                    
                    **Action:** Maintain current position, watch for confirmation.
                    """)
                else:
                    st.error(f"""
                    ### ❌ BEARISH SIGNAL - {ticker}
                    
                    **Recommendation:** SELL / REDUCE
                    
                    **Rationale:**
                    - MACD indicates bearish momentum
                    - Death Cross active (bearish MA crossover)
                    - Both primary indicators align negatively
                    
                    **Action:** Consider reducing position or implementing tighter stops.
                    """)
                
                st.write("---")
                
                # Summary metrics
                st.subheader("📊 Key Technical Metrics")
                
                metrics_cols = st.columns(5)
                with metrics_cols[0]:
                    st.metric("MACD Status", macd_summary['status'])
                with metrics_cols[1]:
                    st.metric("MA Status", "Bullish" if cross_bullish else "Bearish")
                with metrics_cols[2]:
                    st.metric("Golden Crosses", cross_summary['total_golden'])
                with metrics_cols[3]:
                    st.metric("Death Crosses", cross_summary['total_death'])
                with metrics_cols[4]:
                    overall = "BUY" if (macd_bullish and cross_bullish) else "SELL" if (not macd_bullish and not cross_bullish) else "HOLD"
                    st.metric("Overall Signal", overall)
                
                st.write("---")
                st.info("💡 **Technical Analysis Note:** Technical indicators work best when combined with fundamental analysis. Always consider your risk tolerance and investment goals before making decisions.")
                
            else:
                st.error(f"❌ Failed to fetch data for {ticker}. Please check the ticker symbol and try again.")
                st.info("💡 Make sure the ticker symbol is valid (e.g., AAPL, MSFT, TSLA, SPY)")
    
    else:
        st.info("👈 Enter a stock ticker and click 'Analyze Security' to begin technical analysis")
        
        st.markdown("""
        ### 🎯 What this tool provides:
        
        **📈 MACD Analysis**
        - Calculates MACD line, Signal line, and Histogram
        - Displays interactive chart with crossover markers
        - Shows recent calculations table (last 10 days)
        - Provides bullish/bearish interpretation with momentum strength
        
        **🟡 Golden Cross vs 🔴 Death Cross**
        - Detects moving average crossovers (MA 20 & MA 50)
        - Shows historical crossover events with dates and prices
        - Visual chart with highlighted crossover regions
        - Current trend status and signal strength
        
        **🎯 Combined Conclusion**
        - Aggregates both indicators for overall signal
        - Provides actionable recommendation
        - Key metrics summary for quick reference
        
        ### 📊 Popular Tickers to Analyze:
        **Stocks:** AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META, JPM, KO, PFE
        **ETFs:** SPY, QQQ, VTI, BND, VXUS, IWM, TLT
        **Commodities:** GLD
        """)

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
    
    # Tab 2: Technical Analysis (Standalone)
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
