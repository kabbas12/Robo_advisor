"""
AI Robo-Advisor: A Portfolio Construction Tool for Retail Investors
Thesis Project - Simplified & Fully Functional Version
Author: [Your Name]
Date: [Current Date]
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
    page_title="AI Robo-Advisor - Thesis Project",
    page_icon="📊",
    layout="wide"
)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .buy-signal {
        background-color: #d4edda;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 5px 0;
    }
    .sell-signal {
        background-color: #f8d7da;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== ETF DATABASE (15 Core Funds) ==========
ETF_DATABASE = {
    # US Equity
    "SPY": {
        "name": "S&P 500 ETF",
        "category": "US Large Cap",
        "description": "Tracks 500 largest US companies",
        "expense_ratio": 0.09,
        "risk_level": "Medium",
        "dividend_yield": 1.3,
        "sector": "Equity"
    },
    "VTI": {
        "name": "Total Stock Market ETF",
        "category": "US Total Market",
        "description": "Complete US stock market",
        "expense_ratio": 0.03,
        "risk_level": "Medium-High",
        "dividend_yield": 1.4,
        "sector": "Equity"
    },
    "QQQ": {
        "name": "Nasdaq 100 ETF",
        "category": "Growth",
        "description": "Technology and innovation focus",
        "expense_ratio": 0.20,
        "risk_level": "High",
        "dividend_yield": 0.6,
        "sector": "Equity"
    },
    "IWM": {
        "name": "Russell 2000 ETF",
        "category": "Small Cap",
        "description": "US small-cap companies",
        "expense_ratio": 0.19,
        "risk_level": "High",
        "dividend_yield": 1.2,
        "sector": "Equity"
    },
    # International
    "VXUS": {
        "name": "International Stock ETF",
        "category": "International",
        "description": "Non-US developed and emerging markets",
        "expense_ratio": 0.07,
        "risk_level": "Medium-High",
        "dividend_yield": 2.9,
        "sector": "International"
    },
    "EEM": {
        "name": "Emerging Markets ETF",
        "category": "Emerging Markets",
        "description": "Emerging market equities",
        "expense_ratio": 0.68,
        "risk_level": "High",
        "dividend_yield": 2.5,
        "sector": "International"
    },
    # Bonds
    "BND": {
        "name": "Total Bond Market ETF",
        "category": "Bonds",
        "description": "US investment-grade bonds",
        "expense_ratio": 0.03,
        "risk_level": "Low",
        "dividend_yield": 4.2,
        "sector": "Fixed Income"
    },
    "AGG": {
        "name": "Core US Aggregate Bond ETF",
        "category": "Bonds",
        "description": "Broad US bond market",
        "expense_ratio": 0.04,
        "risk_level": "Low",
        "dividend_yield": 4.3,
        "sector": "Fixed Income"
    },
    "LQD": {
        "name": "Corporate Bond ETF",
        "category": "Corporate Bonds",
        "description": "Investment-grade corporate bonds",
        "expense_ratio": 0.14,
        "risk_level": "Medium-Low",
        "dividend_yield": 4.8,
        "sector": "Fixed Income"
    },
    # Real Estate & Alternatives
    "VNQ": {
        "name": "Real Estate ETF",
        "category": "Real Estate",
        "description": "US real estate investment trusts",
        "expense_ratio": 0.12,
        "risk_level": "Medium",
        "dividend_yield": 4.1,
        "sector": "Alternatives"
    },
    "GLD": {
        "name": "Gold ETF",
        "category": "Commodities",
        "description": "Physical gold bullion",
        "expense_ratio": 0.40,
        "risk_level": "Medium",
        "dividend_yield": 0.0,
        "sector": "Alternatives"
    },
    # Sector ETFs
    "XLK": {
        "name": "Technology Sector ETF",
        "category": "Sector",
        "description": "Technology companies",
        "expense_ratio": 0.10,
        "risk_level": "High",
        "dividend_yield": 0.8,
        "sector": "Equity"
    },
    "XLF": {
        "name": "Financial Sector ETF",
        "category": "Sector",
        "description": "Financial services companies",
        "expense_ratio": 0.10,
        "risk_level": "Medium-High",
        "dividend_yield": 2.1,
        "sector": "Equity"
    },
    # Dividend
    "VYM": {
        "name": "High Dividend Yield ETF",
        "category": "Dividend",
        "description": "High dividend paying stocks",
        "expense_ratio": 0.06,
        "risk_level": "Medium",
        "dividend_yield": 3.0,
        "sector": "Equity"
    },
    # ESG
    "ESGU": {
        "name": "ESG US ETF",
        "category": "ESG",
        "description": "ESG-focused US equities",
        "expense_ratio": 0.15,
        "risk_level": "Medium",
        "dividend_yield": 1.3,
        "sector": "Equity"
    }
}

# ========== RISK ASSESSMENT (5 Questions) ==========
def calculate_risk_profile(answers):
    """Simple risk assessment with 5 questions"""
    total_score = sum(answers)
    
    if total_score <= 8:
        return {
            "profile": "Conservative",
            "score": total_score,
            "description": "You prioritize capital preservation",
            "allocation": {
                "BND": 0.40, "AGG": 0.20, "LQD": 0.10,
                "VTI": 0.10, "VXUS": 0.10, "VNQ": 0.05, "GLD": 0.05
            },
            "expected_return": 0.05,
            "expected_volatility": 0.07,
            "equity_pct": 25,
            "bond_pct": 70,
            "alt_pct": 5
        }
    elif total_score <= 13:
        return {
            "profile": "Moderate",
            "score": total_score,
            "description": "You seek balanced growth with managed risk",
            "allocation": {
                "VTI": 0.25, "SPY": 0.15, "VXUS": 0.15,
                "BND": 0.20, "AGG": 0.10,
                "VNQ": 0.05, "GLD": 0.05, "VYM": 0.05
            },
            "expected_return": 0.08,
            "expected_volatility": 0.12,
            "equity_pct": 55,
            "bond_pct": 30,
            "alt_pct": 15
        }
    else:
        return {
            "profile": "Aggressive",
            "score": total_score,
            "description": "You pursue maximum growth and accept volatility",
            "allocation": {
                "VTI": 0.25, "QQQ": 0.20, "SPY": 0.15,
                "VXUS": 0.15, "IWM": 0.10,
                "BND": 0.05, "XLK": 0.05, "VNQ": 0.05
            },
            "expected_return": 0.11,
            "expected_volatility": 0.18,
            "equity_pct": 85,
            "bond_pct": 5,
            "alt_pct": 10
        }

# ========== PORTFOLIO CONSTRUCTION ==========
def build_portfolio(risk_result, total_amount):
    """Build portfolio based on risk profile"""
    portfolio_details = []
    allocation = risk_result["allocation"]
    
    for ticker, weight in allocation.items():
        etf_info = ETF_DATABASE.get(ticker, {})
        portfolio_details.append({
            "Ticker": ticker,
            "ETF Name": etf_info.get("name", ticker),
            "Category": etf_info.get("category", "Other"),
            "Allocation %": weight * 100,
            "Amount ($)": total_amount * weight,
            "Expense Ratio": etf_info.get("expense_ratio", 0.10),
            "Dividend Yield": etf_info.get("dividend_yield", 0),
            "Risk Level": etf_info.get("risk_level", "Medium")
        })
    
    allocation_data = {
        "expected_return": risk_result["expected_return"],
        "expected_volatility": risk_result["expected_volatility"],
        "sharpe_ratio": (risk_result["expected_return"] - 0.02) / risk_result["expected_volatility"],
        "max_drawdown": -risk_result["expected_volatility"] * 2
    }
    
    return portfolio_details, allocation_data

# ========== MONTE CARLO SIMULATION ==========
def run_monte_carlo(initial_amount, years, expected_return, volatility, n_sims=3000):
    """Simple Monte Carlo simulation"""
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
        "percentile_10": np.percentile(final_values, 10),
        "percentile_25": np.percentile(final_values, 25),
        "percentile_75": np.percentile(final_values, 75),
        "percentile_90": np.percentile(final_values, 90),
        "probability_of_loss": np.mean(final_values < initial_amount) * 100,
        "best_case": np.max(final_values),
        "worst_case": np.min(final_values)
    }
    
    return portfolio_values, stats

# ========== TECHNICAL ANALYSIS ==========
@st.cache_data(ttl=3600)
def fetch_stock_data(ticker, period="6mo"):
    """Fetch stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        if data.empty:
            return None
        return data
    except:
        return None

