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
    .risk-badge {
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        display: inline-block;
    }
    .buy-signal {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    .sell-signal {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
    }
    .neutral-signal {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
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
                "BND": 0.40,
                "SHY": 0.25,
                "VTI": 0.20,
                "VXUS": 0.10,
                "GLD": 0.05
            },
            "expected_return": 0.05,
            "expected_volatility": 0.07,
            "sharpe_ratio": 0.71,
            "max_drawdown": -0.10,
            "suitable_for": "Retirement funds, emergency savings, short-term goals (1-3 years)"
        },
        "Moderate": {
            "allocation": {
                "BND": 0.20,
                "VTI": 0.40,
                "VXUS": 0.20,
                "QQQ": 0.10,
                "SPY": 0.10
            },
            "expected_return": 0.08,
            "expected_volatility": 0.12,
            "sharpe_ratio": 0.67,
            "max_drawdown": -0.25,
            "suitable_for": "Long-term wealth building, retirement (5-10 years), college funds"
        },
        "Aggressive": {
            "allocation": {
                "VTI": 0.35,
                "QQQ": 0.25,
                "VXUS": 0.20,
                "SPY": 0.15,
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
        st.error(f"Error fetching {ticker}: {str(e)}")
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
    
    return df

def plot_macd_analysis(df, ticker, macd_fast, macd_slow, macd_signal):
    """Plot MACD analysis separately"""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.08, 
                        row_heights=[0.5, 0.5],
                        subplot_titles=(f"{ticker} - Price Chart", "MACD Indicator"))
    
    # Price chart with moving averages
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
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
    
    fig.update_layout(title=f"{ticker} - MACD Analysis",
                     height=600,
                     showlegend=True,
                     xaxis_title="Date")
    
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="MACD Value", row=2, col=1)
    
    return fig

def plot_golden_death_cross(df, ticker, ma_short, ma_long):
    """Plot Golden Cross vs Death Cross separately"""
    fig = go.Figure()
    
    # Price line
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], 
                            mode='lines', name='Close Price', 
                            line=dict(color='gray', width=1)))
    
    # Short MA
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_Short'], 
                            mode='lines', name=f'MA {ma_short} (Short)', 
                            line=dict(color='orange', width=2)))
    
    # Long MA
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_Long'], 
                            mode='lines', name=f'MA {ma_long} (Long)', 
                            line=dict(color='blue', width=2)))
    
    # Golden Cross markers
    golden_crosses = df[df['Golden_Cross'] == True]
    death_crosses = df[df['Death_Cross'] == True]
    
    fig.add_trace(go.Scatter(x=golden_crosses.index, y=golden_crosses['Close'],
                            mode='markers', name='Golden Cross (Buy Signal)',
                            marker=dict(color='green', size=12, symbol='triangle-up', 
                                       line=dict(color='darkgreen', width=2))))
    
    fig.add_trace(go.Scatter(x=death_crosses.index, y=death_crosses['Close'],
                            mode='markers', name='Death Cross (Sell Signal)',
                            marker=dict(color='red', size=12, symbol='triangle-down',
                                       line=dict(color='darkred', width=2))))
    
    # Highlight the crossover regions
    if len(golden_crosses) > 0:
        last_golden = golden_crosses.index[-1]
        fig.add_vline(x=last_golden, line_dash="dash", line_color="green",
                     annotation_text="Last Golden Cross", annotation_position="top left")
    
    if len(death_crosses) > 0:
        last_death = death_crosses.index[-1]
        fig.add_vline(x=last_death, line_dash="dash", line_color="red",
                     annotation_text="Last Death Cross", annotation_position="top right")
    
    fig.update_layout(title=f"{ticker} - Golden Cross vs Death Cross Analysis",
                     xaxis_title="Date",
                     yaxis_title="Price ($)",
                     height=500,
                     hovermode='x unified')
    
    return fig

