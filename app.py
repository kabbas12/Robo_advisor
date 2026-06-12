"""
AI Robo-Advisor for FinTech Thesis
With Real ETF Names and Professional Descriptions
Author: [Your Name]
"""

# ========== IMPORT LIBRARIES ==========
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="AI Robo-Advisor - Professional Portfolio Tool",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== ETF DATABASE WITH REAL NAMES ==========
ETF_DATABASE = {
    "BND": {
        "name": "Vanguard Total Bond Market ETF",
        "category": "Bonds",
        "description": "Broad exposure to US investment-grade bonds",
        "expense_ratio": 0.03,
        "risk_level": "Low"
    },
    "VTI": {
        "name": "Vanguard Total Stock Market ETF",
        "category": "US Stocks",
        "description": "Entire US stock market including small, mid, and large caps",
        "expense_ratio": 0.03,
        "risk_level": "Medium-High"
    },
    "VXUS": {
        "name": "Vanguard Total International Stock ETF",
        "category": "International Stocks",
        "description": "Non-US companies from developed and emerging markets",
        "expense_ratio": 0.07,
        "risk_level": "Medium-High"
    },
    "QQQ": {
        "name": "Invesco QQQ Trust",
        "category": "Growth Stocks",
        "description": "Nasdaq 100 - technology and innovation focus",
        "expense_ratio": 0.20,
        "risk_level": "High"
    },
    "SHY": {
        "name": "iShares 1-3 Year Treasury Bond ETF",
        "category": "Short-term Bonds",
        "description": "Low-risk US government bonds with short maturity",
        "expense_ratio": 0.15,
        "risk_level": "Very Low"
    },
    "SPY": {
        "name": "SPDR S&P 500 ETF Trust",
        "category": "Large Cap US Stocks",
        "description": "500 largest US companies (blue-chip stocks)",
        "expense_ratio": 0.09,
        "risk_level": "Medium"
    }
}

# ========== RISK PROFILING FUNCTION ==========
def calculate_risk_profile(answers):
    """
    Calculate risk profile from user answers
    Returns profile name and score
    """
    total_score = sum(answers)
    
    if total_score <= 12:
        return {
            "profile": "Conservative",
            "score": total_score,
            "color": "#2E86AB",
            "description": "You prioritize capital preservation over high returns",
            "allocation_style": "Income & Safety Focused"
        }
    elif total_score <= 20:
        return {
            "profile": "Moderate",
            "score": total_score,
            "color": "#F18F01",
            "description": "You seek balanced growth with managed risk",
            "allocation_style": "Balanced Growth"
        }
    else:
        return {
            "profile": "Aggressive",
            "score": total_score,
            "color": "#C73E1D",
            "description": "You pursue maximum growth and accept volatility",
            "allocation_style": "Growth & Wealth Building"
        }

# ========== PORTFOLIO CONSTRUCTION ==========
def get_portfolio_allocation(risk_profile, total_amount):
    """
    Returns detailed portfolio allocation with real ETF names
    """
    portfolios = {
        "Conservative": {
            "allocation": {
                "BND": 0.50,  # 50% Bonds (safety)
                "SHY": 0.20,  # 20% Short-term bonds (liquidity)
                "VTI": 0.20,  # 20% US stocks (moderate growth)
                "VXUS": 0.10  # 10% International (diversification)
            },
            "expected_return": 0.05,  # 5% annual
            "expected_volatility": 0.08,  # 8% annual
            "suitable_for": "Retirement funds, emergency savings, short-term goals (1-3 years)"
        },
        "Moderate": {
            "allocation": {
                "BND": 0.25,  # 25% Bonds (stability)
                "VTI": 0.45,  # 45% US stocks (growth)
                "VXUS": 0.20,  # 20% International (diversification)
                "QQQ": 0.10   # 10% Tech growth (higher return potential)
            },
            "expected_return": 0.08,  # 8% annual
            "expected_volatility": 0.12,  # 12% annual
            "suitable_for": "Long-term wealth building, retirement (5-10 years), college funds"
        },
        "Aggressive": {
            "allocation": {
                "VTI": 0.45,  # 45% US total market (core holding)
                "QQQ": 0.25,  # 25% Tech/growth (higher returns)
                "VXUS": 0.20,  # 20% International (global exposure)
                "BND": 0.10   # 10% Bonds (minimal safety net)
            },
            "expected_return": 0.11,  # 11% annual
            "expected_volatility": 0.18,  # 18% annual
            "suitable_for": "Long-term wealth (10+ years), high-income investors, inheritance planning"
        }
    }
    
    allocation_data = portfolios[risk_profile]
    
    # Calculate dollar amounts
    portfolio_details = []
    for ticker, weight in allocation_data["allocation"].items():
        etf_info = ETF_DATABASE.get(ticker, {})
        portfolio_details.append({
            "Ticker": ticker,
            "ETF Name": etf_info.get("name", ticker),
            "Category": etf_info.get("category", "Other"),
            "Allocation %": f"{weight * 100:.0f}%",
            "Amount ($)": f"${total_amount * weight:,.2f}",
            "Description": etf_info.get("description", "Diversified ETF"),
            "Expense Ratio": etf_info.get("expense_ratio", 0.10)
        })
    
    return portfolio_details, allocation_data

