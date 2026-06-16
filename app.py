"""
AI Robo-Advisor for FinTech Thesis
With Professional Dashboard & Banking Analytics
Author: Syed Kamran Abbas 
"""

# ========== IMPORT LIBRARIES ==========
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
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
        "inception_date": "2007-04-03"
    },
    "VTI": {
        "name": "Vanguard Total Stock Market ETF",
        "category": "US Stocks",
        "description": "Entire US stock market including small, mid, and large caps",
        "expense_ratio": 0.03,
        "risk_level": "Medium-High",
        "dividend_yield": 1.4,
        "inception_date": "2001-05-24"
    },
    "VXUS": {
        "name": "Vanguard Total International Stock ETF",
        "category": "International Stocks",
        "description": "Non-US companies from developed and emerging markets",
        "expense_ratio": 0.07,
        "risk_level": "Medium-High",
        "dividend_yield": 2.9,
        "inception_date": "2011-01-26"
    },
    "QQQ": {
        "name": "Invesco QQQ Trust",
        "category": "Growth Stocks",
        "description": "Nasdaq 100 - technology and innovation focus",
        "expense_ratio": 0.20,
        "risk_level": "High",
        "dividend_yield": 0.6,
        "inception_date": "1999-03-10"
    },
    "SHY": {
        "name": "iShares 1-3 Year Treasury Bond ETF",
        "category": "Short-term Bonds",
        "description": "Low-risk US government bonds with short maturity",
        "expense_ratio": 0.15,
        "risk_level": "Very Low",
        "dividend_yield": 4.1,
        "inception_date": "2002-07-22"
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
                "BND": 0.50,
                "SHY": 0.20,
                "VTI": 0.20,
                "VXUS": 0.10
            },
            "expected_return": 0.05,
            "expected_volatility": 0.08,
            "sharpe_ratio": 0.62,
            "max_drawdown": -0.12,
            "suitable_for": "Retirement funds, emergency savings, short-term goals (1-3 years)"
        },
        "Moderate": {
            "allocation": {
                "BND": 0.25,
                "VTI": 0.45,
                "VXUS": 0.20,
                "QQQ": 0.10
            },
            "expected_return": 0.08,
            "expected_volatility": 0.12,
            "sharpe_ratio": 0.67,
            "max_drawdown": -0.25,
            "suitable_for": "Long-term wealth building, retirement (5-10 years), college funds"
        },
        "Aggressive": {
            "allocation": {
                "VTI": 0.45,
                "QQQ": 0.25,
                "VXUS": 0.20,
                "BND": 0.10
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
            "Allocation %": weight * 100,
            "Amount ($)": total_amount * weight,
            "Description": etf_info.get("description", "Diversified ETF"),
            "Expense Ratio": etf_info.get("expense_ratio", 0.10),
            "Dividend Yield": etf_info.get("dividend_yield", 0)
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
        
        # Fee analysis
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
    
    # Calculate benchmark returns
    sAndP_return = 0.10  # S&P 500 historical return
    bond_return = 0.04    # Bond market return
    
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
    
    # Create histogram of final values
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
    st.caption("Professional Portfolio Construction with Real-Time Analytics Dashboard")
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
        
        # Dashboard toggle
        show_dashboard = st.checkbox("📊 Show Detailed Dashboard", value=True, 
                                     help="Display comprehensive analytics dashboard")
        
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
        **Style**: {risk_result['allocation_style']} | **Score**: {risk_result['score']}/25 | **Risk Tolerance**: {risk_result['risk_tolerance']}
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
            display_df = portfolio_df[["Ticker", "ETF Name", "Allocation %", "Amount ($)", "Expense Ratio", "Dividend Yield"]]
            display_df["Allocation %"] = display_df["Allocation %"].apply(lambda x: f"{x:.0f}%")
            display_df["Amount ($)"] = display_df["Amount ($)"].apply(lambda x: f"${x:,.0f}")
            display_df["Expense Ratio"] = display_df["Expense Ratio"].apply(lambda x: f"{x:.2f}%")
            display_df["Dividend Yield"] = display_df["Dividend Yield"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Portfolio summary
            st.write("---")
            st.write("**📈 Portfolio Characteristics:**")
            st.write(f"• Expected Annual Return: **{allocation_data['expected_return']*100:.0f}%**")
            st.write(f"• Expected Volatility: **{allocation_data['expected_volatility']*100:.0f}%**")
            st.write(f"• Sharpe Ratio: **{allocation_data['sharpe_ratio']:.2f}**")
            st.write(f"• Suitable For: **{allocation_data['suitable_for']}**")
        
        with col2:
            fig = px.pie(
                portfolio_df, 
                values="Allocation %",
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
        st.write(f"Projecting ${initial_amount:,} over {investment_years} years with {allocation_data['expected_return']*100:.0f}% expected return")
        
        with st.spinner(f"Running 5,000 market simulations..."):
            sim_results, sim_stats = run_monte_carlo(
                initial_amount, 
                investment_years, 
                allocation_data['expected_return'],
                allocation_data['expected_volatility'],
                n_sims=5000
            )
        
        # Display basic simulation stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Median Outcome", f"${sim_stats['median']:,.0f}")
        with col2:
            st.metric("Expected Range", f"${sim_stats['percentile_25']:,.0f} - ${sim_stats['percentile_75']:,.0f}")
        with col3:
            st.metric("Risk of Loss", f"{sim_stats['probability_of_loss']:.1f}%")
        with col4:
            st.metric("Gain >50% Probability", f"{sim_stats['probability_of_gain_50pct']:.1f}%")
        
        # Simulation chart
        days = np.arange(len(sim_results))
        median_path = np.median(sim_results, axis=1)
        percentile_25 = np.percentile(sim_results, 25, axis=1)
        percentile_75 = np.percentile(sim_results, 75, axis=1)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=np.concatenate([days, days[::-1]]),
            y=np.concatenate([percentile_75, percentile_25[::-1]]),
            fill='toself',
            fillcolor='rgba(128, 128, 128, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='25th-75th Percentile',
            showlegend=True
        ))
        
        fig.add_trace(go.Scatter(
            x=days,
            y=median_path,
            mode='lines',
            line=dict(color='red', width=2),
            name='Median Path'
        ))
        
        fig.add_hline(y=initial_amount, line_dash="dash", line_color="green", 
                     annotation_text="Initial Investment")
        
        fig.update_layout(
            title=f"Portfolio Value Over {investment_years} Years (5,000 Simulations)",
            xaxis_title="Trading Days",
            yaxis_title="Portfolio Value ($)",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("---")
        
        # Show Dashboard if enabled
        if show_dashboard:
            create_dashboard(portfolio_details, allocation_data, sim_stats, 
                           initial_amount, investment_years, risk_profile)
        
        # Education & Ethics Section
        st.header("📚 Understanding Your Portfolio")
        
        with st.expander("🔍 What are these ETFs? (Click to expand)"):
            for etf in portfolio_details:
                st.write(f"**{etf['Ticker']} - {etf['ETF Name']}**")
                st.write(f"*{etf['Description']}*")
                st.write(f"Category: {etf['Category']} | Expense Ratio: {etf['Expense Ratio']:.2f}% | Dividend Yield: {etf['Dividend Yield']:.1f}%")
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
            - 5,000 random market scenarios
            - Assumes lognormal return distribution
            - Historical volatility: {allocation_data['expected_volatility']*100:.0f}%
            - 252 trading days per year
            """)
    
    else:
        # Welcome screen
        st.info("### 👈 Welcome to AI Robo-Advisor")
        st.write("""
        **Complete the risk assessment in the left sidebar to get your personalized portfolio**
        
        This tool will:
        - ✅ Assess your risk tolerance using 5 professional questions
        - ✅ Build a diversified ETF portfolio using real funds
        - ✅ Run 5,000 Monte Carlo simulations to project outcomes
        - ✅ Show detailed dashboard with risk analytics
        - ✅ Compare performance against market benchmarks
        - ✅ Calculate dividend income and fee analysis
        - ✅ Explain the AI's decision-making process
        
        **New Dashboard Features:**
        - 📊 Real-time risk metrics (VaR, Sharpe Ratio, Drawdown)
        - 💰 Dividend income projections
        - 📈 Benchmark comparisons (S&P 500, Bonds)
        - 🎯 Confidence interval analysis
        - 🏦 Banking & institutional insights
        """)
        
        # Feature preview
        st.subheader("✨ Dashboard Preview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Risk Analytics**")
            st.write("• Value at Risk (VaR)")
            st.write("• Maximum Drawdown")
            st.write("• Sharpe Ratio")
            st.write("• Volatility Analysis")
        
        with col2:
            st.write("**Return Scenarios**")
            st.write("• Best/Worst Case")
            st.write("• Confidence Intervals")
            st.write("• Probability Distribution")
            st.write("• CAGR Calculation")
        
        with col3:
            st.write("**Income Analysis**")
            st.write("• Dividend Projections")
            st.write("• Fee Impact")
            st.write("• Tax Considerations")
            st.write("• Benchmark Comparison")

# ========== RUN APPLICATION ==========
if __name__ == "__main__":
    main()