def calculate_technical_indicators(data):
    """Calculate MACD and Moving Averages"""
    df = data.copy()
    
    # Simple Moving Averages
    df['MA_20'] = df['Close'].rolling(window=20).mean()
    df['MA_50'] = df['Close'].rolling(window=50).mean()
    
    # MACD
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['Histogram'] = df['MACD'] - df['Signal']
    
    # Golden Cross and Death Cross
    df['Golden_Cross'] = (df['MA_20'] > df['MA_50']) & (df['MA_20'].shift(1) <= df['MA_50'].shift(1))
    df['Death_Cross'] = (df['MA_20'] < df['MA_50']) & (df['MA_20'].shift(1) >= df['MA_50'].shift(1))
    
    # Current Trend
    df['Trend'] = 'Bullish' if df['MA_20'].iloc[-1] > df['MA_50'].iloc[-1] else 'Bearish'
    
    return df

def plot_macd(data, ticker):
    """Plot MACD chart"""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.08, row_heights=[0.5, 0.5])
    
    # Price and MAs
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Price', line=dict(color='black', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['MA_20'], name='MA 20', line=dict(color='orange', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['MA_50'], name='MA 50', line=dict(color='blue', width=1.5)), row=1, col=1)
    
    # Golden/Death Cross markers
    golden = data[data['Golden_Cross']]
    death = data[data['Death_Cross']]
    fig.add_trace(go.Scatter(x=golden.index, y=golden['Close'], mode='markers', 
                            name='Golden Cross', marker=dict(color='green', size=12, symbol='triangle-up')), row=1, col=1)
    fig.add_trace(go.Scatter(x=death.index, y=death['Close'], mode='markers',
                            name='Death Cross', marker=dict(color='red', size=12, symbol='triangle-down')), row=1, col=1)
    
    # MACD
    fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], name='MACD', line=dict(color='blue', width=1.5)), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['Signal'], name='Signal', line=dict(color='red', width=1.5)), row=2, col=1)
    colors = ['green' if v >= 0 else 'red' for v in data['Histogram']]
    fig.add_trace(go.Bar(x=data.index, y=data['Histogram'], name='Histogram', marker_color=colors), row=2, col=1)
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
    fig.update_layout(title=f"{ticker} - Technical Analysis", height=500, showlegend=True)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)
    
    return fig