def get_technical_signals(df, ticker, etf_info):
    """Generate trading signals based on technical indicators"""
    signals = {
        "buy_signals": [],
        "sell_signals": [],
        "neutral_signals": [],
        "overall": "",
        "confidence": 0,
        "summary": ""
    }
    
    # Golden Cross/Death Cross signals
    if df['Golden_Cross'].iloc[-1]:
        signals["buy_signals"].append({
            "indicator": "Golden Cross (Moving Average Crossover)",
            "signal": "BUY",
            "details": f"Short MA ({df['MA_Short'].iloc[-1]:.2f}) crossed above Long MA ({df['MA_Long'].iloc[-1]:.2f})",
            "strength": "Strong"
        })
    elif df['Death_Cross'].iloc[-1]:
        signals["sell_signals"].append({
            "indicator": "Death Cross (Moving Average Crossover)",
            "signal": "SELL",
            "details": f"Short MA ({df['MA_Short'].iloc[-1]:.2f}) crossed below Long MA ({df['MA_Long'].iloc[-1]:.2f})",
            "strength": "Strong"
        })
    
    # MACD signals
    if df['MACD'].iloc[-1] > df['Signal_Line'].iloc[-1] and df['MACD'].iloc[-2] <= df['Signal_Line'].iloc[-2]:
        signals["buy_signals"].append({
            "indicator": "MACD Bullish Crossover",
            "signal": "BUY",
            "details": "MACD line crossed above Signal line indicating upward momentum",
            "strength": "Moderate"
        })
    elif df['MACD'].iloc[-1] < df['Signal_Line'].iloc[-1] and df['MACD'].iloc[-2] >= df['Signal_Line'].iloc[-2]:
        signals["sell_signals"].append({
            "indicator": "MACD Bearish Crossover",
            "signal": "SELL",
            "details": "MACD line crossed below Signal line indicating downward momentum",
            "strength": "Moderate"
        })
    
    # MACD Histogram momentum
    if df['MACD_Histogram'].iloc[-1] > 0 and df['MACD_Histogram'].iloc[-1] > df['MACD_Histogram'].iloc[-2]:
        if df['MACD_Histogram'].iloc[-2] <= 0:
            signals["buy_signals"].append({
                "indicator": "MACD Histogram Turning Positive",
                "signal": "BUY",
                "details": "Histogram crossed above zero line indicating bullish momentum",
                "strength": "Moderate"
            })
        else:
            signals["buy_signals"].append({
                "indicator": "Increasing Bullish Momentum",
                "signal": "BULLISH",
                "details": "Histogram positive and increasing",
                "strength": "Weak"
            })
    elif df['MACD_Histogram'].iloc[-1] < 0 and df['MACD_Histogram'].iloc[-1] < df['MACD_Histogram'].iloc[-2]:
        if df['MACD_Histogram'].iloc[-2] >= 0:
            signals["sell_signals"].append({
                "indicator": "MACD Histogram Turning Negative",
                "signal": "SELL",
                "details": "Histogram crossed below zero line indicating bearish momentum",
                "strength": "Moderate"
            })
        else:
            signals["sell_signals"].append({
                "indicator": "Increasing Bearish Momentum",
                "signal": "BEARISH",
                "details": "Histogram negative and decreasing",
                "strength": "Weak"
            })
    
    # Current trend
    if df['MA_Short'].iloc[-1] > df['MA_Long'].iloc[-1]:
        signals["buy_signals"].append({
            "indicator": "Uptrend Confirmed",
            "signal": "BULLISH",
            "details": f"Short MA above Long MA by ${abs(df['MA_Short'].iloc[-1] - df['MA_Long'].iloc[-1]):.2f}",
            "strength": "Moderate"
        })
    else:
        signals["sell_signals"].append({
            "indicator": "Downtrend Confirmed",
            "signal": "BEARISH",
            "details": f"Short MA below Long MA by ${abs(df['MA_Short'].iloc[-1] - df['MA_Long'].iloc[-1]):.2f}",
            "strength": "Moderate"
        })
    
    # Calculate overall recommendation
    buy_count = len(signals["buy_signals"])
    sell_count = len(signals["sell_signals"])
    
    if buy_count > sell_count:
        signals["overall"] = "BUY"
        signals["confidence"] = (buy_count / (buy_count + sell_count)) * 100
        signals["summary"] = f"Based on {buy_count} bullish signals vs {sell_count} bearish signals, {ticker} shows positive technical momentum."
    elif sell_count > buy_count:
        signals["overall"] = "SELL"
        signals["confidence"] = (sell_count / (buy_count + sell_count)) * 100
        signals["summary"] = f"Based on {sell_count} bearish signals vs {buy_count} bullish signals, {ticker} shows negative technical momentum."
    else:
        signals["overall"] = "NEUTRAL"
        signals["confidence"] = 50
        signals["summary"] = f"Mixed signals detected for {ticker}. Consider waiting for clearer trend confirmation."
    
    return signals

