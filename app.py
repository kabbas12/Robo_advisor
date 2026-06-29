"""
AI Robo-Advisor for FinTech Thesis
With Professional Dashboard, Banking Analytics & Integrated Technical Analysis
Author: Syed Kamran Abbas 
"""

# ========== IMPORT LIBRARIES ==========
# Import core libraries for data manipulation and visualization
import streamlit as st  # Web application framework for building interactive dashboards
import pandas as pd  # Data manipulation and analysis library
import numpy as np  # Numerical computing library for array operations
import plotly.express as px  # High-level plotting library for interactive charts
import plotly.graph_objects as go  # Low-level plotting library for custom visualizations
from plotly.subplots import make_subplots  # Creates multiple subplots in one figure
from datetime import datetime, timedelta  # Date and time handling for data queries
import yfinance as yf  # Yahoo Finance API wrapper for market data retrieval
import warnings  # Controls warning messages from libraries
warnings.filterwarnings('ignore')  # Suppress non-critical warnings for cleaner output

# ========== PAGE CONFIGURATION ==========
# Configure Streamlit page settings: title, icon, layout, and sidebar state
st.set_page_config(
    page_title="AI Robo-Advisor - Professional Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS FOR DASHBOARD ==========
# Apply custom styling for dashboard components, cards, and signal indicators
st.markdown("""
<style>
    /* Card styling for metric displays */
    .dashboard-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 4px solid #2E86AB;
        margin: 10px 0;
    }
    /* Large font for metric values */
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #2E86AB;
    }
    /* Label styling for metrics */
    .metric-label {
        font-size: 14px;
        color: #666;
    }
    /* Buy signal styling (green) */
    .buy-signal {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 5px 0;
    }
    /* Sell signal styling (red) */
    .sell-signal {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        margin: 5px 0;
    }
    /* Neutral signal styling (yellow) */
    .neutral-signal {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
        margin: 5px 0;
    }
    /* Golden cross event styling */
    .golden-cross {
        background-color: #d4edda;
        padding: 8px;
        border-radius: 5px;
        text-align: center;
    }
    /* Death cross event styling */
    .death-cross {
        background-color: #f8d7da;
        padding: 8px;
        border-radius: 5px;
        text-align: center;
    }
    /* Strong buy recommendation card */
    .strong-buy {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    /* Strong sell recommendation card */
    .strong-sell {
        background: linear-gradient(135deg, #dc3545, #e74c3c);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    /* Portfolio score display */
    .portfolio-score {
        background: linear-gradient(135deg, #2E86AB, #3498db);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== ETF DATABASE WITH REAL NAMES ==========
# Comprehensive database of ETFs with their characteristics for portfolio construction
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
# Calculates investor risk profile based on questionnaire responses
def calculate_risk_profile(answers):
    """Calculate risk profile (Conservative/Moderate/Aggressive) based on 5-question assessment"""
    total_score = sum(answers)  # Sum of all question scores (each 1-5)
    
    # Categorize based on total score thresholds
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
# Builds optimized ETF portfolio based on risk profile and investment amount
def get_portfolio_allocation(risk_profile, total_amount):
    """Construct portfolio with ETF allocations based on risk profile"""
    # Pre-defined portfolios for each risk level with expected returns and risk metrics
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
    
    allocation_data = portfolios[risk_profile]  # Get allocation for selected risk profile
    
    # Build detailed portfolio with ETF information
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
# Performs Monte Carlo simulation to project portfolio outcomes
def run_monte_carlo(initial_amount, years, expected_return, volatility, n_sims=5000):
    """Run Monte Carlo simulation to project portfolio values"""
    # Convert annual returns to daily parameters (252 trading days per year)
    daily_return = expected_return / 252
    daily_vol = volatility / np.sqrt(252)
    
    trading_days = years * 252
    np.random.seed(42)  # Set seed for reproducibility
    
    # Generate random daily returns for each simulation
    random_returns = np.random.normal(daily_return, daily_vol, (trading_days, n_sims))
    # Calculate cumulative returns over the period
    cumulative_returns = np.cumprod(1 + random_returns, axis=0)
    # Project portfolio values
    portfolio_values = initial_amount * cumulative_returns
    
    final_values = portfolio_values[-1, :]  # Extract final values from all simulations
    
    # Calculate statistical metrics
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
# Functions for MACD, Golden Cross, and Death Cross technical analysis

@st.cache_data(ttl=3600)
def fetch_stock_data(ticker, start_date, end_date):
    """Fetch historical stock data from Yahoo Finance with caching"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date)
        if data.empty:
            return None
        return data
    except Exception as e:
        return None

def calculate_technical_indicators(data, ma_short=20, ma_long=50, macd_fast=12, macd_slow=26, macd_signal=9):
    """Calculate MACD and Golden Cross technical indicators"""
    df = data.copy()
    
    # Moving averages for Golden Cross detection
    df['MA_Short'] = df['Close'].rolling(window=ma_short).mean()
    df['MA_Long'] = df['Close'].rolling(window=ma_long).mean()
    
    # MACD calculation using Exponential Moving Averages
    df['EMA_Fast'] = df['Close'].ewm(span=macd_fast, adjust=False).mean()
    df['EMA_Slow'] = df['Close'].ewm(span=macd_slow, adjust=False).mean()
    df['MACD'] = df['EMA_Fast'] - df['EMA_Slow']  # MACD line
    df['Signal_Line'] = df['MACD'].ewm(span=macd_signal, adjust=False).mean()  # Signal line
    df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']  # Histogram
    
    # Golden Cross signals (short MA crosses above long MA)
    df['Golden_Cross'] = (df['MA_Short'] > df['MA_Long']) & (df['MA_Short'].shift(1) <= df['MA_Long'].shift(1))
    # Death Cross signals (short MA crosses below long MA)
    df['Death_Cross'] = (df['MA_Short'] < df['MA_Long']) & (df['MA_Short'].shift(1) >= df['MA_Long'].shift(1))
    
    # Current trend based on MA relationship
    df['Trend'] = 'Bullish' if df['MA_Short'].iloc[-1] > df['MA_Long'].iloc[-1] else 'Bearish'
    
    # MACD Crossover signals
    df['MACD_Bullish_Cross'] = (df['MACD'] > df['Signal_Line']) & (df['MACD'].shift(1) <= df['Signal_Line'].shift(1))
    df['MACD_Bearish_Cross'] = (df['MACD'] < df['Signal_Line']) & (df['MACD'].shift(1) >= df['Signal_Line'].shift(1))
    
    return df

def calculate_macd_table(df):
    """Create table of recent MACD values for display"""
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
    """Create table of Golden Cross and Death Cross events"""
    # Filter crossover events
    golden_crosses = df[df['Golden_Cross'] == True]
    death_crosses = df[df['Death_Cross'] == True]
    
    cross_data = []
    
    # Format Golden Cross events
    for idx in golden_crosses.index:
        cross_data.append({
            'Date': idx.strftime('%Y-%m-%d'),
            'Type': '🟢 Golden Cross (BUY)',
            'Short MA': round(golden_crosses.loc[idx, 'MA_Short'], 2),
            'Long MA': round(golden_crosses.loc[idx, 'MA_Long'], 2),
            'Price at Signal': round(golden_crosses.loc[idx, 'Close'], 2),
            'Signal Strength': 'Strong Bullish'
        })
    
    # Format Death Cross events
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
    """Create interactive MACD chart with price and indicator"""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.08, 
                        row_heights=[0.5, 0.5],
                        subplot_titles=(f"{ticker} - Price Chart", "MACD Indicator"))
    
    # Price chart (top subplot)
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], 
                            mode='lines', name='Close Price', 
                            line=dict(color='black', width=1.5)), row=1, col=1)
    
    # MACD line and Signal line (bottom subplot)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], 
                            mode='lines', name='MACD Line', 
                            line=dict(color='blue', width=2)), row=2, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal_Line'], 
                            mode='lines', name='Signal Line', 
                            line=dict(color='red', width=2)), row=2, col=1)
    
    # MACD Histogram bars
    colors = ['green' if val >= 0 else 'red' for val in df['MACD_Histogram']]
    fig.add_trace(go.Bar(x=df.index, y=df['MACD_Histogram'], 
                        name='MACD Histogram', marker_color=colors), row=2, col=1)
    
    # Mark crossover points
    bullish_cross = df[df['MACD_Bullish_Cross'] == True]
    bearish_cross = df[df['MACD_Bearish_Cross'] == True]
    
    fig.add_trace(go.Scatter(x=bullish_cross.index, y=bullish_cross['MACD'],
                            mode='markers', name='Bullish Crossover',
                            marker=dict(color='green', size=10, symbol='triangle-up')), row=2, col=1)
    
    fig.add_trace(go.Scatter(x=bearish_cross.index, y=bearish_cross['MACD'],
                            mode='markers', name='Bearish Crossover',
                            marker=dict(color='red', size=10, symbol='triangle-down')), row=2, col=1)
    
    # Add zero reference line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
    
    fig.update_layout(title=f"{ticker} - MACD Analysis",
                     height=600,
                     showlegend=True,
                     xaxis_title="Date")
    
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="MACD Value", row=2, col=1)
    
    return fig