# ========== MAIN APP ==========
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Robo-Advisor</h1>
        <p style="font-size: 18px;">Simplified Portfolio Construction with Technical Analysis</p>
        <p style="font-size: 14px; opacity: 0.8;">Thesis Project - Fully Functional Prototype</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Step 1: Risk Assessment")
        st.write("Answer these 5 questions:")
        st.write("---")
        
        # Question 1
        q1 = st.slider("1️⃣ Investment Time Horizon", 1, 30, 10, 
                      help="How many years until you need the money?")
        q1_score = min(5, q1 // 6 + 1)
        
        # Question 2
        q2 = st.select_slider("2️⃣ Market Drop Reaction", 
            options=["Sell Everything", "Get Nervous", "Do Nothing", "Buy More", "Aggressively Buy"],
            value="Do Nothing")
        q2_scores = {"Sell Everything": 1, "Get Nervous": 2, "Do Nothing": 3, "Buy More": 4, "Aggressively Buy": 5}
        q2_score = q2_scores[q2]
        
        # Question 3
        q3 = st.radio("3️⃣ Investment Goal", 
            ["Capital Preservation", "Income", "Balanced Growth", "Wealth Building", "Maximum Growth"],
            index=2)
        q3_scores = {"Capital Preservation": 1, "Income": 2, "Balanced Growth": 3, 
                    "Wealth Building": 4, "Maximum Growth": 5}
        q3_score = q3_scores[q3]
        
        # Question 4
        q4 = st.slider("4️⃣ Risk Capacity (% of savings)", 0, 100, 50)
        q4_score = min(5, q4 // 20 + 1)
        
        # Question 5
        q5 = st.select_slider("5️⃣ Expected Return", 
            options=["3-4% (Safe)", "5-6% (Conservative)", "7-8% (Moderate)", 
                    "9-10% (Growth)", "11%+ (Aggressive)"],
            value="7-8% (Moderate)")
        q5_scores = {"3-4% (Safe)": 1, "5-6% (Conservative)": 2, "7-8% (Moderate)": 3, 
                    "9-10% (Growth)": 4, "11%+ (Aggressive)": 5}
        q5_score = q5_scores[q5]
        
        st.write("---")
        
        # Investment Details
        st.header("💰 Step 2: Investment")
        amount = st.number_input("Amount ($)", min_value=1000, max_value=1000000, value=10000, step=1000)
        years = st.slider("Years", 1, 30, 10)
        
        st.write("---")
        submit = st.button("🎯 Generate Portfolio", type="primary", use_container_width=True)
    
    # Main content
    if submit:
        # Calculate risk profile
        answers = [q1_score, q2_score, q3_score, q4_score, q5_score]
        risk_result = calculate_risk_profile(answers)
        
        # Build portfolio
        portfolio_details, allocation_data = build_portfolio(risk_result, amount)
        
        # Display results
        st.success(f"""
        ### ✅ Your Risk Profile: **{risk_result['profile']}**
        Score: {risk_result['score']}/25 | {risk_result['description']}
        **Recommended Allocation**: {risk_result['equity_pct']}% Equity | {risk_result['bond_pct']}% Bonds | {risk_result['alt_pct']}% Alternatives
        """)
        
        # Portfolio Display
        st.subheader("📊 Your Portfolio")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            df = pd.DataFrame(portfolio_details)
            display_df = df[["Ticker", "ETF Name", "Category", "Allocation %", "Amount ($)", "Expense Ratio"]]
            display_df["Allocation %"] = display_df["Allocation %"].apply(lambda x: f"{x:.1f}%")
            display_df["Amount ($)"] = display_df["Amount ($)"].apply(lambda x: f"${x:,.0f}")
            display_df["Expense Ratio"] = display_df["Expense Ratio"].apply(lambda x: f"{x:.2f}%")
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        with col2:
            fig = px.pie(df, values="Allocation %", names="Ticker", title="Asset Allocation", hole=0.3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        # Monte Carlo Simulation
        st.subheader("📈 Monte Carlo Simulation")
        with st.spinner("Running simulations..."):
            sim_results, sim_stats = run_monte_carlo(amount, years, 
                                                    allocation_data['expected_return'],
                                                    allocation_data['expected_volatility'])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Median Outcome", f"${sim_stats['median']:,.0f}")
        with col2:
            st.metric("Expected Range", f"${sim_stats['percentile_25']:,.0f} - ${sim_stats['percentile_75']:,.0f}")
        with col3:
            st.metric("Risk of Loss", f"{sim_stats['probability_of_loss']:.1f}%")
        with col4:
            cagr = ((sim_stats['median'] / amount) ** (1/years) - 1) * 100
            st.metric("CAGR", f"{cagr:.1f}%")
        
        # Simulation Chart
        days = np.arange(len(sim_results))
        median_path = np.median(sim_results, axis=1)
        p25 = np.percentile(sim_results, 25, axis=1)
        p75 = np.percentile(sim_results, 75, axis=1)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=np.concatenate([days, days[::-1]]), 
                                y=np.concatenate([p75, p25[::-1]]),
                                fill='toself', fillcolor='rgba(100,100,100,0.2)',
                                line=dict(color='rgba(255,255,255,0)'), name='25th-75th Percentile'))
        fig.add_trace(go.Scatter(x=days, y=median_path, mode='lines', 
                                line=dict(color='red', width=2), name='Median Path'))
        fig.add_hline(y=amount, line_dash="dash", line_color="green", annotation_text="Initial")
        fig.update_layout(title=f"Portfolio Value Over {years} Years", height=400,
                         xaxis_title="Trading Days", yaxis_title="Portfolio Value ($)")
        st.plotly_chart(fig, use_container_width=True)
        
        # Technical Analysis Tab
        st.subheader("📈 Technical Analysis")
        
        # Select security for technical analysis
        selected_ticker = st.selectbox("Select Security for Technical Analysis", 
                                      [etf['Ticker'] for etf in portfolio_details[:5]])
        
        if selected_ticker:
            with st.spinner(f"Fetching data for {selected_ticker}..."):
                data = fetch_stock_data(selected_ticker, period="6mo")
                if data is not None:
                    tech_data = calculate_technical_indicators(data)
                    fig = plot_macd(tech_data, selected_ticker)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Current Status
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Current Price", f"${tech_data['Close'].iloc[-1]:.2f}")
                        st.metric("Trend", tech_data['Trend'].iloc[-1])
                    with col2:
                        st.metric("MA 20", f"${tech_data['MA_20'].iloc[-1]:.2f}")
                        st.metric("MA 50", f"${tech_data['MA_50'].iloc[-1]:.2f}")
                    
                    # Show recent crosses
                    last_golden = tech_data[tech_data['Golden_Cross']]
                    last_death = tech_data[tech_data['Death_Cross']]
                    
                    if len(last_golden) > 0:
                        st.success(f"🟢 Last Golden Cross: {last_golden.index[-1].strftime('%Y-%m-%d')} at ${last_golden['Close'].iloc[-1]:.2f}")
                    if len(last_death) > 0:
                        st.error(f"🔴 Last Death Cross: {last_death.index[-1].strftime('%Y-%m-%d')} at ${last_death['Close'].iloc[-1]:.2f}")
                else:
                    st.warning(f"Could not fetch data for {selected_ticker}")
    
    else:
        # Welcome screen
        st.info("### 👈 Complete the risk assessment in the sidebar to get started")
        st.write("""
        **This Robo-Advisor will:**
        1. ✅ Assess your risk tolerance with 5 questions
        2. ✅ Build a diversified ETF portfolio (15+ ETFs)
        3. ✅ Run Monte Carlo simulations to project outcomes
        4. ✅ Provide technical analysis with MACD and Moving Averages
        5. ✅ Visualize all results with interactive charts
        
        **Thesis Project Features:**
        - 📊 Modern Portfolio Theory application
        - 📈 Technical Analysis integration
        - 🎲 Monte Carlo probabilistic modeling
        - 🎯 User-friendly interface
        - 📚 Educational component
        """)
        
        # Show example
        with st.expander("📊 Preview: Technical Analysis Example", expanded=True):
            st.write("""
            **MACD (Moving Average Convergence Divergence) Analysis:**
            - MACD Line: Difference between 12-day and 26-day EMAs
            - Signal Line: 9-day EMA of MACD
            - Histogram: MACD - Signal Line
            - Bullish Signal: MACD crosses above Signal Line
            - Bearish Signal: MACD crosses below Signal Line
            
            **Golden Cross vs Death Cross:**
            - Golden Cross: 20-day MA crosses above 50-day MA (Bullish)
            - Death Cross: 20-day MA crosses below 50-day MA (Bearish)
            """)

# ========== RUN ==========
if __name__ == "__main__":
    main()