def analyze_portfolio_securities(portfolio_details, risk_profile, investment_horizon):
    """Analyze all securities in the portfolio and provide recommendations"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    analysis_results = []
    
    with st.spinner("Analyzing portfolio securities..."):
        for security in portfolio_details:
            ticker = security['Ticker']
            st.write(f"📊 Analyzing {ticker} - {security['ETF Name']}...")
            
            # Fetch data
            data = fetch_stock_data(ticker, start_date, end_date)
            
            if data is not None and not data.empty:
                # Calculate indicators
                df_tech = calculate_technical_indicators(data)
                
                # Get signals
                signals = get_technical_signals(df_tech, ticker, security)
                
                # Store results
                analysis_results.append({
                    "Ticker": ticker,
                    "ETF Name": security['ETF Name'],
                    "Category": security['Category'],
                    "Allocation": security['Allocation %'],
                    "Current Price": df_tech['Close'].iloc[-1],
                    "MA_Short": df_tech['MA_Short'].iloc[-1],
                    "MA_Long": df_tech['MA_Long'].iloc[-1],
                    "Trend": df_tech['Trend'].iloc[-1],
                    "MACD": df_tech['MACD'].iloc[-1],
                    "Signal": df_tech['Signal_Line'].iloc[-1],
                    "Histogram": df_tech['MACD_Histogram'].iloc[-1],
                    "Overall_Signal": signals["overall"],
                    "Confidence": signals["confidence"],
                    "Summary": signals["summary"],
                    "Buy_Signals": len(signals["buy_signals"]),
                    "Sell_Signals": len(signals["sell_signals"]),
                    "Raw_Signals": signals
                })
            else:
                analysis_results.append({
                    "Ticker": ticker,
                    "ETF Name": security['ETF Name'],
                    "Category": security['Category'],
                    "Allocation": security['Allocation %'],
                    "Current Price": 0,
                    "MA_Short": 0,
                    "MA_Long": 0,
                    "Trend": "N/A",
                    "MACD": 0,
                    "Signal": 0,
                    "Histogram": 0,
                    "Overall_Signal": "N/A",
                    "Confidence": 0,
                    "Summary": f"Could not fetch data for {ticker}",
                    "Buy_Signals": 0,
                    "Sell_Signals": 0,
                    "Raw_Signals": None
                })
    
    return analysis_results

# ========== TECHNICAL ANALYSIS TAB ==========
def technical_analysis_tab(portfolio_details=None, risk_profile=None, investment_horizon=None):
    """Display Technical Analysis tab content integrated with portfolio"""
    st.header("📈 Technical Analysis - Portfolio Securities")
    st.caption("Analyze MACD and Golden/Death Cross signals for your portfolio holdings")
    st.write("---")
    
    if portfolio_details is None or len(portfolio_details) == 0:
        st.warning("⚠️ Please generate a portfolio first in the 'Portfolio Advisor' tab before using Technical Analysis.")
        st.info("Go to the Portfolio Advisor tab, complete the risk assessment, and generate your portfolio to see technical analysis here.")
        return
    
    # Display portfolio context
    with st.expander("📊 Current Portfolio Summary", expanded=True):
        st.write(f"**Risk Profile:** {risk_profile}")
        st.write(f"**Investment Horizon:** {investment_horizon} years")
        
        portfolio_df = pd.DataFrame(portfolio_details)
        display_cols = ['Ticker', 'ETF Name', 'Category', 'Allocation %', 'Amount ($)']
        st.dataframe(portfolio_df[display_cols], use_container_width=True, hide_index=True)
    
    st.write("---")
    
    # Analyze all securities
    st.subheader("🔍 Technical Analysis Results")
    st.write("Analyzing each security in your portfolio using MACD and Moving Average crossovers...")
    
    analysis_results = analyze_portfolio_securities(portfolio_details, risk_profile, investment_horizon)
    
    # Display summary table
    st.subheader("📊 Technical Analysis Summary Table")
    
    summary_df = pd.DataFrame([{
        'Ticker': r['Ticker'],
        'ETF Name': r['ETF Name'][:30] + '...' if len(r['ETF Name']) > 30 else r['ETF Name'],
        'Allocation %': f"{r['Allocation']:.0f}%",
        'Current Price': f"${r['Current Price']:.2f}" if r['Current Price'] > 0 else 'N/A',
        'Trend': r['Trend'],
        'Signal': r['Overall_Signal'],
        'Confidence': f"{r['Confidence']:.0f}%",
        'Buy Signals': r['Buy_Signals'],
        'Sell Signals': r['Sell_Signals']
    } for r in analysis_results])
    
    # Color code the Signal column
    def color_signal(val):
        if val == 'BUY':
            return 'background-color: #d4edda; color: #155724'
        elif val == 'SELL':
            return 'background-color: #f8d7da; color: #721c24'
        else:
            return 'background-color: #fff3cd; color: #856404'
    
    st.dataframe(summary_df.style.applymap(color_signal, subset=['Signal']), 
                use_container_width=True, hide_index=True)
    
    st.write("---")
    
    # Detailed analysis for each security
    st.subheader("📈 Detailed Security Analysis")
    
    for idx, result in enumerate(analysis_results):
        if result['Current Price'] > 0:
            with st.expander(f"🔍 {result['Ticker']} - {result['ETF Name']} ({result['Category']})", expanded=(idx==0)):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Current Price", f"${result['Current Price']:.2f}")
                    st.metric("Short MA (20)", f"${result['MA_Short']:.2f}")
                    st.metric("Trend", result['Trend'])
                
                with col2:
                    st.metric("Long MA (50)", f"${result['MA_Long']:.2f}")
                    ma_diff = result['MA_Short'] - result['MA_Long']
                    st.metric("MA Difference", f"${ma_diff:.2f}", 
                             delta="Bullish" if ma_diff > 0 else "Bearish")
                    st.metric("MACD", f"{result['MACD']:.4f}")
                
                with col3:
                    st.metric("Signal Line", f"{result['Signal']:.4f}")
                    st.metric("Histogram", f"{result['Histogram']:.4f}")
                    st.metric("Overall Signal", result['Overall_Signal'])
                
                st.write("---")
                
                # Fetch data for charts
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                data = fetch_stock_data(result['Ticker'], start_date, end_date)
                
                if data is not None:
                    df_tech = calculate_technical_indicators(data)
                    
                    # Display MACD Plot
                    st.subheader(f"📊 MACD Analysis - {result['Ticker']}")
                    macd_fig = plot_macd_analysis(df_tech, result['Ticker'], 12, 26, 9)
                    st.plotly_chart(macd_fig, use_container_width=True)
                    
                    # Display Golden/Death Cross Plot
                    st.subheader(f"🟡 Golden Cross vs Death Cross - {result['Ticker']}")
                    cross_fig = plot_golden_death_cross(df_tech, result['Ticker'], 20, 50)
                    st.plotly_chart(cross_fig, use_container_width=True)
                    
                    # Display signals
                    st.subheader("📋 Technical Signals")
                    
                    if result['Raw_Signals']:
                        signals = result['Raw_Signals']
                        
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if signals['buy_signals']:
                                st.markdown("**🟢 Buy/Bullish Signals**")
                                for signal in signals['buy_signals']:
                                    st.markdown(f"""
                                    <div class="buy-signal">
                                        <strong>{signal['indicator']}</strong><br>
                                        {signal['details']}<br>
                                        <small>Strength: {signal['strength']}</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    st.write("")
                        
                        with col_b:
                            if signals['sell_signals']:
                                st.markdown("**🔴 Sell/Bearish Signals**")
                                for signal in signals['sell_signals']:
                                    st.markdown(f"""
                                    <div class="sell-signal">
                                        <strong>{signal['indicator']}</strong><br>
                                        {signal['details']}<br>
                                        <small>Strength: {signal['strength']}</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    st.write("")
                        
                        if not signals['buy_signals'] and not signals['sell_signals']:
                            st.markdown("""
                            <div class="neutral-signal">
                                <strong>No Strong Signals Detected</strong><br>
                                The security is showing neutral technical patterns.
                            </div>
                            """, unsafe_allow_html=True)
                
                st.write("---")
    
    # Portfolio-wide technical conclusion
    st.write("---")
    st.subheader("🎯 Portfolio-Wide Technical Conclusion")
    
    # Aggregate signals
    buy_count = sum(1 for r in analysis_results if r['Overall_Signal'] == 'BUY')
    sell_count = sum(1 for r in analysis_results if r['Overall_Signal'] == 'SELL')
    neutral_count = sum(1 for r in analysis_results if r['Overall_Signal'] == 'NEUTRAL')
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("BUY Signals", buy_count)
    with col2:
        st.metric("SELL Signals", sell_count)
    with col3:
        st.metric("NEUTRAL", neutral_count)
    with col4:
        total_weighted_score = sum(
            (r['Allocation'] / 100) * (1 if r['Overall_Signal'] == 'BUY' else -1 if r['Overall_Signal'] == 'SELL' else 0)
            for r in analysis_results
        )
        st.metric("Weighted Sentiment", f"{total_weighted_score:.2f}", 
                 delta="Bullish" if total_weighted_score > 0 else "Bearish" if total_weighted_score < 0 else "Neutral")
    
    st.write("---")
    
    # Generate comprehensive conclusion
    st.subheader("📝 Technical Analysis Conclusion")
    
    if buy_count > sell_count:
        st.success(f"""
        ### ✅ Overall Technical Outlook: BULLISH
        
        **Summary:**
        - {buy_count} securities showing BUY signals
        - {sell_count} securities showing SELL signals  
        - {neutral_count} securities showing NEUTRAL signals
        
        **Recommendation:**
        Given your {risk_profile} risk profile and {investment_horizon}-year investment horizon, the current technical setup suggests favorable entry points for most portfolio holdings. Consider:
        - ✅ Maintaining or increasing exposure to securities with BUY signals
        - ⚠️ Monitoring securities with SELL signals for potential weakness
        - 📊 Rebalancing quarterly to capture technical momentum
        
        **Risk Consideration:** While technicals are bullish, maintain your strategic allocation based on your risk profile.
        """)
    elif sell_count > buy_count:
        st.error(f"""
        ### ❌ Overall Technical Outlook: BEARISH
        
        **Summary:**
        - {sell_count} securities showing SELL signals        - {buy_count} securities showing BUY signals
        - {neutral_count} securities showing NEUTRAL signals
        
        **Recommendation:**
        The technical indicators suggest caution for your {risk_profile} portfolio. Consider:
        - 🔄 Reducing exposure to securities with strong SELL signals
        - 💰 Increasing cash/bond allocation temporarily
        - 📉 Implementing stop-losses at support levels
        - ⏰ Waiting for trend reversal before increasing equity exposure
        
        **For your {investment_horizon}-year horizon:** Consider dollar-cost averaging new investments to reduce timing risk.
        """)
    else:
        st.warning(f"""
        ### ⚖️ Overall Technical Outlook: NEUTRAL/MIXED
        
        **Summary:**
        - {neutral_count} securities showing NEUTRAL signals
        - {buy_count} securities showing BUY signals
        - {sell_count} securities showing SELL signals
        
        **Recommendation:**
        Technical signals are mixed for your {risk_profile} portfolio. Best approach:
        - ✅ Maintain current strategic allocation
        - 📊 Focus on fundamental analysis for individual securities
        - 🔍 Watch for clearer technical confirmation in coming weeks
        - 💡 Consider increasing quality/defensive positions
        
        **For your {investment_horizon}-year horizon:** Stay disciplined with your investment plan and rebalance according to your target allocation.
        """)
    
    st.write("---")
    
    # Actionable recommendations
    st.subheader("🎯 Actionable Recommendations")
    
    col_rec1, col_rec2 = st.columns(2)
    
    with col_rec1:
        st.markdown("**✅ Consider Increasing (BUY signals):**")
        buy_securities = [r for r in analysis_results if r['Overall_Signal'] == 'BUY']
        if buy_securities:
            for sec in buy_securities:
                st.write(f"- **{sec['Ticker']}** ({sec['ETF Name']}) - Confidence: {sec['Confidence']:.0f}%")
        else:
            st.write("- No strong BUY signals at this time")
    
    with col_rec2:
        st.markdown("**⚠️ Consider Reducing/Reviewing (SELL signals):**")
        sell_securities = [r for r in analysis_results if r['Overall_Signal'] == 'SELL']
        if sell_securities:
            for sec in sell_securities:
                st.write(f"- **{sec['Ticker']}** ({sec['ETF Name']}) - Confidence: {sec['Confidence']:.0f}%")
        else:
            st.write("- No strong SELL signals at this time")
    
    st.write("---")
    st.info("💡 **Technical Analysis Note:** Technical indicators are most effective when used alongside fundamental analysis and your long-term investment strategy. For your risk profile, consider rebalancing quarterly rather than reacting to short-term signals.")

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
    
    # Tab 2: Technical Analysis (Integrated with Portfolio)
    with tab2:
        if st.session_state.portfolio_generated:
            technical_analysis_tab(
                portfolio_details=st.session_state.portfolio_details,
                risk_profile=st.session_state.risk_profile,
                investment_horizon=st.session_state.investment_years
            )
        else:
            st.warning("⚠️ Please generate a portfolio first in the 'Portfolio Advisor' tab.")
            st.info("""
            ### How to use Technical Analysis:
            1. Go to the **Portfolio Advisor** tab
            2. Complete the risk assessment questions
            3. Click 'Generate Portfolio'
            4. Return to this tab to see technical analysis for your portfolio holdings
            
            The Technical Analysis will automatically analyze all securities in your portfolio using:
            - 📊 MACD (Moving Average Convergence Divergence)
            - 🟡 Golden Cross (Short MA crossing above Long MA)
            - 🔴 Death Cross (Short MA crossing below Long MA)
            - 📈 Trend analysis and momentum indicators
            """)
            
            # Show example preview
            with st.expander("📊 Preview: What Technical Analysis Looks Like", expanded=True):
                st.write("""
                **Once you generate a portfolio, you'll see:**
                
                1. **Summary Table** - Overview of all securities with their technical signals
                2. **Detailed Analysis** - For each security:
                   - MACD chart with signal line and histogram
                   - Golden Cross vs Death Cross visualization
                   - Buy/Sell signals with confidence levels
                3. **Portfolio Conclusion** - Aggregated technical outlook
                4. **Actionable Recommendations** - Which securities to consider increasing or reducing
                
                **Example Signal Interpretation:**
                - 🟢 **Golden Cross** = Bullish - Short MA crosses above Long MA
                - 🔴 **Death Cross** = Bearish - Short MA crosses below Long MA
                - 📈 **MACD Bullish** = MACD line crosses above Signal line
                - 📉 **MACD Bearish** = MACD line crosses below Signal line
                """)
    
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
                """)
            
            with st.expander("🟡 Golden Cross vs Death Cross"):
                st.write("""
                **Golden Cross (Bullish):**
                - 50-day MA crosses ABOVE 200-day MA
                - Indicates long-term bullish reversal
                - Historically leads to significant uptrends
                
                **Death Cross (Bearish):**
                - 50-day MA crosses BELOW 200-day MA
                - Indicates long-term bearish reversal
                - Often precedes market corrections
                
                **For portfolio management:** Use crossovers to adjust exposure to different asset classes.
                """)
        
        with col2:
            with st.expander("📊 How to Use Technical Analysis in Portfolio Management"):
                st.write("""
                **Integration with Robo-Advisor:**
                
                1. **Risk Profile Alignment**
                   - Conservative: Focus on securities with bullish trends
                   - Aggressive: Can tolerate more bearish signals for potential reversals
                
                2. **Rebalancing Triggers**
                   - Use Death Cross to reduce overweight positions
                   - Use Golden Cross to add to underweight positions
                
                3. **Timing Contributions**
                   - Add new money during Golden Cross signals
                   - Pause contributions during Death Cross signals
                
                4. **Risk Management**
                   - Set stop-losses at recent support levels
                   - Take profits when MACD histogram shows extreme readings
                """)
            
            with st.expander("⚠️ Limitations of Technical Analysis"):
                st.write("""
                **Important Caveats:**
                - Not 100% accurate - false signals occur
                - Works best in trending markets, not sideways
                - Should complement fundamental analysis
                - Past patterns don't guarantee future results
                - Best for short to medium-term decisions
                - For long-term investing, focus more on fundamentals
                
                **Our Recommendation:**
                Use technical analysis for:
                - Timing new investments
                - Rebalancing decisions
                - Short-term tactical adjustments
                
                Maintain strategic allocation based on your risk profile for long-term success.
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
        st.info("💡 **Pro Tip:** Combine technical analysis with fundamental research. Use technicals for timing and fundamentals for selection.")

# ========== RUN APPLICATION ==========
if __name__ == "__main__":
    main()
