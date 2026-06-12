#Robo-Advisor App for FinTech Course Thesis
# Author: [Syed Kamran Abbas]
#Date: June 2026

from risk_questions import RiskProfiler
# ========== IMPORT LIBRARIES ==========
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="AI Robo-Advisor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS FOR BETTER LOOK ==========
st.markdown("""
<style>
    .stButton > button {
        background-color: #2E86AB;
        color: white;
        font-size: 18px;
        padding: 10px 24px;
        border-radius: 10px;
    }
    .big-font {
        font-size: 20px !important;
        font-weight: bold;
    }
    .success-box {
        padding: 20px;
        background-color: #d4edda;
        border-radius: 10px;
        border-left: 5px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

# ========== RISK PROFILING LOGIC ==========
def calculate_risk_score(answers):
    """
    Calculate risk score from user answers
    Higher score = higher risk tolerance
    """
    total_score = sum(answers)
    
    if total_score <= 12:
        return "Conservative", "#2E86AB"
    elif total_score <= 20:
        return "Moderate", "#F18F01"
    else:
        return "Aggressive", "#C73E1D"

def get_portfolio_weights(profile):
    """
    Return ETF weights based on risk profile
    """
    portfolios = {
        "Conservative": {
            "BND": 0.60,    # Total bond market
            "VTI": 0.25,    # Total stock market
            "VXUS": 0.10,   # International stocks
            "SHY": 0.05     # Short-term treasury
        },
        "Moderate": {
            "BND": 0.30,
            "VTI": 0.45,
            "VXUS": 0.20,
            "QQQ": 0.05     # Nasdaq (growth)
        },
        "Aggressive": {
            "BND": 0.10,
            "VTI": 0.50,
            "VXUS": 0.25,
            "QQQ": 0.15
        }
    }
    return portfolios[profile]

# ========== MONTE CARLO SIMULATION ==========
def monte_carlo_simulation(weights, initial_amount, years, n_sims=5000):
    """
    Run Monte Carlo simulation for portfolio returns
    """
    # Historical parameters (based on S&P 500 long-term average)
    expected_return = 0.08  # 8% annual expected return
    volatility = 0.15       # 15% annual volatility
    
    # Convert to daily parameters (252 trading days)
    daily_return = expected_return / 252
    daily_vol = volatility / np.sqrt(252)
    
    # Calculate portfolio return (weighted average)
    portfolio_return = daily_return
    portfolio_vol = daily_vol
    
    # Simulation
    trading_days = years * 252
    returns = np.random.normal(portfolio_return, portfolio_vol, 
                               (trading_days, n_sims))
    
    # Calculate cumulative returns
    cumulative_returns = np.cumprod(1 + returns, axis=0)
    
    # Calculate portfolio values
    portfolio_values = initial_amount * cumulative_returns
    
    return portfolio_values

def calculate_portfolio_stats(portfolio_values):
    """
    Calculate summary statistics for the simulation
    """
    final_values = portfolio_values[-1, :]
    
    stats = {
        "Expected Value": np.mean(final_values),
        "Median Value": np.median(final_values),
        "5th Percentile (Worst Case)": np.percentile(final_values, 5),
        "95th Percentile (Best Case)": np.percentile(final_values, 95),
        "Standard Deviation": np.std(final_values),
        "Probability of Loss": np.mean(final_values < 10000) * 100
    }
    return stats

# ========== FETCH REAL ETF DATA ==========
@st.cache_data(ttl=3600)
def fetch_etf_data(etf_symbols, period="1y"):
    """
    Fetch historical data for ETFs
    """
    data = {}
    for symbol in etf_symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            if not hist.empty:
                data[symbol] = hist['Close']
        except Exception as e:
            st.warning(f"Could not fetch data for {symbol}: {e}")
    
    return pd.DataFrame(data)

# ========== MAIN APP ==========
def main():
    # Title and description
    st.title("🤖 AI-Powered Robo-Advisor")
    st.markdown("---")
    
    # Sidebar for user input
    with st.sidebar:
        st.header("📋 Risk Assessment Questionnaire")
        st.markdown("Answer the following questions honestly:")
        st.markdown("---")
        
       # In the sidebar section, replace all questions with:
answers = RiskProfiler.display_questionnaire()
risk_result = RiskProfiler.get_risk_profile(answers)
risk_profile = risk_result['profile']
        
        # Investment amount
        st.markdown("---")
        initial_investment = st.number_input("💰 Investment amount ($)", 
                                            min_value=1000, 
                                            max_value=1000000, 
                                            value=10000,
                                            step=1000)
        
        investment_years = st.slider("📅 Investment period (years)", 
                                    min_value=1, max_value=30, value=5)
        
        # Submit button
        st.markdown("---")
        submitted = st.button("🚀 GET MY PORTFOLIO", use_container_width=True)
    
    # Main content area
    if submitted:
        # Calculate risk score
        answers = [q1//6 + 1, q2_score, q3_score, q4_score, q5_score]
        answers = [min(5, max(1, a)) for a in answers]  # Ensure 1-5 range
        risk_profile, profile_color = calculate_risk_score(answers)
        
        # Display risk profile
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown(f"""
            <div class="success-box" style="text-align: center;">
                <h2 style="color: {profile_color}">Your Risk Profile: {risk_profile}</h2>
                <p style="font-size: 18px;">Based on your answers, we've created a personalized portfolio</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Get portfolio weights
        weights = get_portfolio_weights(risk_profile)
        
        # Display portfolio allocation
        st.subheader("📊 Recommended Portfolio Allocation")
        
        # Create DataFrame for display
        portfolio_df = pd.DataFrame({
            'ETF': list(weights.keys()),
            'Allocation (%)': [w*100 for w in weights.values()],
            'Description': [
                'Total Bond Market ETF',
                'Total Stock Market ETF',
                'International Stock ETF',
                'Short-term Treasury ETF' if 'SHY' in weights else 'Nasdaq Growth ETF'
            ][:len(weights)]
        })
        
        # Display as table and chart
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.dataframe(portfolio_df, use_container_width=True, hide_index=True)
            
            # Calculate dollar amounts
            st.markdown("### 💵 Your Investment")
            for etf, weight in weights.items():
                amount = initial_investment * weight
                st.write(f"• **{etf}**: ${amount:,.2f}")
        
        with col2:
            fig = px.pie(portfolio_df, values='Allocation (%)', names='ETF', 
                        title='Portfolio Allocation',
                        color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        # Monte Carlo Simulation
        st.subheader("📈 Monte Carlo Simulation (5,000 scenarios)")
        st.markdown("*Shows possible outcomes for your $10,000 investment*")
        
        with st.spinner("Running 5,000 simulations..."):
            sim_results = monte_carlo_simulation(weights, initial_investment, 
                                                investment_years, n_sims=5000)
            
            # Calculate statistics
            stats = calculate_portfolio_stats(sim_results)
        
        # Display simulation chart
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create plotly figure
            fig = go.Figure()
            
            # Add all simulation paths (sample 100 for visibility)
            sample_paths = np.random.choice(sim_results.shape[1], 
                                           min(100, sim_results.shape[1]), 
                                           replace=False)
            for i in sample_paths:
                fig.add_trace(go.Scatter(
                    y=sim_results[:, i],
                    mode='lines',
                    line=dict(width=0.5, color='lightgray'),
                    showlegend=False,
                    hoverinfo='none'
                ))
            
            # Add median line
            median_path = np.median(sim_results, axis=1)
            fig.add_trace(go.Scatter(
                y=median_path,
                mode='lines',
                line=dict(color='red', width=3),
                name='Median Path',
                hovertemplate='Year %{x}: $%{y:,.0f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=f'Portfolio Value Over {investment_years} Years',
                xaxis_title='Trading Days',
                yaxis_title='Portfolio Value ($)',
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Key Statistics")
            
            # Create stats dataframe
            stats_df = pd.DataFrame({
                'Metric': list(stats.keys()),
                'Value': [
                    f"${stats['Expected Value']:,.0f}",
                    f"${stats['Median Value']:,.0f}",
                    f"${stats['5th Percentile (Worst Case)']:,.0f}",
                    f"${stats['95th Percentile (Best Case)']:,.0f}",
                    f"${stats['Standard Deviation']:,.0f}",
                    f"{stats['Probability of Loss']:.1f}%"
                ]
            })
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
            
            # Return summary
            total_return = (stats['Median Value'] - initial_investment) / initial_investment * 100
            st.info(f"""
            **Summary for ${initial_investment:,} over {investment_years} years:**
            
            📈 Median outcome: **${stats['Median Value']:,.0f}**
            📊 Expected return: **{total_return:.1f}%**
            ⚠️ Risk of loss: **{stats['Probability of Loss']:.1f}%**
            """)
        
        # Educational disclaimer
        st.markdown("---")
        st.warning("""
        ⚠️ **Important Disclosure**: Past performance does not guarantee future results. 
        This robo-advisor is for educational purposes only. Consider consulting with a 
        licensed financial advisor before making investment decisions.
        """)
        
        # Explainability section (for LO4 - Ethics)
        with st.expander("🤔 Why this portfolio? (AI Explainability)"):
            st.markdown(f"""
            **Your profile: {risk_profile}**
            
            **Reasoning:**
            - You have a {investment_years}-year investment horizon
            - Your risk tolerance score was {sum(answers)}/25
            - Portfolio {risk_profile.lower()} portfolios historically balance growth with volatility
            
            **What this means:**
            - **Conservative**: Prioritizes capital preservation (60% bonds)
            - **Moderate**: Balanced approach (30% bonds, 70% stocks)
            - **Aggressive**: Growth-focused (10% bonds, 90% stocks)
            
            **Limitations of AI:**
            - Monte Carlo simulations assume normal market conditions
            - Cannot predict black swan events (e.g., 2008 crisis, COVID-19)
            - Does not consider your full financial picture (debts, emergency fund)
            """)
    
    else:
        # Welcome screen before submission
        st.info("👈 **Please complete the risk assessment in the sidebar and click 'GET MY PORTFOLIO'**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            ### 📊 What you get:
            - Personalized risk profile
            - ETF portfolio allocation
            - Interactive pie chart
            """)
        with col2:
            st.markdown("""
            ### 📈 Monte Carlo:
            - 5,000 market scenarios
            - 1-30 year projections
            - Probability analysis
            """)
        with col3:
            st.markdown("""
            ### 🤖 AI Features:
            - Risk scoring algorithm
            - Statistical simulation
            - Explainable decisions
            """)

# ========== RUN THE APP ==========
if __name__ == "__main__":
    main()