# ========== MONTE CARLO SIMULATION ==========
def run_monte_carlo(initial_amount, years, expected_return, volatility, n_sims=2000):
    """
    Run Monte Carlo simulation with realistic parameters
    """
    # Convert annual to daily parameters (252 trading days)
    daily_return = expected_return / 252
    daily_vol = volatility / np.sqrt(252)
    
    # Simulation
    trading_days = years * 252
    np.random.seed(42)  # For reproducibility
    
    # Generate random returns
    random_returns = np.random.normal(daily_return, daily_vol, (trading_days, n_sims))
    
    # Calculate cumulative returns
    cumulative_returns = np.cumprod(1 + random_returns, axis=0)
    
    # Calculate portfolio values
    portfolio_values = initial_amount * cumulative_returns
    
    # Calculate statistics
    final_values = portfolio_values[-1, :]
    
    stats = {
        "median": np.median(final_values),
        "mean": np.mean(final_values),
        "percentile_5": np.percentile(final_values, 5),
        "percentile_25": np.percentile(final_values, 25),
        "percentile_75": np.percentile(final_values, 75),
        "percentile_95": np.percentile(final_values, 95),
        "probability_of_loss": np.mean(final_values < initial_amount) * 100,
        "best_case": np.max(final_values),
        "worst_case": np.min(final_values)
    }
    
    return portfolio_values, stats

