"""
AI Robo-Advisor for FinTech Thesis
Author: Syed Kamran Abbas 
"""

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
import gc  # Garbage collection

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="AI Robo-Advisor - Professional Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== MEMORY OPTIMIZATION ==========
# Limit data size
pd.options.display.max_rows = 100
pd.options.display.max_colwidth = 50

# Reduce numpy precision for memory savings
np.set_printoptions(precision=4, suppress=True)

# ========== CUSTOM CSS ==========
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
    .strong-buy {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .strong-sell {
        background: linear-gradient(135deg, #dc3545, #e74c3c);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== ETF DATABASE ==========
ETF_DATABASE = {
    "BND": {"name": "Vanguard Total Bond Market ETF", "category": "Bonds", "expense_ratio": 0.03, "dividend_yield": 3.2},
    "VTI": {"name": "Vanguard Total Stock Market ETF", "category": "US Stocks", "expense_ratio": 0.03, "dividend_yield": 1.4},
    "VXUS": {"name": "Vanguard Total International Stock ETF", "category": "International Stocks", "expense_ratio": 0.07, "dividend_yield": 2.9},
    "QQQ": {"name": "Invesco QQQ Trust", "category": "Growth Stocks", "expense_ratio": 0.20, "dividend_yield": 0.6},
    "SHY": {"name": "iShares 1-3 Year Treasury Bond ETF", "category": "Short-term Bonds", "expense_ratio": 0.15, "dividend_yield": 4.1},
    "SPY": {"name": "SPDR S&P 500 ETF Trust", "category": "US Large Cap", "expense_ratio": 0.09, "dividend_yield": 1.3},
    "TLT": {"name": "iShares 20+ Year Treasury Bond ETF", "category": "Long-term Bonds", "expense_ratio": 0.15, "dividend_yield": 3.8},
    "GLD": {"name": "SPDR Gold Shares", "category": "Commodities", "expense_ratio": 0.40, "dividend_yield": 0.0},
    "IWM": {"name": "iShares Russell 2000 ETF", "category": "Small Cap Stocks", "expense_ratio": 0.19, "dividend_yield": 1.2},
    "EFA": {"name": "iShares MSCI EAFE ETF", "category": "Developed International", "expense_ratio": 0.33, "dividend_yield": 2.8}
}

# ========== RISK PROFILING ==========
def calculate_risk_profile(answers):
    total_score = sum(answers)
    if total_score <= 12:
        return {"profile": "Conservative", "score": total_score, "risk_tolerance": "Low"}
    elif total_score <= 20:
        return {"profile": "Moderate", "score": total_score, "risk_tolerance": "Medium"}
    else:
        return {"profile": "Aggressive", "score": total_score, "risk_tolerance": "High"}

# ========== PORTFOLIO CONSTRUCTION ==========
def get_portfolio_allocation(risk_profile, total_amount):
    portfolios = {
        "Conservative": {
            "allocation": {"BND": 0.35, "SHY": 0.25, "VTI": 0.15, "VXUS": 0.10, "GLD": 0.05, "TLT": 0.10},
            "expected_return": 0.05,
            "expected_volatility": 0.07,
            "sharpe_ratio": 0.71,
            "max_drawdown": -0.10
        },
        "Moderate": {
            "allocation": {"BND": 0.15, "VTI": 0.35, "VXUS": 0.20, "QQQ": 0.10, "SPY": 0.10, "IWM": 0.10},
            "expected_return": 0.08,
            "expected_volatility": 0.12,
            "sharpe_ratio": 0.67,
            "max_drawdown": -0.25
        },
        "Aggressive": {
            "allocation": {"VTI": 0.30, "QQQ": 0.20, "VXUS": 0.15, "SPY": 0.15, "IWM": 0.15, "BND": 0.05},
            "expected_return": 0.11,
            "expected_volatility": 0.18,
            "sharpe_ratio": 0.61,
            "max_drawdown": -0.35
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
            "Allocation %": weight * 100,
            "Amount ($)": total_amount * weight,
            "Expense Ratio": etf_info.get("expense_ratio", 0.10),
            "Dividend Yield": etf_info.get("dividend_yield", 0)
        })
    
    return portfolio_details, allocation_data

# ========== MONTE CARLO SIMULATION (OPTIMIZED) ==========
def run_monte_carlo(initial_amount, years, expected_return, volatility, n_sims=500):
    """Optimized Monte Carlo with reduced simulations for memory"""
    daily_return = expected_return / 252
    daily_vol = volatility / np.sqrt(252)
    trading_days = years * 252
    
    np.random.seed(42)
    
    # Use float32 for memory efficiency
    random_returns = np.random.normal(daily_return, daily_vol, (trading_days, n_sims)).astype(np.float32)
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
        "std_dev": np.std(final_values)
    }
    
    # Clean up memory
    del random_returns
    gc.collect()
    
    return portfolio_values, stats

# ========== TECHNICAL ANALYSIS (CACHED) ==========
@st.cache_data(ttl=3600, max_entries=10)
def fetch_stock_data(ticker, start_date, end_date):
    """Fetch stock data from Yahoo Finance with caching"""
    try:
        stock = yf.Ticker(ticker)
        # Limit data to last 6 months for performance
        data = stock.history(start=start_date, end=end_date, period="6mo")
        if data.empty:
            return None
        return data
    except Exception:
        return None

def calculate_technical_indicators(data, ma_short=20, ma_long=50):
    """Simplified technical indicators"""
    if len(data) < ma_long:
        return None
    
    df = data.copy()
    
    # Moving averages
    df['MA_Short'] = df['Close'].rolling(window=ma_short, min_periods=1).mean()
    df['MA_Long'] = df['Close'].rolling(window=ma_long, min_periods=1).mean()
    
    # Simplified MACD
    df['EMA_Fast'] = df['Close'].ewm(span=12, adjust=False, min_periods=1).mean()
    df['EMA_Slow'] = df['Close'].ewm(span=26, adjust=False, min_periods=1).mean()
    df['MACD'] = df['EMA_Fast'] - df['EMA_Slow']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False, min_periods=1).mean()
    df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']
    
    # Cross signals
    df['Golden_Cross'] = (df['MA_Short'] > df['MA_Long']) & (df['MA_Short'].shift(1) <= df['MA_Long'].shift(1))
    df['Death_Cross'] = (df['MA_Short'] < df['MA_Long']) & (df['MA_Short'].shift(1) >= df['MA_Long'].shift(1))
    df['Trend'] = 'Bullish' if df['MA_Short'].iloc[-1] > df['MA_Long'].iloc[-1] else 'Bearish'
    
    return df

# ========== DASHBOARD ==========
def create_dashboard(portfolio_details, allocation_data, sim_stats, initial_amount, investment_years):
    st.header("📊 Investment Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Portfolio Value (Median)", f"${sim_stats['median']:,.0f}")
    with col2:
        total_return = (sim_stats['median'] - initial_amount) / initial_amount * 100
        st.metric("Expected Return", f"{total_return:.1f}%")
    with col3:
        cagr = ((sim_stats['median'] / initial_amount) ** (1/investment_years) - 1) * 100
        st.metric("CAGR (Annualized)", f"{cagr:.1f}%")
    with col4:
        st.metric("Risk of Loss", f"{sim_stats['probability_of_loss']:.1f}%")

# ========== MAIN APPLICATION ==========
def main():
    st.title("🤖 AI Robo-Advisor")
    st.caption("Professional Portfolio Construction with Analytics")
    st.write("---")
    
    # Initialize session state
    if 'portfolio_generated' not in st.session_state:
        st.session_state.portfolio_generated = False
        st.session_state.portfolio_details = None
        st.session_state.risk_profile = None
    
    # Tabs
    tab1, tab2 = st.tabs(["📊 Portfolio Advisor", "📚 Education"])
    
    with tab1:
        with st.sidebar:
            st.header("📋 Risk Assessment")
            
            q1 = st.slider("Investment Time Horizon", 1, 30, 10)
            q1_score = min(5, q1 // 6 + 1)
            
            q2 = st.select_slider(
                "Reaction to Market Drop",
                options=["Sell everything", "Get nervous", "Do nothing", "Buy more", "Aggressively buy more"],
                value="Do nothing"
            )
            q2_scores = {"Sell everything": 1, "Get nervous": 2, "Do nothing": 3, "Buy more": 4, "Aggressively buy more": 5}
            q2_score = q2_scores[q2]
            
            q3 = st.radio(
                "Primary Investment Goal",
                ["Capital preservation", "Income generation", "Balanced growth", "Long-term wealth", "Maximum growth"],
                index=2
            )
            q3_scores = {"Capital preservation": 1, "Income generation": 2, "Balanced growth": 3, "Long-term wealth": 4, "Maximum growth": 5}
            q3_score = q3_scores[q3]
            
            q4 = st.slider("Risk Capacity (% of savings)", 0, 100, 50)
            q4_score = min(5, q4 // 20 + 1)
            
            q5 = st.select_slider(
                "Expected Annual Return",
                options=["3-4% (Very safe)", "5-6% (Conservative)", "7-8% (Moderate)", "9-10% (Growth)", "11%+ (Aggressive)"],
                value="7-8% (Moderate)"
            )
            q5_scores = {"3-4% (Very safe)": 1, "5-6% (Conservative)": 2, "7-8% (Moderate)": 3, "9-10% (Growth)": 4, "11%+ (Aggressive)": 5}
            q5_score = q5_scores[q5]
            
            st.write("---")
            st.header("💰 Investment Details")
            
            initial_amount = st.number_input("Investment Amount ($)", 1000, 1000000, 10000, 1000)
            investment_years = st.slider("Investment Period (Years)", 1, 30, 10)
            show_dashboard = st.checkbox("Show Dashboard", True)
            
            submit = st.button("Generate Portfolio", type="primary", use_container_width=True)
        
        if submit:
            answers = [q1_score, q2_score, q3_score, q4_score, q5_score]
            risk_result = calculate_risk_profile(answers)
            risk_profile = risk_result["profile"]
            
            st.session_state.portfolio_generated = True
            st.session_state.risk_profile = risk_profile
            
            portfolio_details, allocation_data = get_portfolio_allocation(risk_profile, initial_amount)
            st.session_state.portfolio_details = portfolio_details
            
            st.success(f"✅ Your Risk Profile: **{risk_profile}** | Score: {risk_result['score']}/25")
            
            st.header("📊 Your Personalized Portfolio")
            
            portfolio_df = pd.DataFrame(portfolio_details)
            display_df = portfolio_df[["Ticker", "ETF Name", "Category", "Allocation %", "Amount ($)"]]
            display_df["Allocation %"] = display_df["Allocation %"].apply(lambda x: f"{x:.0f}%")
            display_df["Amount ($)"] = display_df["Amount ($)"].apply(lambda x: f"${x:,.0f}")
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Pie chart
            fig = px.pie(portfolio_df, values="Allocation %", names="Ticker", title="Asset Allocation", hole=0.3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.header("📈 Monte Carlo Simulation")
            
            with st.spinner("Running simulations..."):
                sim_results, sim_stats = run_monte_carlo(
                    initial_amount, investment_years, 
                    allocation_data['expected_return'],
                    allocation_data['expected_volatility']
                )
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Median Outcome", f"${sim_stats['median']:,.0f}")
            with col2:
                st.metric("Expected Range", f"${sim_stats['percentile_25']:,.0f} - ${sim_stats['percentile_75']:,.0f}")
            with col3:
                st.metric("Risk of Loss", f"{sim_stats['probability_of_loss']:.1f}%")
            with col4:
                st.metric("Std Deviation", f"${sim_stats['std_dev']:,.0f}")
            
            # Simulation chart
            days = np.arange(len(sim_results))
            median_path = np.median(sim_results, axis=1)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=days, y=median_path, mode='lines', line=dict(color='red', width=2), name='Median Path'))
            fig.add_hline(y=initial_amount, line_dash="dash", line_color="green", annotation_text="Initial")
            fig.update_layout(title=f"Portfolio Value Over {investment_years} Years", height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            if show_dashboard:
                create_dashboard(portfolio_details, allocation_data, sim_stats, initial_amount, investment_years)
    
    with tab2:
        st.header("📚 Educational Resources")
        st.write("""
        ### Understanding Your Portfolio
        
        **Risk Profiles:**
        - **Conservative**: Low risk, focus on capital preservation
        - **Moderate**: Balanced approach with managed risk
        - **Aggressive**: High risk for maximum growth
        
        **Technical Indicators:**
        - **MACD**: Momentum indicator for buy/sell signals
        - **Moving Averages**: Trend direction identification
        
        **Important:**
        - Past performance doesn't guarantee future results
        - All investments carry risk of loss
        - Consult a licensed financial advisor
        """)

if __name__ == "__main__":
    main()
