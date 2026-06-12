"""
Robo-Advisor App for FinTech Course Thesis
Fixed Version - No st.markdown errors
"""

# ========== IMPORT LIBRARIES ==========
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="AI Robo-Advisor",
    page_icon="🤖",
    layout="wide"
)

# ========== RISK PROFILING LOGIC ==========
def calculate_risk_score(answers):
    """
    Calculate risk score from user answers
    """
    total_score = sum(answers)
    
    if total_score <= 12:
        return "Conservative"
    elif total_score <= 20:
        return "Moderate"
    else:
        return "Aggressive"

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
def monte_carlo_simulation(weights, initial_amount, years, n_sims=1000):
    """
    Simple Monte Carlo simulation
    """
    # Historical parameters
    expected_return = 0.08  # 8% annual expected return
    volatility = 0.15       # 15% annual volatility
    
    # Convert to daily
    daily_return = expected_return / 252
    daily_vol = volatility / np.sqrt(252)
    
    # Simulation
    trading_days = years * 252
    returns = np.random.normal(daily_return, daily_vol, 
                               (trading_days, n_sims))
    
    # Calculate cumulative returns
    cumulative_returns = np.cumprod(1 + returns, axis=0)
    
    # Calculate portfolio values
    portfolio_values = initial_amount * cumulative_returns
    
    return portfolio_values

# ========== MAIN APP ==========
def main():
    # Title
    st.title("🤖 AI-Powered Robo-Advisor")
    st.write("---")  # Use st.write instead of st.markdown
    
    # Sidebar for user input
    with st.sidebar:
        st.header("📋 Risk Assessment Questionnaire")
        st.write("Answer the following questions:")
        st.write("---")
        
        # Questions
        q1 = st.slider("1️⃣ Investment horizon (years)", 
                       min_value=1, max_value=30, value=10)
        
        q2 = st.select_slider("2️⃣ How would you react to a 20% market drop?",
                              options=["Sell everything", "Get nervous", "Do nothing", 
                                      "Buy more", "Aggressively buy more"],
                              value="Do nothing")
        q2_score = ["Sell everything", "Get nervous", "Do nothing", 
                   "Buy more", "Aggressively buy more"].index(q2) + 1
        
        q3 = st.radio("3️⃣ Your investment goal is:",
                     ["Capital preservation", "Income", "Balanced", 
                      "Growth", "Aggressive growth"],
                     index=2)
        q3_score = ["Capital preservation", "Income", "Balanced", 
                   "Growth", "Aggressive growth"].index(q3) + 1
        
        q4 = st.slider("4️⃣ What % of your savings would you invest?", 
                       min_value=0, max_value=100, value=50)
        q4_score = q4 // 20 + 1
        
        q5 = st.select_slider("5️⃣ Expected annual return target:",
                              options=["3-4%", "5-6%", "7-8%", "9-10%", "11%+"],
                              value="7-8%")
        q5_score = ["3-4%", "5-6%", "7-8%", "9-10%", "11%+"].index(q5) + 1
        
        # Investment amount
        st.write("---")
        initial_investment = st.number_input("💰 Investment amount ($)", 
                                            min_value=1000, 
                                            max_value=1000000, 
                                            value=10000,
                                            step=1000)
        
        investment_years = st.slider("📅 Investment period (years)", 
                                    min_value=1, max_value=30, value=5)
        
        st.write("---")
        submitted = st.button("🚀 GET MY PORTFOLIO", use_container_width=True)
    
    # Main content area
    if submitted:
        # Calculate risk score
        answers = [min(5, max(1, q1 // 6 + 1)), q2_score, q3_score, q4_score, q5_score]
        risk_profile = calculate_risk_score(answers)
        
        # Display risk profile
        st.success(f"### Your Risk Profile: **{risk_profile}**")
        st.write("Based on your answers, we've created a personalized portfolio")
        st.write("---")
        
        # Get portfolio weights
        weights = get_portfolio_weights(risk_profile)
        
        # Display portfolio allocation
        st.subheader("📊 Recommended Portfolio Allocation")
        
        # Create DataFrame for display
        portfolio_df = pd.DataFrame({
            'ETF': list(weights.keys()),
            'Allocation (%)': [w*100 for w in weights.values()]
        })
        
        # Display as columns
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.dataframe(portfolio_df, use_container_width=True, hide_index=True)
            
            # Calculate dollar amounts
            st.write("### 💵 Your Investment")
            for etf, weight in weights.items():
                amount = initial_investment * weight
                st.write(f"• **{etf}**: ${amount:,.2f}")
        
        with col2:
            fig = px.pie(portfolio_df, values='Allocation (%)', names='ETF', 
                        title='Portfolio Allocation')
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        # Monte Carlo Simulation
        st.subheader("📈 Monte Carlo Simulation")
        st.write("Shows possible outcomes for your investment")
        
        with st.spinner("Running simulations..."):
            sim_results = monte_carlo_simulation(weights, initial_investment, 
                                                investment_years, n_sims=1000)
            
            # Calculate statistics
            final_values = sim_results[-1, :]
            median_value = np.median(final_values)
            percentile_5 = np.percentile(final_values, 5)
            percentile_95 = np.percentile(final_values, 95)
        
        # Display results
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Median Outcome", f"${median_value:,.0f}")
        with col2:
            st.metric("Best Case (95th %)", f"${percentile_95:,.0f}")
        with col3:
            st.metric("Worst Case (5th %)", f"${percentile_5:,.0f}")
        
        # Simple line chart for simulation
        st.subheader("Sample Projection Paths")
        
        # Create chart data (show 50 sample paths)
        chart_data = pd.DataFrame()
        sample_paths = np.random.choice(sim_results.shape[1], min(50, sim_results.shape[1]), replace=False)
        
        for i, path_idx in enumerate(sample_paths[:10]):  # Show 10 paths for clarity
            chart_data[f'Path {i+1}'] = sim_results[:, path_idx]
        
        # Add median line
        chart_data['Median'] = np.median(sim_results, axis=1)
        
        st.line_chart(chart_data)
        
        # Return summary
        total_return = (median_value - initial_investment) / initial_investment * 100
        st.info(f"""
        **Summary for ${initial_investment:,} over {investment_years} years:**
        
        📈 Median outcome: **${median_value:,.0f}**
        📊 Expected return: **{total_return:.1f}%**
        ⚠️ Range: ${percentile_5:,.0f} to ${percentile_95:,.0f}
        """)
        
        # Disclaimer
        st.write("---")
        st.warning("""
        ⚠️ **Important Disclosure**: Past performance does not guarantee future results. 
        This robo-advisor is for educational purposes only. Consider consulting with a 
        licensed financial advisor before making investment decisions.
        """)
        
        # Explainability section
        with st.expander("🤔 Why this portfolio? (AI Explainability)"):
            st.write(f"""
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
            - Does not consider your full financial picture
            """)
    
    else:
        # Welcome screen
        st.info("👈 **Please complete the risk assessment in the sidebar and click 'GET MY PORTFOLIO'**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("### 📊 What you get:")
            st.write("- Personalized risk profile")
            st.write("- ETF portfolio allocation")
            st.write("- Interactive pie chart")
        with col2:
            st.write("### 📈 Monte Carlo:")
            st.write("- 1,000 market scenarios")
            st.write("- 1-30 year projections")
            st.write("- Probability analysis")
        with col3:
            st.write("### 🤖 AI Features:")
            st.write("- Risk scoring algorithm")
            st.write("- Statistical simulation")
            st.write("- Explainable decisions")

# ========== RUN THE APP ==========
if __name__ == "__main__":
    main()