def plot_golden_death_cross_graph(df, ticker):
    """Create interactive Golden Cross vs Death Cross chart"""
    fig = go.Figure()
    
    # Price line (dotted for reference)
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], 
                            mode='lines', name='Close Price', 
                            line=dict(color='gray', width=1, dash='dot')))
    
    # Short-term Moving Average (20-day)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_Short'], 
                            mode='lines', name=f'MA 20 (Short)', 
                            line=dict(color='orange', width=2)))
    
    # Long-term Moving Average (50-day)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_Long'], 
                            mode='lines', name=f'MA 50 (Long)', 
                            line=dict(color='blue', width=2)))
    
    # Mark Golden Cross events
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
    
    # Highlight bullish periods with shaded area
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
    """Extract MACD summary metrics for current period"""
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
    """Extract Golden/Death Cross summary metrics"""
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

def analyze_portfolio_securities(portfolio_details, risk_profile, investment_horizon):
    """Analyze all securities in portfolio using technical indicators"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 1 year of historical data
    
    analysis_results = []
    
    with st.spinner("Analyzing portfolio securities..."):
        for security in portfolio_details:
            ticker = security['Ticker']
            
            # Fetch historical data
            data = fetch_stock_data(ticker, start_date, end_date)
            
            if data is not None and not data.empty:
                # Calculate technical indicators
                df_tech = calculate_technical_indicators(data)
                
                # Extract summary metrics
                macd_summary = get_macd_analysis_summary(df_tech)
                cross_summary = get_cross_analysis_summary(df_tech)
                macd_table = calculate_macd_table(df_tech)
                cross_table = calculate_cross_table(df_tech)
                
                # Store comprehensive analysis results
                analysis_results.append({
                    "Ticker": ticker,
                    "ETF Name": security['ETF Name'],
                    "Category": security['Category'],
                    "Allocation": security['Allocation %'],
                    "Current Price": df_tech['Close'].iloc[-1],
                    "MA_Short": df_tech['MA_Short'].iloc[-1],
                    "MA_Long": df_tech['MA_Long'].iloc[-1],
                    "Trend": df_tech['Trend'].iloc[-1],
                    "MACD_Value": macd_summary['macd_value'],
                    "Signal_Line": macd_summary['signal_value'],
                    "MACD_Histogram": macd_summary['histogram'],
                    "MACD_Status": macd_summary['status'],
                    "MACD_Hist_Trend": macd_summary['histogram_trend'],
                    "Cross_Status": cross_summary['relationship'],
                    "Cross_Diff": cross_summary['difference'],
                    "Total_Golden": cross_summary['total_golden'],
                    "Total_Death": cross_summary['total_death'],
                    "MACD_Table": macd_table,
                    "Cross_Table": cross_table,
                    "DF_Data": df_tech
                })
            else:
                # Handle data fetch failure
                analysis_results.append({
                    "Ticker": ticker,
                    "ETF Name": security['ETF Name'],
                    "Category": security['Category'],
                    "Allocation": security['Allocation %'],
                    "Current Price": 0,
                    "MA_Short": 0,
                    "MA_Long": 0,
                    "Trend": "N/A",
                    "MACD_Value": 0,
                    "Signal_Line": 0,
                    "MACD_Histogram": 0,
                    "MACD_Status": "N/A",
                    "MACD_Hist_Trend": "N/A",
                    "Cross_Status": "N/A",
                    "Cross_Diff": 0,
                    "Total_Golden": 0,
                    "Total_Death": 0,
                    "MACD_Table": pd.DataFrame(),
                    "Cross_Table": pd.DataFrame(),
                    "DF_Data": None
                })
    
    return analysis_results

# ========== ENHANCED TECHNICAL ANALYSIS WITH INDIVIDUAL SECURITY FOCUS ==========
def technical_analysis_tab(portfolio_details=None, risk_profile=None, investment_horizon=None):
    """Display comprehensive Technical Analysis tab with individual security focus"""
    st.header("📈 Technical Analysis - Portfolio Securities")
    st.caption("Complete MACD and Golden/Death Cross analysis with calculations, tables, and graphs")
    st.write("---")
    
    # Validate portfolio exists
    if portfolio_details is None or len(portfolio_details) == 0:
        st.warning("⚠️ Please generate a portfolio first in the 'Portfolio Advisor' tab before using Technical Analysis.")
        st.info("Go to the Portfolio Advisor tab, complete the risk assessment, and generate your portfolio to see technical analysis here.")
        return
    
    # Display current portfolio summary
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
    
    # Display Summary Table
    st.subheader("📊 Technical Analysis Summary Table")
    
    summary_df = pd.DataFrame([{
        'Ticker': r['Ticker'],
        'ETF Name': r['ETF Name'][:25] + '...' if len(r['ETF Name']) > 25 else r['ETF Name'],
        'Allocation %': f"{r['Allocation']:.0f}%",
        'Price': f"${r['Current Price']:.2f}" if r['Current Price'] > 0 else 'N/A',
        'Trend': r['Trend'],
        'MACD Status': r['MACD_Status'],
        'Cross Status': '🟢 Golden' if 'Bullish' in r['Cross_Status'] else '🔴 Death' if 'Bearish' in r['Cross_Status'] else 'Neutral',
        'Golden Crosses': r['Total_Golden'],
        'Death Crosses': r['Total_Death'],
        'Recommendation': get_individual_recommendation(r)
    } for r in analysis_results])
    
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    st.write("---")
    
    # Individual Security Analysis Section
    st.subheader("🔍 Individual Security Analysis")
    st.write("Select a security from your portfolio for detailed technical analysis:")
    
    # Create dropdown for security selection
    security_options = [f"{r['Ticker']} - {r['ETF Name'][:30]}" for r in analysis_results]
    selected_security = st.selectbox("Choose Security:", security_options, index=0)
    
    # Get selected security index
    selected_idx = security_options.index(selected_security)
    result = analysis_results[selected_idx]
    
    if result['Current Price'] > 0:
        # Display detailed individual analysis
        display_individual_security_analysis(result, risk_profile)
    else:
        st.error(f"❌ Could not fetch data for {result['Ticker']}. Please try again later.")
    
    st.write("---")
    
    # Portfolio-Wide Analysis
    st.subheader("🎯 Portfolio-Wide Technical Conclusion")
    
    # Aggregate signals across portfolio
    buy_count = sum(1 for r in analysis_results if r['MACD_Status'] == "Bullish" and "Bullish" in r['Cross_Status'])
    sell_count = sum(1 for r in analysis_results if r['MACD_Status'] == "Bearish" and "Bearish" in r['Cross_Status'])
    mixed_count = len(analysis_results) - buy_count - sell_count
    
    # Display aggregated metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Strong BUY Signals", buy_count)
    with col2:
        st