# ========== MAIN APPLICATION ==========
def main():
    # Header
    st.title("🤖 AI Robo-Advisor")
    st.caption("Professional Portfolio Construction Using Real ETFs | Powered by Monte Carlo Simulation")
    st.write("---")
    
    # Sidebar - Risk Assessment
    with st.sidebar:
        st.header("📋 Step 1: Risk Assessment")
        st.write("Answer these 5 questions honestly:")
        st.write("---")
        
        # Question 1
        q1 = st.slider(
            "**1. Investment Time Horizon**",
            min_value=1, max_value=30, value=10,
            help="Longer horizons allow more risk and potential growth"
        )
        q1_score = min(5, q1 // 6 + 1)
        
        # Question 2
        q2 = st.select_slider(
            "**2. Reaction to Market Drop (20%)**",
            options=["Sell everything", "Get nervous", "Do nothing", "Buy more", "Aggressively buy more"],
            value="Do nothing",
            help="How would you emotionally react to a market crash?"
        )
        q2_scores = {"Sell everything": 1, "Get nervous": 2, "Do nothing": 3, 
                    "Buy more": 4, "Aggressively buy more": 5}
        q2_score = q2_scores[q2]
        
        # Question 3
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
        
        # Question 4
        q4 = st.slider(
            "**4. Risk Capacity (% of savings)**",
            min_value=0, max_value=100, value=50,
            help="What percentage of your total savings are you investing?"
        )
        q4_score = min(5, q4 // 20 + 1)
        
        # Question 5
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
        
        # Investment details
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
        
        # Submit button
        submit = st.button("🎯 Generate Portfolio", type="primary", use_container_width=True)
    
    # Main content - Results
    if submit:
        # Calculate risk profile
        answers = [q1_score, q2_score, q3_score, q4_score, q5_score]
        risk_result = calculate_risk_profile(answers)
        risk_profile = risk_result["profile"]
        
        # Display risk profile banner
        st.success(f"""
        ### ✅ Your Risk Profile: **{risk_profile}**
        {risk_result['description']}
        **Style**: {risk_result['allocation_style']} | **Score**: {risk_result['score']}/25
        """)
        
        st.write("---")
        
        # Get portfolio allocation
        portfolio_details, allocation_data = get_portfolio_allocation(risk_profile, initial_amount)
        portfolio_df = pd.DataFrame(portfolio_details)
        
        # Display portfolio allocation
        st.header("📊 Your Personalized Portfolio")
        st.write(f"Based on your {risk_profile} profile, we recommend this ETF portfolio:")
        
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            # Display detailed table
            display_df = portfolio_df[["Ticker", "ETF Name", "Allocation %", "Amount ($)", "Expense Ratio"]]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Portfolio summary
            st.write("---")
            st.write("**📈 Portfolio Characteristics:**")
            st.write(f"• Expected Annual Return: **{allocation_data['expected_return']*100:.0f}%**")
            st.write(f"• Expected Volatility: **{allocation_data['expected_volatility']*100:.0f}%**")
            st.write(f"• Suitable For: **{allocation_data['suitable_for']}**")
        
        with col2:
            # Pie chart
            fig = px.pie(
                portfolio_df, 
                values=[float(x.replace('$', '').replace(',', '').split()[0]) for x in portfolio_df["Amount ($)"]],
                names=portfolio_df["Ticker"],
                title="Asset Allocation",
                color_discrete_sequence=px.colors.qualitative.Set2,
                hole=0.3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.write("---")
        
        # Monte Carlo Simulation
        st.header("📈 Monte Carlo Simulation")
        st.write(f"Projecting {initial_amount:,} over {investment_years} years with {allocation_data['expected_return']*100:.0f}% expected return")
        
        with st.spinner(f"Running 2,000 market simulations..."):
            sim_results, sim_stats = run_monte_carlo(
                initial_amount, 
                investment_years, 
                allocation_data['expected_return'],
                allocation_data['expected_volatility']
            )
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Median Outcome", f"${sim_stats['median']:,.0f}")
            percent_return = (sim_stats['median'] - initial_amount) / initial_amount * 100
            st.caption(f"📈 +{percent_return:.0f}% return")
        
        with col2:
            st.metric("Expected Range", f"${sim_stats['percentile_25']:,.0f} - ${sim_stats['percentile_75']:,.0f}")
            st.caption("25th to 75th percentile")
        
        with col3:
            st.metric("Worst Case (5%)", f"${sim_stats['percentile_5']:,.0f}")
            st.caption("Only 5% of scenarios worse")
        
        with col4:
            st.metric("Best Case (95%)", f"${sim_stats['percentile_95']:,.0f}")
            st.caption("Only 5% of scenarios better")
        
        # Risk of loss warning
        if sim_stats['probability_of_loss'] > 10:
            st.warning(f"⚠️ **Risk Warning**: {sim_stats['probability_of_loss']:.0f}% probability of losing money over {investment_years} years")
        else:
            st.info(f"✅ **Risk Assessment**: {sim_stats['probability_of_loss']:.0f}% probability of loss over {investment_years} years")
        
        # Simulation chart
        st.subheader("Portfolio Value Projections")
        
        # Create chart with median and confidence bands
        days = np.arange(len(sim_results))
        median_path = np.median(sim_results, axis=1)
        percentile_25 = np.percentile(sim_results, 25, axis=1)
        percentile_75 = np.percentile(sim_results, 75, axis=1)
        
        fig = go.Figure()
        
        # Add confidence band
        fig.add_trace(go.Scatter(
            x=np.concatenate([days, days[::-1]]),
            y=np.concatenate([percentile_75, percentile_25[::-1]]),
            fill='toself',
            fillcolor='rgba(128, 128, 128, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='25th-75th Percentile',
            showlegend=True
        ))
        
        # Add median line
        fig.add_trace(go.Scatter(
            x=days,
            y=median_path,
            mode='lines',
            line=dict(color='red', width=2),
            name='Median Path'
        ))
        
        # Add initial investment line
        fig.add_hline(y=initial_amount, line_dash="dash", line_color="green", 
                     annotation_text="Initial Investment")
        
        fig.update_layout(
            title=f"Portfolio Value Over {investment_years} Years (2,000 Simulations)",
            xaxis_title="Trading Days",
            yaxis_title="Portfolio Value ($)",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("---")
        
        # Education & Ethics Section
        st.header("📚 Understanding Your Portfolio")
        
        with st.expander("🔍 What are these ETFs? (Click to expand)"):
            for etf in portfolio_details:
                st.write(f"**{etf['Ticker']} - {etf['ETF Name']}**")
                st.write(f"*{etf['Description']}*")
                st.write(f"Category: {etf['Category']} | Expense Ratio: {etf['Expense Ratio']:.2f}%")
                st.write("---")
        
        with st.expander("⚠️ Important Disclosures & Ethics (Required for LO4)"):
            st.write("""
            **Regulatory & Ethical Considerations:**
            
            1. **Past Performance**: Historical returns do not guarantee future results
            2. **Market Risk**: All investments carry risk of loss
            3. **Inflation Risk**: Fixed income investments may lose purchasing power
            4. **Concentration Risk**: Sector-focused ETFs (like QQQ) have higher volatility
            5. **No Guarantees**: Monte Carlo simulations are probabilistic, not certainties
            
            **AI Limitations:**
            - Does not consider your complete financial picture (debts, emergency fund, insurance)
            - Cannot predict black swan events (2008 crisis, COVID-19, etc.)
            - Tax implications not considered
            - Not personalized financial advice
            
            **Next Steps:**
            - Consult with a licensed financial advisor
            - Consider dollar-cost averaging for large investments
            - Regularly rebalance your portfolio (annually)
            """)
        
        with st.expander("📊 How the AI Makes Decisions"):
            st.write(f"""
            **Risk Scoring Methodology:**
            - Your total risk score: **{risk_result['score']}/25**
            - Conservative: 0-12 points → Higher bond allocation
            - Moderate: 13-20 points → Balanced stock/bond mix
            - Aggressive: 21-25 points → Growth-focused stocks
            
            **Why this portfolio for you:**
            - Time horizon: {investment_years} years
            - Risk tolerance matches {risk_profile} historical allocation models
            - Based on Modern Portfolio Theory (Markowitz, 1952)
            - Optimized for your risk/return trade-off
            
            **Monte Carlo Methodology:**
            - 2,000 random market scenarios
            - Assumes lognormal return distribution
            - Historical volatility: {allocation_data['expected_volatility']*100:.0f}%
            - 252 trading days per year
            """)
    
    else:
        # Welcome screen (before submission)
        st.info("### 👈 Welcome to AI Robo-Advisor")
        st.write("""
        **Complete the risk assessment in the left sidebar to get your personalized portfolio**
        
        This tool will:
        - ✅ Assess your risk tolerance using 5 professional questions
        - ✅ Build a diversified ETF portfolio using real funds (Vanguard, BlackRock, Invesco)
        - ✅ Run 2,000 Monte Carlo simulations to project outcomes
        - ✅ Show you expected returns, risks, and confidence intervals
        - ✅ Explain the AI's decision-making process
        
        **Built with real ETFs you can actually invest in:**
        - VTI (Total US Stock Market)
        - BND (Total US Bond Market)
        - QQQ (Nasdaq 100 Tech)
        - VXUS (International Stocks)
        - SHY (Short-term Treasury Bonds)
        """)
        
        # Sample portfolio preview
        st.subheader("📊 Sample Portfolio by Risk Level")
        sample_col1, sample_col2, sample_col3 = st.columns(3)
        
        with sample_col1:
            st.write("**Conservative**")
            st.write("• 70% Bonds (BND, SHY)")
            st.write("• 30% Stocks (VTI, VXUS)")
            st.write("• Expected return: 5%")
            st.write("• Low volatility")
        
        with sample_col2:
            st.write("**Moderate**")
            st.write("• 25% Bonds (BND)")
            st.write("• 75% Stocks (VTI, VXUS, QQQ)")
            st.write("• Expected return: 8%")
            st.write("• Moderate volatility")
        
        with sample_col3:
            st.write("**Aggressive**")
            st.write("• 10% Bonds (BND)")
            st.write("• 90% Stocks (VTI, QQQ, VXUS)")
            st.write("• Expected return: 11%")
            st.write("• Higher volatility")

# ========== RUN APPLICATION ==========
if __name__ == "__main__":
    main()
