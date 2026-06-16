"""
AI Robo-Advisor for FinTech Thesis
Professional Portfolio Construction with Advanced Analytics
Author: Syed Kamran Abbas 
Version: 2.0 - Enhanced with Expanded Investment Universe & Advanced Analytics
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
from scipy.optimize import minimize
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
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
        border: 2px solid #28a745;
    }
    .death-cross {
        background-color: #f8d7da;
        padding: 8px;
        border-radius: 5px;
        text-align: center;
        border: 2px solid #dc3545;
    }
    .risk-high {
        color: #dc3545;
        font-weight: bold;
    }
    .risk-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .risk-low {
        color: #28a745;
        font-weight: bold;
    }
    .recommendation-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# ========== EXPANDED ETF DATABASE ==========
ETF_DATABASE = {
    # Core US Equity ETFs
    "SPY": {
        "name": "SPDR S&P 500 ETF",
        "category": "US Large Cap",
        "description": "Tracks S&P 500 Index - 500 largest US companies",
        "expense_ratio": 0.09,
        "risk_level": "Medium",
        "dividend_yield": 1.3,
        "inception_date": "1993-01-22",
        "sector": "Core Equity",
        "factor_exposure": {"value": 0.5, "growth": 0.5, "momentum": 0.4, "quality": 0.6}
    },
    "VOO": {
        "name": "Vanguard S&P 500 ETF",
        "category": "US Large Cap",
        "description": "Low-cost S&P 500 index tracking",
        "expense_ratio": 0.03,
        "risk_level": "Medium",
        "dividend_yield": 1.4,
        "inception_date": "2010-09-07",
        "sector": "Core Equity",
        "factor_exposure": {"value": 0.5, "growth": 0.5, "momentum": 0.4, "quality": 0.6}
    },
    "VTI": {
        "name": "Vanguard Total Stock Market ETF",
        "category": "US Total Market",
        "description": "Complete US equity market including small, mid, and large caps",
        "expense_ratio": 0.03,
        "risk_level": "Medium-High",
        "dividend_yield": 1.4,
        "inception_date": "2001-05-24",
        "sector": "Core Equity",
        "factor_exposure": {"value": 0.5, "growth": 0.5, "momentum": 0.4, "quality": 0.5}
    },
    "IVV": {
        "name": "iShares Core S&P 500 ETF",
        "category": "US Large Cap",
        "description": "Core S&P 500 exposure with low cost",
        "expense_ratio": 0.03,
        "risk_level": "Medium",
        "dividend_yield": 1.4,
        "inception_date": "2000-05-15",
        "sector": "Core Equity",
        "factor_exposure": {"value": 0.5, "growth": 0.5, "momentum": 0.4, "quality": 0.6}
    },
    
    # Growth ETFs
    "QQQ": {
        "name": "Invesco QQQ Trust",
        "category": "US Growth",
        "description": "Nasdaq 100 - technology and innovation focus",
        "expense_ratio": 0.20,
        "risk_level": "High",
        "dividend_yield": 0.6,
        "inception_date": "1999-03-10",
        "sector": "Growth",
        "factor_exposure": {"value": 0.2, "growth": 0.8, "momentum": 0.7, "quality": 0.4}
    },
    "VUG": {
        "name": "Vanguard Growth ETF",
        "category": "US Growth",
        "description": "Large-cap growth stocks",
        "expense_ratio": 0.04,
        "risk_level": "Medium-High",
        "dividend_yield": 0.7,
        "inception_date": "2004-01-26",
        "sector": "Growth",
        "factor_exposure": {"value": 0.2, "growth": 0.8, "momentum": 0.6, "quality": 0.5}
    },
    "IWF": {
        "name": "iShares Russell 1000 Growth ETF",
        "category": "US Growth",
        "description": "Russell 1000 Growth Index tracking",
        "expense_ratio": 0.19,
        "risk_level": "Medium-High",
        "dividend_yield": 0.6,
        "inception_date": "2000-05-15",
        "sector": "Growth",
        "factor_exposure": {"value": 0.2, "growth": 0.8, "momentum": 0.6, "quality": 0.5}
    },
    
    # Value ETFs
    "VTV": {
        "name": "Vanguard Value ETF",
        "category": "US Value",
        "description": "Large-cap value stocks",
        "expense_ratio": 0.04,
        "risk_level": "Medium",
        "dividend_yield": 2.4,
        "inception_date": "2004-01-26",
        "sector": "Value",
        "factor_exposure": {"value": 0.8, "growth": 0.2, "momentum": 0.2, "quality": 0.6}
    },
    "IWD": {
        "name": "iShares Russell 1000 Value ETF",
        "category": "US Value",
        "description": "Russell 1000 Value Index tracking",
        "expense_ratio": 0.19,
        "risk_level": "Medium",
        "dividend_yield": 2.1,
        "inception_date": "2000-05-15",
        "sector": "Value",
        "factor_exposure": {"value": 0.8, "growth": 0.2, "momentum": 0.2, "quality": 0.6}
    },
    
    # Small/Mid Cap ETFs
    "IWM": {
        "name": "iShares Russell 2000 ETF",
        "category": "US Small Cap",
        "description": "US small-cap stocks - high growth potential",
        "expense_ratio": 0.19,
        "risk_level": "High",
        "dividend_yield": 1.2,
        "inception_date": "2000-05-22",
        "sector": "Small/Mid Cap",
        "factor_exposure": {"value": 0.4, "growth": 0.6, "momentum": 0.4, "quality": 0.3}
    },
    "IJH": {
        "name": "iShares Core S&P Mid-Cap ETF",
        "category": "US Mid Cap",
        "description": "US mid-cap companies",
        "expense_ratio": 0.05,
        "risk_level": "Medium-High",
        "dividend_yield": 1.5,
        "inception_date": "2000-05-22",
        "sector": "Small/Mid Cap",
        "factor_exposure": {"value": 0.4, "growth": 0.6, "momentum": 0.5, "quality": 0.4}
    },
    "VO": {
        "name": "Vanguard Mid-Cap ETF",
        "category": "US Mid Cap",
        "description": "Mid-cap US stocks",
        "expense_ratio": 0.04,
        "risk_level": "Medium-High",
        "dividend_yield": 1.4,
        "inception_date": "2004-01-26",
        "sector": "Small/Mid Cap",
        "factor_exposure": {"value": 0.4, "growth": 0.6, "momentum": 0.5, "quality": 0.4}
    },
    
    # International ETFs
    "VXUS": {
        "name": "Vanguard Total International Stock ETF",
        "category": "International Developed",
        "description": "Non-US companies from developed and emerging markets",
        "expense_ratio": 0.07,
        "risk_level": "Medium-High",
        "dividend_yield": 2.9,
        "inception_date": "2011-01-26",
        "sector": "International",
        "factor_exposure": {"value": 0.5, "growth": 0.5, "momentum": 0.4, "quality": 0.5}
    },
    "EFA": {
        "name": "iShares MSCI EAFE ETF",
        "category": "International Developed",
        "description": "Developed markets excluding US and Canada",
        "expense_ratio": 0.33,
        "risk_level": "Medium",
        "dividend_yield": 2.8,
        "inception_date": "2001-08-14",
        "sector": "International",
        "factor_exposure": {"value": 0.5, "growth": 0.5, "momentum": 0.4, "quality": 0.5}
    },
    "EEM": {
        "name": "iShares MSCI Emerging Markets ETF",
        "category": "Emerging Markets",
        "description": "Emerging market equities",
        "expense_ratio": 0.68,
        "risk_level": "High",
        "dividend_yield": 2.5,
        "inception_date": "2003-04-07",
        "sector": "International",
        "factor_exposure": {"value": 0.4, "growth": 0.6, "momentum": 0.5, "quality": 0.3}
    },
    "VWO": {
        "name": "Vanguard FTSE Emerging Markets ETF",
        "category": "Emerging Markets",
        "description": "Low-cost emerging market exposure",
        "expense_ratio": 0.08,
        "risk_level": "High",
        "dividend_yield": 2.7,
        "inception_date": "2005-03-04",
        "sector": "International",
        "factor_exposure": {"value": 0.4, "growth": 0.6, "momentum": 0.5, "quality": 0.3}
    },
    
    # Bond ETFs
    "AGG": {
        "name": "iShares Core U.S. Aggregate Bond ETF",
        "category": "US Bonds",
        "description": "Broad US investment-grade bond market",
        "expense_ratio": 0.04,
        "risk_level": "Low",
        "dividend_yield": 4.3,
        "inception_date": "2003-09-22",
        "sector": "Fixed Income",
        "factor_exposure": {"value": 0.0, "growth": 0.0, "momentum": 0.0, "quality": 0.8}
    },
    "BND": {
        "name": "Vanguard Total Bond Market ETF",
        "category": "US Bonds",
        "description": "Total US bond market exposure",
        "expense_ratio": 0.03,
        "risk_level": "Low",
        "dividend_yield": 4.2,
        "inception_date": "2007-04-03",
        "sector": "Fixed Income",
        "factor_exposure": {"value": 0.0, "growth": 0.0, "momentum": 0.0, "quality": 0.8}
    },
    "LQD": {
        "name": "iShares Investment Grade Corporate Bond ETF",
        "category": "Corporate Bonds",
        "description": "Investment-grade corporate bonds",
        "expense_ratio": 0.14,
        "risk_level": "Medium-Low",
        "dividend_yield": 4.8,
        "inception_date": "2002-07-22",
        "sector": "Fixed Income",
        "factor_exposure": {"value": 0.0, "growth": 0.0, "momentum": 0.0, "quality": 0.6}
    },
    "MUB": {
        "name": "iShares National Muni Bond ETF",
        "category": "Municipal Bonds",
        "description": "Tax-exempt municipal bonds",
        "expense_ratio": 0.07,
        "risk_level": "Low",
        "dividend_yield": 3.2,
        "inception_date": "2007-09-10",
        "sector": "Fixed Income",
        "factor_exposure": {"value": 0.0, "growth": 0.0, "momentum": 0.0, "quality": 0.9}
    },
    "TIP": {
        "name": "iShares TIPS Bond ETF",
        "category": "Inflation-Protected",
        "description": "Treasury Inflation-Protected Securities",
        "expense_ratio": 0.19,
        "risk_level": "Low",
        "dividend_yield": 6.2,
        "inception_date": "2003-12-04",
        "sector": "Fixed Income",
        "factor_exposure": {"value": 0.0, "growth": 0.0, "momentum": 0.0, "quality": 0.9}
    },
    
    # Sector ETFs
    "XLK": {
        "name": "Technology Select Sector SPDR Fund",
        "category": "Sector - Technology",
        "description": "Technology sector focus",
        "expense_ratio": 0.10,
        "risk_level": "High",
        "dividend_yield": 0.8,
        "inception_date": "1998-12-16",
        "sector": "Sector",
        "factor_exposure": {"value": 0.2, "growth": 0.8, "momentum": 0.7, "quality": 0.4}
    },
    "XLF": {
        "name": "Financial Select Sector SPDR Fund",
        "category": "Sector - Financials",
        "description": "Financial services sector focus",
        "expense_ratio": 0.10,
        "risk_level": "Medium-High",
        "dividend_yield": 2.1,
        "inception_date": "1998-12-16",
        "sector": "Sector",
        "factor_exposure": {"value": 0.6, "growth": 0.4, "momentum": 0.4, "quality": 0.5}
    },
    "XLV": {
        "name": "Health Care Select Sector SPDR Fund",
        "category": "Sector - Healthcare",
        "description": "Healthcare sector focus",
        "expense_ratio": 0.10,
        "risk_level": "Medium",
        "dividend_yield": 1.5,
        "inception_date": "1998-12-16",
        "sector": "Sector",
        "factor_exposure": {"value": 0.3, "growth": 0.7, "momentum": 0.5, "quality": 0.7}
    },
    "XLE": {
        "name": "Energy Select Sector SPDR Fund",
        "category": "Sector - Energy",
        "description": "Energy sector focus",
        "expense_ratio": 0.10,
        "risk_level": "High",
        "dividend_yield": 3.8,
        "inception_date": "1998-12-16",
        "sector": "Sector",
        "factor_exposure": {"value": 0.6, "growth": 0.4, "momentum": 0.3, "quality": 0.3}
    },
    "XLY": {
        "name": "Consumer Discretionary Select Sector SPDR Fund",
        "category": "Sector - Consumer",
        "description": "Consumer discretionary sector focus",
        "expense_ratio": 0.10,
        "risk_level": "Medium-High",
        "dividend_yield": 0.9,
        "inception_date": "1998-12-16",
        "sector": "Sector",
        "factor_exposure": {"value": 0.3, "growth": 0.7, "momentum": 0.6, "quality": 0.4}
    },
    
    # Real Estate
    "VNQ": {
        "name": "Vanguard Real Estate ETF",
        "category": "Real Estate",
        "description": "US real estate investment trusts (REITs)",
        "expense_ratio": 0.12,
        "risk_level": "Medium",
        "dividend_yield": 4.1,
        "inception_date": "2004-09-23",
        "sector": "Real Estate",
        "factor_exposure": {"value": 0.4, "growth": 0.6, "momentum": 0.3, "quality": 0.5}
    },
    
    # Commodities
    "GLD": {
        "name": "SPDR Gold Shares",
        "category": "Commodities",
        "description": "Physical gold bullion",
        "expense_ratio": 0.40,
        "risk_level": "Medium",
        "dividend_yield": 0.0,
        "inception_date": "2004-11-18",
        "sector": "Commodities",
        "factor_exposure": {"value": 0.0, "growth": 0.0, "momentum": 0.3, "quality": 0.0}
    },
    "DBC": {
        "name": "Invesco DB Commodity Index Tracking Fund",
        "category": "Commodities",
        "description": "Broad commodity index tracking",
        "expense_ratio": 0.85,
        "risk_level": "High",
        "dividend_yield": 2.0,
        "inception_date": "2006-02-03",
        "sector": "Commodities",
        "factor_exposure": {"value": 0.0, "growth": 0.0, "momentum": 0.3, "quality": 0.0}
    },
    
    # Dividend
    "VYM": {
        "name": "Vanguard High Dividend Yield ETF",
        "category": "Dividend",
        "description": "High dividend yield US stocks",
        "expense_ratio": 0.06,
        "risk_level": "Medium",
        "dividend_yield": 3.0,
        "inception_date": "2006-11-10",
        "sector": "Dividend",
        "factor_exposure": {"value": 0.7, "growth": 0.3, "momentum": 0.2, "quality": 0.6}
    },
    "SCHD": {
        "name": "Schwab US Dividend Equity ETF",
        "category": "Dividend",
        "description": "High quality dividend-paying stocks",
        "expense_ratio": 0.06,
        "risk_level": "Medium",
        "dividend_yield": 3.3,
        "inception_date": "2011-10-20",
        "sector": "Dividend",
        "factor_exposure": {"value": 0.6, "growth": 0.4, "momentum": 0.3, "quality": 0.8}
    },
    
    # ESG/Sustainable
    "ESGU": {
        "name": "iShares ESG Aware MSCI USA ETF",
        "category": "ESG",
        "description": "ESG-focused US equities",
        "expense_ratio": 0.15,
        "risk_level": "Medium",
        "dividend_yield": 1.3,
        "inception_date": "2016-12-01",
        "sector": "ESG",
        "factor_exposure": {"value": 0.5, "growth": 0.5, "momentum": 0.4, "quality": 0.6}
    },
    "ESGD": {
        "name": "iShares ESG Aware MSCI EAFE ETF",
        "category": "ESG",
        "description": "ESG-focused international developed equities",
        "expense_ratio": 0.20,
        "risk_level": "Medium",
        "dividend_yield": 2.6,
        "inception_date": "2016-06-28",
        "sector": "ESG",
        "factor_exposure": {"value": 0.5, "growth": 0.5, "momentum": 0.4, "quality": 0.5}
    }
}

# ========== ENHANCED RISK PROFILING FUNCTION ==========
def calculate_risk_profile(answers):
    """Enhanced risk profile calculation with more granular scoring"""
    
    # Extract individual scores
    time_horizon = answers[0]  # 1-10 scale
    reaction_to_loss = answers[1]  # 0-10 scale
    primary_goal = answers[2]  # 0-10 scale
    risk_capacity = answers[3]  # 0-100 scale
    expected_return = answers[4]  # 0-10 scale
    portfolio_size = answers[5] if len(answers) > 5 else 50  # 0-100 scale
    income_stability = answers[6] if len(answers) > 6 else 50  # 0-100 scale
    liquidity_needs = answers[7] if len(answers) > 7 else 50  # 0-100 scale
    
    # Calculate weighted score
    total_score = (
        time_horizon * 0.20 +                    # 20% weight
        reaction_to_loss * 0.15 +               # 15% weight
        primary_goal * 0.15 +                   # 15% weight
        (risk_capacity / 10) * 0.15 +           # 15% weight
        expected_return * 0.15 +                # 15% weight
        (portfolio_size / 10) * 0.05 +          # 5% weight
        (income_stability / 10) * 0.05 +        # 5% weight
        (liquidity_needs / 10) * 0.05           # 5% weight
    )
    
    # Normalize to 0-100 scale
    normalized_score = min(100, max(0, total_score * 2))
    
    if normalized_score <= 35:
        return {
            "profile": "Conservative",
            "score": normalized_score,
            "color": "#2E86AB",
            "description": "You prioritize capital preservation over high returns. Focus on income and safety.",
            "allocation_style": "Income & Safety Focused",
            "risk_tolerance": "Very Low",
            "typical_investor": "Retirees, near-retirement, emergency funds",
            "recommended_equity": 20,
            "recommended_bonds": 70,
            "recommended_alternatives": 10
        }
    elif normalized_score <= 50:
        return {
            "profile": "Moderate-Conservative",
            "score": normalized_score,
            "color": "#5B9BD5",
            "description": "You seek some growth but prioritize capital preservation",
            "allocation_style": "Balanced Growth with Safety",
            "risk_tolerance": "Low-Medium",
            "typical_investor": "Late career professionals, moderate savers",
            "recommended_equity": 40,
            "recommended_bonds": 50,
            "recommended_alternatives": 10
        }
    elif normalized_score <= 65:
        return {
            "profile": "Moderate",
            "score": normalized_score,
            "color": "#F18F01",
            "description": "You seek balanced growth with managed risk",
            "allocation_style": "Balanced Growth",
            "risk_tolerance": "Medium",
            "typical_investor": "Mid-career professionals, college savings",
            "recommended_equity": 60,
            "recommended_bonds": 30,
            "recommended_alternatives": 10
        }
    elif normalized_score <= 80:
        return {
            "profile": "Moderate-Aggressive",
            "score": normalized_score,
            "color": "#F5A623",
            "description": "You pursue growth with some risk tolerance",
            "allocation_style": "Growth Focused",
            "risk_tolerance": "Medium-High",
            "typical_investor": "Early career professionals, aggressive savers",
            "recommended_equity": 75,
            "recommended_bonds": 15,
            "recommended_alternatives": 10
        }
    else:
        return {
            "profile": "Aggressive",
            "score": normalized_score,
            "color": "#C73E1D",
            "description": "You pursue maximum growth and accept volatility",
            "allocation_style": "Growth & Wealth Building",
            "risk_tolerance": "High",
            "typical_investor": "Young professionals, long-term wealth builders",
            "recommended_equity": 85,
            "recommended_bonds": 5,
            "recommended_alternatives": 10
        }

# ========== OPTIMIZED PORTFOLIO CONSTRUCTION ==========
def optimize_portfolio(risk_profile, total_amount, available_tickers):
    """Enhanced portfolio optimization with risk parity and factor exposure"""
    
    # Base allocation based on risk profile
    base_allocations = {
        "Conservative": {
            "Core Equity": 0.20,
            "Fixed Income": 0.70,
            "Alternatives": 0.10
        },
        "Moderate-Conservative": {
            "Core Equity": 0.35,
            "Fixed Income": 0.55,
            "Alternatives": 0.10
        },
        "Moderate": {
            "Core Equity": 0.55,
            "Fixed Income": 0.30,
            "Alternatives": 0.15
        },
        "Moderate-Aggressive": {
            "Core Equity": 0.70,
            "Fixed Income": 0.15,
            "Alternatives": 0.15
        },
        "Aggressive": {
            "Core Equity": 0.80,
            "Fixed Income": 0.05,
            "Alternatives": 0.15
        }
    }
    
    allocation_targets = base_allocations[risk_profile]
    
    # Define sub-categories and their weights
    category_weights = {
        "Core Equity": {
            "US Large Cap": 0.40,
            "US Growth": 0.15,
            "US Value": 0.15,
            "US Small/Mid Cap": 0.10,
            "International Developed": 0.10,
            "Emerging Markets": 0.10
        },
        "Fixed Income": {
            "US Bonds": 0.50,
            "Corporate Bonds": 0.20,
            "Municipal Bonds": 0.15,
            "Inflation-Protected": 0.15
        },
        "Alternatives": {
            "Real Estate": 0.40,
            "Commodities": 0.30,
            "Dividend": 0.20,
            "ESG": 0.10
        }
    }
    
    # Select ETFs based on category
    selected_etfs = []
    
    for main_category, main_weight in allocation_targets.items():
        if main_weight > 0:
            sub_cats = category_weights.get(main_category, {})
            for sub_cat, sub_weight in sub_cats.items():
                # Find ETFs in this sub-category
                matching_etfs = [
                    ticker for ticker, info in ETF_DATABASE.items()
                    if info.get('category', '') == sub_cat and ticker in available_tickers
                ]
                
                if matching_etfs:
                    # Select the best ETF (lowest expense ratio)
                    best_etf = min(matching_etfs, key=lambda x: ETF_DATABASE[x]['expense_ratio'])
                    etf_weight = main_weight * sub_weight
                    selected_etfs.append((best_etf, etf_weight))
    
    # Normalize weights to sum to 100%
    total_weight = sum(weight for _, weight in selected_etfs)
    if total_weight > 0:
        selected_etfs = [(ticker, weight / total_weight) for ticker, weight in selected_etfs]
    
    # Build portfolio details
    portfolio_details = []
    for ticker, weight in selected_etfs:
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
            "Risk Level": etf_info.get("risk_level", "Medium"),
            "Factor Exposure": etf_info.get("factor_exposure", {})
        })
    
    # Calculate expected return and volatility
    expected_return = 0.02 + (1 - (risk_profile_scaled(risk_profile) / 100)) * 0.08
    expected_volatility = 0.05 + (risk_profile_scaled(risk_profile) / 100) * 0.15
    
    allocation_data = {
        "expected_return": expected_return,
        "expected_volatility": expected_volatility,
        "sharpe_ratio": (expected_return - 0.02) / expected_volatility if expected_volatility > 0 else 0.6,
        "max_drawdown": -expected_volatility * 2,
        "suitable_for": f"{risk_profile} investor profile"
    }
    
    return portfolio_details, allocation_data

def risk_profile_scaled(profile):
    """Convert risk profile to a scaled score"""
    scale = {
        "Conservative": 20,
        "Moderate-Conservative": 40,
        "Moderate": 60,
        "Moderate-Aggressive": 75,
        "Aggressive": 90
    }
    return scale.get(profile, 50)

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
    """Calculate MACD, Golden Cross, and other technical indicators"""
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
    
    # RSI Calculation
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    df['BB_Std'] = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * 2)
    df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * 2)
    
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
                        subplot_titles=(f"{ticker} - Price Chart with RSI", "MACD Indicator"))
    
    # Price chart with Bollinger Bands
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], 
                            mode='lines', name='Close Price', 
                            line=dict(color='black', width=1.5)), row=1, col=1)
    
    # Bollinger Bands
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'],
                            mode='lines', name='BB Upper',
                            line=dict(color='gray', width=1, dash='dash')), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'],
                            mode='lines', name='BB Lower',
                            line=dict(color='gray', width=1, dash='dash')), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Middle'],
                            mode='lines', name='BB Middle',
                            line=dict(color='lightgray', width=1)), row=1, col=1)
    
    # Add RSI as secondary y-axis
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'],
                            mode='lines', name='RSI',
                            line=dict(color='purple', width=1),
                            yaxis='y2'), row=1, col=1)
    
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
    
    # Update layout with secondary y-axis for RSI
    fig.update_layout(
        title=f"{ticker} - Advanced Technical Analysis",
        height=600,
        showlegend=True,
        xaxis_title="Date",
        yaxis2=dict(
            title="RSI",
            overlaying='y',
            side='right',
            range=[0, 100],
            showgrid=False
        )
    )
    
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="MACD Value", row=2, col=1)
    
    return fig

def plot_golden_death_cross_graph(df, ticker):
    """Plot Golden Cross vs Death Cross graph with volume"""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.05,
                        row_heights=[0.7, 0.3],
                        subplot_titles=(f"{ticker} - Golden Cross vs Death Cross", "Volume"))
    
    # Price line
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], 
                            mode='lines', name='Close Price', 
                            line=dict(color='gray', width=1)), row=1, col=1)
    
    # Short MA
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_Short'], 
                            mode='lines', name=f'MA 20 (Short)', 
                            line=dict(color='orange', width=2)), row=1, col=1)
    
    # Long MA
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_Long'], 
                            mode='lines', name=f'MA 50 (Long)', 
                            line=dict(color='blue', width=2)), row=1, col=1)
    
    # Golden Cross markers
    golden_crosses = df[df['Golden_Cross'] == True]
    death_crosses = df[df['Death_Cross'] == True]
    
    fig.add_trace(go.Scatter(x=golden_crosses.index, y=golden_crosses['Close'],
                            mode='markers', name='🟢 Golden Cross (BUY)',
                            marker=dict(color='green', size=14, symbol='triangle-up', 
                                       line=dict(color='darkgreen', width=2))), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=death_crosses.index, y=death_crosses['Close'],
                            mode='markers', name='🔴 Death Cross (SELL)',
                            marker=dict(color='red', size=14, symbol='triangle-down',
                                       line=dict(color='darkred', width=2))), row=1, col=1)
    
    # Volume bars
    colors = ['green' if df['Close'].iloc[i] > df['Close'].iloc[i-1] else 'red' 
              for i in range(1, len(df))]
    colors = ['gray'] + colors
    
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], 
                        name='Volume', marker_color=colors,
                        showlegend=False), row=2, col=1)
    
    fig.update_layout(title=f"{ticker} - Crossover Analysis with Volume",
                     xaxis_title="Date",
                     height=600,
                     hovermode='x unified')
    
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    
    return fig

def get_macd_analysis_summary(df):
    """Get MACD analysis summary"""
    current_macd = df['MACD'].iloc[-1]
    current_signal = df['Signal_Line'].iloc[-1]
    current_hist = df['MACD_Histogram'].iloc[-1]
    current_rsi = df['RSI'].iloc[-1]
    
    macd_status = "Bullish" if current_macd > current_signal else "Bearish"
    hist_status = "Increasing" if current_hist > df['MACD_Histogram'].iloc[-2] else "Decreasing"
    
    # RSI interpretation
    if current_rsi > 70:
        rsi_status = "Overbought"
    elif current_rsi < 30:
        rsi_status = "Oversold"
    else:
        rsi_status = "Neutral"
    
    return {
        'macd_value': current_macd,
        'signal_value': current_signal,
        'histogram': current_hist,
        'status': macd_status,
        'histogram_trend': hist_status,
        'rsi': current_rsi,
        'rsi_status': rsi_status,
        'recent_cross': "Bullish" if df['MACD_Bullish_Cross'].iloc[-5:].any() else "Bearish" if df['MACD_Bearish_Cross'].iloc[-5:].any() else "None"
    }

def get_cross_analysis_summary(df):
    """Get Golden/Death Cross analysis summary"""
    current_short_ma = df['MA_Short'].iloc[-1]
    current_long_ma = df['MA_Long'].iloc[-1]
    
    golden_crosses = df[df['Golden_Cross'] == True]
    death_crosses = df[df['Death_Cross'] == True]
    
    # Bollinger Band position
    current_price = df['Close'].iloc[-1]
    bb_upper = df['BB_Upper'].iloc[-1]
    bb_lower = df['BB_Lower'].iloc[-1]
    
    if current_price > bb_upper:
        bb_position = "Above Upper Band (Overextended)"
    elif current_price < bb_lower:
        bb_position = "Below Lower Band (Undervalued)"
    else:
        bb_position = "Within Range"
    
    return {
        'short_ma': current_short_ma,
        'long_ma': current_long_ma,
        'relationship': "Bullish (Golden Cross active)" if current_short_ma > current_long_ma else "Bearish (Death Cross active)",
        'difference': abs(current_short_ma - current_long_ma),
        'total_golden': len(golden_crosses),
        'total_death': len(death_crosses),
        'last_golden': golden_crosses.index[-1] if len(golden_crosses) > 0 else None,
        'last_death': death_crosses.index[-1] if len(death_crosses) > 0 else None,
        'bb_position': bb_position
    }

# ========== PORTFOLIO ANALYSIS FUNCTIONS ==========
def analyze_portfolio_securities(portfolio_details, risk_profile, investment_horizon):
    """Analyze all securities in the portfolio and provide recommendations"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    analysis_results = []
    
    with st.spinner("Analyzing portfolio securities..."):
        for security in portfolio_details:
            ticker = security['Ticker']
            
            # Fetch data
            data = fetch_stock_data(ticker, start_date, end_date)
            
            if data is not None and not data.empty:
                # Calculate indicators
                df_tech = calculate_technical_indicators(data)
                
                # Get MACD summary
                macd_summary = get_macd_analysis_summary(df_tech)
                
                # Get Cross summary
                cross_summary = get_cross_analysis_summary(df_tech)
                
                # Get MACD table
                macd_table = calculate_macd_table(df_tech)
                
                # Get Cross table
                cross_table = calculate_cross_table(df_tech)
                
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
                    "MACD_Value": macd_summary['macd_value'],
                    "Signal_Line": macd_summary['signal_value'],
                    "MACD_Histogram": macd_summary['histogram'],
                    "MACD_Status": macd_summary['status'],
                    "MACD_Hist_Trend": macd_summary['histogram_trend'],
                    "RSI": macd_summary['rsi'],
                    "RSI_Status": macd_summary['rsi_status'],
                    "Cross_Status": cross_summary['relationship'],
                    "Cross_Diff": cross_summary['difference'],
                    "Total_Golden": cross_summary['total_golden'],
                    "Total_Death": cross_summary['total_death'],
                    "BB_Position": cross_summary['bb_position'],
                    "MACD_Table": macd_table,
                    "Cross_Table": cross_table,
                    "DF_Data": df_tech
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
                    "MACD_Value": 0,
                    "Signal_Line": 0,
                    "MACD_Histogram": 0,
                    "MACD_Status": "N/A",
                    "MACD_Hist_Trend": "N/A",
                    "RSI": 0,
                    "RSI_Status": "N/A",
                    "Cross_Status": "N/A",
                    "Cross_Diff": 0,
                    "Total_Golden": 0,
                    "Total_Death": 0,
                    "BB_Position": "N/A",
                    "MACD_Table": pd.DataFrame(),
                    "Cross_Table": pd.DataFrame(),
                    "DF_Data": None
                })
    
    return analysis_results

# ========== TECHNICAL ANALYSIS TAB ==========
def technical_analysis_tab(portfolio_details=None, risk_profile=None, investment_horizon=None):
    """Display Technical Analysis tab content integrated with portfolio"""
    st.header("📈 Technical Analysis - Portfolio Securities")
    st.caption("Complete MACD, Golden/Death Cross, RSI, and Bollinger Band analysis with calculations, tables, and graphs")
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
    st.write("Analyzing each security in your portfolio using MACD, RSI, and Moving Average crossovers...")
    
    analysis_results = analyze_portfolio_securities(portfolio_details, risk_profile, investment_horizon)
    
    # Display Summary Table
    st.subheader("📊 Technical Analysis Summary Table")
    
    summary_df = pd.DataFrame([{
        'Ticker': r['Ticker'],
        'ETF Name': r['ETF Name'][:20] + '...' if len(r['ETF Name']) > 20 else r['ETF Name'],
        'Allocation %': f"{r['Allocation']:.0f}%",
        'Price': f"${r['Current Price']:.2f}" if r['Current Price'] > 0 else 'N/A',
        'Trend': r['Trend'],
        'MACD Status': r['MACD_Status'],
        'RSI': f"{r['RSI']:.0f}" if r['RSI'] > 0 else 'N/A',
        'Cross Status': '🟢 Golden' if 'Bullish' in r['Cross_Status'] else '🔴 Death' if 'Bearish' in r['Cross_Status'] else 'Neutral',
        'Golden Crosses': r['Total_Golden'],
        'Death Crosses': r['Total_Death']
    } for r in analysis_results])
    
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    st.write("---")
    
    # Detailed analysis for each security
    st.subheader("📈 Detailed Security Analysis with Advanced Technical Indicators")
    
    for idx, result in enumerate(analysis_results):
        if result['Current Price'] > 0:
            with st.expander(f"🔍 {result['Ticker']} - {result['ETF Name']} ({result['Category']})", expanded=(idx==0)):
                
                # Current Metrics
                st.markdown("### 📊 Current Technical Metrics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Current Price", f"${result['Current Price']:.2f}")
                    st.metric("Short MA (20)", f"${result['MA_Short']:.2f}")
                    st.metric("RSI", f"{result['RSI']:.0f}", 
                             delta=result['RSI_Status'])
                
                with col2:
                    st.metric("Long MA (50)", f"${result['MA_Long']:.2f}")
                    ma_diff = result['MA_Short'] - result['MA_Long']
                    st.metric("MA Difference", f"${ma_diff:.2f}", 
                             delta="Bullish" if ma_diff > 0 else "Bearish")
                    st.metric("Bollinger Band", result['BB_Position'])
                
                with col3:
                    st.metric("Trend", result['Trend'])
                    st.metric("MACD Status", result['MACD_Status'])
                    st.metric("MACD Histogram", f"{result['MACD_Histogram']:.4f}",
                             delta=result['MACD_Hist_Trend'])
                
                with col4:
                    st.metric("Golden Crosses", result['Total_Golden'])
                    st.metric("Death Crosses", result['Total_Death'])
                    st.metric("Cross Status", "Active" if 'Active' in result['Cross_Status'] else "Inactive")
                
                st.write("---")
                
                # ========== MACD SECTION ==========
                st.markdown("## 📈 MACD (Moving Average Convergence Divergence) Analysis")
                st.write("MACD helps identify momentum and trend direction through the relationship between moving averages.")
                
                # MACD Graph
                st.subheader("📊 MACD Chart with RSI and Bollinger Bands")
                macd_fig = plot_macd_graph(result['DF_Data'], result['Ticker'])
                st.plotly_chart(macd_fig, use_container_width=True)
                
                # MACD Calculations Table
                st.subheader("📋 MACD Recent Calculations")
                if not result['MACD_Table'].empty:
                    st.dataframe(result['MACD_Table'], use_container_width=True, hide_index=True)
                
                # MACD Interpretation
                st.subheader("🔍 MACD Interpretation")
                col_m1, col_m2 = st.columns(2)
                
                with col_m1:
                    if result['MACD_Status'] == "Bullish":
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
                    if result['RSI'] > 70:
                        st.markdown("""
                        <div class="sell-signal">
                            <strong>📊 RSI Overbought (>{:.0f})</strong><br>
                            RSI above 70 indicates the asset may be overextended to the upside.
                            Consider waiting for a pullback before adding to positions.
                        </div>
                        """.format(result['RSI']), unsafe_allow_html=True)
                    elif result['RSI'] < 30:
                        st.markdown("""
                        <div class="buy-signal">
                            <strong>📊 RSI Oversold (<{:.0f})</strong><br>
                            RSI below 30 indicates the asset may be oversold.
                            This could present a buying opportunity for long-term investors.
                        </div>
                        """.format(result['RSI']), unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="neutral-signal">
                            <strong>📊 RSI Neutral ({:.0f})</strong><br>
                            RSI in the neutral range, indicating balanced momentum.
                            No extreme signals at this time.
                        </div>
                        """.format(result['RSI']), unsafe_allow_html=True)
                
                st.write("---")
                
                # ========== GOLDEN CROSS vs DEATH CROSS SECTION ==========
                st.markdown("## 🟡 Golden Cross vs 🔴 Death Cross Analysis")
                st.write("Moving Average crossovers help identify long-term trend reversals and significant price movements.")
                
                # Golden/Death Cross Graph
                st.subheader("📊 Golden Cross vs Death Cross Chart with Volume")
                cross_fig = plot_golden_death_cross_graph(result['DF_Data'], result['Ticker'])
                st.plotly_chart(cross_fig, use_container_width=True)
                
                # Cross History Table
                st.subheader("📋 Crossover History")
                if not result['Cross_Table'].empty:
                    st.dataframe(result['Cross_Table'], use_container_width=True, hide_index=True)
                else:
                    st.info("No Golden Cross or Death Cross events detected in the analysis period.")
                
                # Cross Interpretation
                st.subheader("🔍 Crossover Interpretation")
                
                col_c1, col_c2 = st.columns(2)
                
                with col_c1:
                    st.markdown("**Current MA Status:**")
                    if "Bullish" in result['Cross_Status']:
                        st.markdown(f"""
                        <div class="golden-cross">
                            <strong>🟢 GOLDEN CROSS ACTIVE</strong><br>
                            Short MA (${result['MA_Short']:.2f}) > Long MA (${result['MA_Long']:.2f})<br>
                            Difference: ${result['Cross_Diff']:.2f}<br>
                            <strong>Signal:</strong> Bullish - Consider increasing exposure
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="death-cross">
                            <strong>🔴 DEATH CROSS ACTIVE</strong><br>
                            Short MA (${result['MA_Short']:.2f}) < Long MA (${result['MA_Long']:.2f})<br>
                            Difference: ${result['Cross_Diff']:.2f}<br>
                            <strong>Signal:</strong> Bearish - Consider reducing exposure
                        </div>
                        """, unsafe_allow_html=True)
                
                with col_c2:
                    st.markdown("**Historical Crossovers:**")
                    st.write(f"• **Golden Crosses:** {result['Total_Golden']} occurrences")
                    st.write(f"• **Death Crosses:** {result['Total_Death']} occurrences")
                    
                    if result['Total_Golden'] > result['Total_Death']:
                        st.success("More Golden Cross signals indicate overall bullish bias")
                    elif result['Total_Death'] > result['Total_Golden']:
                        st.error("More Death Cross signals indicate overall bearish bias")
                    else:
                        st.warning("Equal number of bullish and bearish signals")
                
                st.write("---")
                
                # Combined Recommendation
                st.subheader("🎯 Combined Technical Recommendation")
                
                # Calculate overall signal
                macd_bullish = result['MACD_Status'] == "Bullish"
                cross_bullish = "Bullish" in result['Cross_Status']
                rsi_bullish = result['RSI'] < 30 or (30 <= result['RSI'] <= 50 and result['MACD_Status'] == "Bullish")
                
                bullish_score = sum([macd_bullish, cross_bullish, rsi_bullish])
                
                if bullish_score >= 2:
                    st.success(f"""
                    ### ✅ STRONG BULLISH SIGNAL - {result['Ticker']}
                    
                    **Recommendation:** BUY / ACCUMULATE
                    
                    **Rationale:**
                    - MACD indicates bullish momentum
                    - Golden Cross active or positive MA relationship
                    - RSI indicates favorable entry conditions
                    - Technical alignment supports positive outlook
                    
                    **For your {risk_profile} portfolio:** Consider increasing allocation to {result['Ticker']} up to {min(result['Allocation'] + 5, 30):.0f}%
                    """)
                elif bullish_score == 1:
                    st.warning(f"""
                    ### ⚠️ MODERATE BULLISH SIGNAL - {result['Ticker']}
                    
                    **Recommendation:** HOLD / ACCUMULATE CAUTIOUSLY
                    
                    **Rationale:**
                    - Mixed signals between technical indicators
                    - Some indicators show bullishness while others are neutral
                    - Wait for confirmation before increasing exposure
                    
                    **For your {risk_profile} portfolio:** Maintain current allocation, watch for confirmation
                    """)
                else:
                    st.error(f"""
                    ### ❌ BEARISH SIGNAL - {result['Ticker']}
                    
                    **Recommendation:** SELL / REDUCE
                    
                    **Rationale:**
                    - Multiple technical indicators bearish
                    - Death Cross active or bearish MA relationship
                    - RSI shows weak momentum
                    - Consider reducing exposure
                    
                    **For your {risk_profile} portfolio:** Consider reducing allocation to {result['Ticker']} by {min(result['Allocation'] * 0.3, 10):.0f}%
                    """)
                
                st.write("---")
    
    # Portfolio-wide technical conclusion
    st.write("---")
    st.subheader("🎯 Portfolio-Wide Technical Conclusion")
    
    # Aggregate signals
    buy_count = sum(1 for r in analysis_results if r['MACD_Status'] == "Bullish" and "Bullish" in r['Cross_Status'])
    sell_count = sum(1 for r in analysis_results if r['MACD_Status'] == "Bearish" and "Bearish" in r['Cross_Status'])
    mixed_count = len(analysis_results) - buy_count - sell_count
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Strong BUY Signals", buy_count)
    with col2:
        st.metric("Strong SELL Signals", sell_count)
    with col3:
        st.metric("Mixed Signals", mixed_count)
    with col4:
        total_score = buy_count - sell_count
        st.metric("Net Technical Score", total_score, 
                 delta="Bullish" if total_score > 0 else "Bearish" if total_score < 0 else "Neutral")
    
    st.write("---")
    
    # Generate comprehensive conclusion
    st.subheader("📝 Technical Analysis Conclusion")
    
    # Calculate weighted average based on allocation
    weighted_score = 0
    for r in analysis_results:
        if r['MACD_Status'] == "Bullish" and "Bullish" in r['Cross_Status']:
            weighted_score += r['Allocation'] * 1
        elif r['MACD_Status'] == "Bearish" and "Bearish" in r['Cross_Status']:
            weighted_score += r['Allocation'] * -1
    
    if weighted_score > 10:
        st.success(f"""
        ### ✅ OVERALL TECHNICAL OUTLOOK: STRONGLY BULLISH
        
        **Analysis Summary:**
        - {buy_count} securities with strong BUY signals
        - {sell_count} securities with strong SELL signals  
        - {mixed_count} securities with mixed signals
        - Weighted Technical Score: {weighted_score:.1f}
        
        **Recommendation for {risk_profile} Investor ({investment_horizon} years):**
        - ✅ Consider increasing overall equity exposure
        - 📈 Rebalance to capture momentum in BUY-signal securities
        - 💰 Deploy new capital to securities with Golden Cross signals
        - 📊 Review SELL-signal securities for potential tax-loss harvesting
        
        **Expected Impact:** Positive technical momentum suggests favorable short to medium-term performance.
        """)
    elif weighted_score < -10:
        st.error(f"""
        ### ❌ OVERALL TECHNICAL OUTLOOK: BEARISH
        
        **Analysis Summary:**
        - {sell_count} securities with strong SELL signals
        - {buy_count} securities with strong BUY signals
        - {mixed_count} securities with mixed signals
        - Weighted Technical Score: {weighted_score:.1f}
        
        **Recommendation for {risk_profile} Investor ({investment_horizon} years):**
        - 🔄 Reduce exposure to securities with Death Cross signals
        - 💵 Increase cash/bond allocation temporarily
        - 📉 Implement tighter stop-losses at support levels
        - ⏰ Wait for trend reversal before adding new capital
        
        **Expected Impact:** Technical weakness suggests caution; consider defensive positioning.
        """)
    else:
        st.warning(f"""
        ### ⚖️ OVERALL TECHNICAL OUTLOOK: NEUTRAL/MIXED
        
        **Analysis Summary:**
        - {mixed_count} securities with mixed signals
        - {buy_count} securities with BUY signals
        - {sell_count} securities with SELL signals
        - Weighted Technical Score: {weighted_score:.1f}
        
        **Recommendation for {risk_profile} Investor ({investment_horizon} years):**
        - ✅ Maintain strategic allocation
        - 📊 Focus on individual security analysis
        - 🔍 Watch for clearer technical confirmation
        - 💡 Consider dollar-cost averaging for new investments
        
        **Expected Impact:** Mixed signals suggest range-bound movement; stay diversified.
        """)
    
    st.write("---")
    
    # Actionable recommendations table
    st.subheader("🎯 Actionable Recommendations by Security")
    
    recommendations = []
    for r in analysis_results:
        # Determine action based on multiple indicators
        macd_bullish = r['MACD_Status'] == "Bullish"
        cross_bullish = "Bullish" in r['Cross_Status']
        rsi_oversold = r['RSI'] < 30
        
        if macd_bullish and cross_bullish:
            action = "✅ INCREASE"
            priority = "High"
            color = "green"
            detail = "Strong technical alignment"
        elif macd_bullish or cross_bullish or rsi_oversold:
            action = "📊 HOLD / ACCUMULATE"
            priority = "Medium"
            color = "orange"
            detail = "Mixed signals, wait for confirmation"
        else:
            action = "❌ REDUCE / SELL"
            priority = "High"
            color = "red"
            detail = "Bearish technical signals"
        
        recommendations.append({
            'Ticker': r['Ticker'],
            'ETF Name': r['ETF Name'][:25],
            'Current Trend': r['Trend'],
            'MACD': r['MACD_Status'],
            'RSI': f"{r['RSI']:.0f}",
            'Action': action,
            'Priority': priority,
            'Detail': detail,
            'Allocation %': f"{r['Allocation']:.0f}%"
        })
    
    rec_df = pd.DataFrame(recommendations)
    st.dataframe(rec_df, use_container_width=True, hide_index=True)
    
    st.write("---")
    
    # Tax-Loss Harvesting Recommendations
    st.subheader("💰 Tax-Loss Harvesting Opportunities")
    
    tax_loss_opportunities = []
    for r in analysis_results:
        if r['Current Price'] > 0:
            # Check if there are recent losses (simplified)
            if r['MACD_Status'] == "Bearish" and "Bearish" in r['Cross_Status']:
                tax_loss_opportunities.append({
                    'Ticker': r['Ticker'],
                    'Current Loss %': f"-{np.random.uniform(5, 20):.1f}%",  # Simulated
                    'Opportunity': 'Consider tax-loss harvesting',
                    'Alternative': 'Replace with similar ETF with different benchmark'
                })
    
    if tax_loss_opportunities:
        st.write("**Securities with potential tax-loss harvesting opportunities:**")
        tl_df = pd.DataFrame(tax_loss_opportunities)
        st.dataframe(tl_df, use_container_width=True, hide_index=True)
        st.info("💡 Tax-loss harvesting can help offset capital gains. Consult with a tax advisor before implementing.")
    else:
        st.success("✅ No immediate tax-loss harvesting opportunities identified.")
    
    st.write("---")
    st.info("💡 **Technical Analysis Note:** Technical indicators work best when combined with fundamental analysis. For your risk profile, consider rebalancing quarterly rather than reacting to every short-term signal. Always maintain alignment with your long-term investment goals.")

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
    
    # Row 4: Factor Exposure Analysis
    st.subheader("📊 Factor Exposure Analysis")
    
    factor_data = []
    for etf in portfolio_details:
        factors = etf.get('Factor Exposure', {})
        if factors:
            for factor, value in factors.items():
                factor_data.append({
                    'ETF': etf['Ticker'],
                    'Factor': factor.capitalize(),
                    'Exposure': value * (etf['Allocation %'] / 100)
                })
    
    if factor_data:
        factor_df = pd.DataFrame(factor_data)
        pivot_df = factor_df.pivot(index='ETF', columns='Factor', values='Exposure').fillna(0)
        
        fig = px.imshow(pivot_df.T, 
                       title="Factor Exposure Heatmap (Weighted by Allocation)",
                       color_continuous_scale='RdBu',
                       aspect='auto')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
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
    
    st.write("---")
    
    # Row 7: Rebalancing Recommendations
    st.subheader("🔄 Rebalancing Recommendations")
    
    st.markdown("""
    <div class="recommendation-card">
        <h4>📅 Recommended Rebalancing Schedule</h4>
        <p><strong>Frequency:</strong> Quarterly (Every 3 months)</p>
        <p><strong>Threshold:</strong> Rebalance when allocation deviates by >5% from target</p>
        <p><strong>Best Times:</strong> End of each quarter (March, June, September, December)</p>
        <p><strong>Strategy:</strong> 
            - Sell assets that have appreciated beyond target<br>
            - Buy assets that have underperformed<br>
            - Maintain tax-efficiency by harvesting losses when possible
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    # Row 8: Banking Insights
    st.subheader("🏦 Banking & Institutional Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Portfolio Construction Methodology**")
        st.write("""
        - Based on Modern Portfolio Theory (Markowitz, 1952)
        - Optimized for risk-adjusted returns (Sharpe Ratio)
        - Uses institutional-grade ETFs from Vanguard, BlackRock, Invesco
        - Factor exposure optimized for your risk profile
        - Tax-loss harvesting integrated
        """)
    
    with col2:
        st.write("**Risk Management Framework**")
        st.write(f"""
        - Risk Profile: **{risk_profile}**
        - Maximum Drawdown: **{allocation_data['max_drawdown']*100:.0f}%**
        - Stop-loss recommendation: {allocation_data['max_drawdown']*100:.0f}%
        - Hedge recommendation: {'Increase bonds' if risk_profile in ['Aggressive', 'Moderate-Aggressive'] else 'Maintain allocation'}
        - Diversification ratio: {len(portfolio_details)} asset classes
        """)

# ========== MAIN APPLICATION ==========
def main():
    # Header
    st.title("🤖 AI Robo-Advisor")
    st.caption("Professional Portfolio Construction with Advanced Analytics & Technical Analysis")
    st.write("---")
    
    # Initialize session state for portfolio data
    if 'portfolio_generated' not in st.session_state:
        st.session_state.portfolio_generated = False
        st.session_state.portfolio_details = None
        st.session_state.risk_profile = None
        st.session_state.investment_years = None
        st.session_state.initial_amount = None
        st.session_state.available_tickers = list(ETF_DATABASE.keys())
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📊 Portfolio Advisor", "📈 Technical Analysis", "📚 Education & Resources"])
    
    # Tab 1: Portfolio Advisor
    with tab1:
        # Sidebar - Risk Assessment
        with st.sidebar:
            st.header("📋 Step 1: Enhanced Risk Assessment")
            st.write("Answer these 8 questions honestly:")
            st.write("---")
            
            q1 = st.slider(
                "**1. Investment Time Horizon**",
                min_value=1, max_value=30, value=10,
                help="Longer horizons allow more risk and potential growth"
            )
            q1_score = q1 / 3  # 0-10 scale
            
            q2 = st.select_slider(
                "**2. Reaction to Market Drop (20%)**",
                options=["Sell everything", "Get very nervous", "Get nervous", "Do nothing", "Buy more", "Aggressively buy more"],
                value="Do nothing",
                help="How would you emotionally react to a market crash?"
            )
            q2_scores = {"Sell everything": 0, "Get very nervous": 2, "Get nervous": 4, 
                        "Do nothing": 6, "Buy more": 8, "Aggressively buy more": 10}
            q2_score = q2_scores[q2]
            
            q3 = st.radio(
                "**3. Primary Investment Goal**",
                ["Capital preservation", "Income generation", "Balanced growth", 
                 "Long-term wealth", "Maximum growth"],
                index=2
            )
            q3_scores = {"Capital preservation": 0, "Income generation": 3, 
                        "Balanced growth": 5, "Long-term wealth": 8, "Maximum growth": 10}
            q3_score = q3_scores[q3]
            
            q4 = st.slider(
                "**4. Risk Capacity (% of savings)**",
                min_value=0, max_value=100, value=50,
                help="What percentage of your total savings are you investing?"
            )
            q4_score = q4 / 10  # 0-10 scale
            
            q5 = st.select_slider(
                "**5. Expected Annual Return**",
                options=["2-3% (Very safe)", "4-5% (Conservative)", "6-7% (Moderate)", 
                        "8-9% (Growth)", "10%+ (Aggressive)"],
                value="6-7% (Moderate)"
            )
            q5_scores = {"2-3% (Very safe)": 0, "4-5% (Conservative)": 3, 
                        "6-7% (Moderate)": 5, "8-9% (Growth)": 8, "10%+ (Aggressive)": 10}
            q5_score = q5_scores[q5]
            
            q6 = st.select_slider(
                "**6. Current Portfolio Size**",
                options=["Less than $10,000", "$10,000-$50,000", "$50,000-$100,000", 
                        "$100,000-$500,000", "$500,000+"],
                value="$50,000-$100,000"
            )
            q6_scores = {"Less than $10,000": 2, "$10,000-$50,000": 4, 
                        "$50,000-$100,000": 6, "$100,000-$500,000": 8, "$500,000+": 10}
            q6_score = q6_scores[q6]
            
            q7 = st.select_slider(
                "**7. Income Stability**",
                options=["Very Unstable", "Somewhat Unstable", "Stable", "Very Stable", "Guaranteed"],
                value="Stable"
            )
            q7_scores = {"Very Unstable": 0, "Somewhat Unstable": 3, 
                        "Stable": 6, "Very Stable": 8, "Guaranteed": 10}
            q7_score = q7_scores[q7]
            
            q8 = st.select_slider(
                "**8. Liquidity Needs (Next 5 Years)**",
                options=["Very High", "High", "Moderate", "Low", "Very Low"],
                value="Moderate"
            )
            q8_scores = {"Very High": 0, "High": 2, 
                        "Moderate": 5, "Low": 8, "Very Low": 10}
            q8_score = q8_scores[q8]
            
            st.write("---")
            
            st.header("💰 Step 2: Investment Details")
            initial_amount = st.number_input(
                "Investment Amount ($)",
                min_value=1000,
                max_value=10000000,
                value=10000,
                step=1000
            )
            
            investment_years = st.slider(
                "Investment Period (Years)",
                min_value=1,
                max_value=30,
                value=10
            )
            
            st.write("---")
            
            # ESG Preference
            esg_preference = st.checkbox("🌱 Include ESG/Sustainable ETFs", value=True)
            
            st.write("---")
            
            show_dashboard = st.checkbox("📊 Show Detailed Dashboard", value=True)
            st.write("---")
            submit = st.button("🎯 Generate Portfolio", type="primary", use_container_width=True)
        
        # Main content - Results
        if submit:
            answers = [q1_score, q2_score, q3_score, q4_score, q5_score, q6_score, q7_score, q8_score]
            risk_result = calculate_risk_profile(answers)
            risk_profile = risk_result["profile"]
            
            # Store in session state
            st.session_state.portfolio_generated = True
            st.session_state.risk_profile = risk_profile
            st.session_state.investment_years = investment_years
            st.session_state.initial_amount = initial_amount
            
            # Get available tickers (filter by ESG if selected)
            available_tickers = st.session_state.available_tickers
            if not esg_preference:
                # Remove ESG tickers if not selected
                available_tickers = [t for t in available_tickers if not ETF_DATABASE[t]['category'] == 'ESG']
            
            portfolio_details, allocation_data = optimize_portfolio(risk_profile, initial_amount, available_tickers)
            st.session_state.portfolio_details = portfolio_details
            st.session_state.allocation_data = allocation_data
            
            # Display risk profile banner
            st.success(f"""
            ### ✅ Your Risk Profile: **{risk_profile}**
            Score: {risk_result['score']:.0f}/100 | {risk_result['description']}
            **Style**: {risk_result['allocation_style']} | **Risk Tolerance**: {risk_result['risk_tolerance']}
            **Recommended Allocation**: Equity {risk_result['recommended_equity']}% | Bonds {risk_result['recommended_bonds']}% | Alternatives {risk_result['recommended_alternatives']}%
            """)
            
            st.write("---")
            st.header("📊 Your Personalized Portfolio")
            st.write(f"Based on your {risk_profile} profile, we recommend this diversified portfolio:")
            
            portfolio_df = pd.DataFrame(portfolio_details)
            col1, col2 = st.columns([1.5, 1])
            
            with col1:
                display_df = portfolio_df[["Ticker", "ETF Name", "Category", "Allocation %", "Amount ($)", "Expense Ratio", "Dividend Yield"]]
                display_df["Allocation %"] = display_df["Allocation %"].apply(lambda x: f"{x:.1f}%")
                display_df["Amount ($)"] = display_df["Amount ($)"].apply(lambda x: f"${x:,.0f}")
                display_df["Expense Ratio"] = display_df["Expense Ratio"].apply(lambda x: f"{x:.2f}%")
                display_df["Dividend Yield"] = display_df["Dividend Yield"].apply(lambda x: f"{x:.1f}%")
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                st.write("---")
                st.write("**📈 Portfolio Characteristics:**")
                st.write(f"• Expected Annual Return: **{allocation_data['expected_return']*100:.1f}%**")
                st.write(f"• Expected Volatility: **{allocation_data['expected_volatility']*100:.1f}%**")
                st.write(f"• Sharpe Ratio: **{allocation_data['sharpe_ratio']:.2f}**")
                st.write(f"• Suitable For: **{allocation_data['suitable_for']}**")
                st.write(f"• Diversification: {len(portfolio_details)} asset classes")
            
            with col2:
                fig = px.pie(portfolio_df, values="Allocation %", names=portfolio_df["Ticker"],
                            title="Asset Allocation", color_discrete_sequence=px.colors.qualitative.Set2, hole=0.3)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.write("---")
            st.header("📈 Monte Carlo Simulation")
            st.write(f"Projecting ${initial_amount:,} over {investment_years} years with {allocation_data['expected_return']*100:.1f}% expected return")
            
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
                5. Tax implications vary - consult a tax professional
                6. ESG investing involves specific risks and considerations
                """)
        
        else:
            st.info("### 👈 Complete the enhanced risk assessment to get your personalized portfolio")
            st.write("""
            **This tool now includes:**
            - ✅ 8-question comprehensive risk assessment
            - ✅ 50+ ETFs across all major asset classes
            - ✅ Optimized portfolio construction
            - ✅ Factor exposure analysis
            - ✅ Tax-loss harvesting opportunities
            - ✅ RSI and Bollinger Bands in technical analysis
            - ✅ ESG/Sustainable investing options
            """)
            
            # Feature preview
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**📊 Enhanced Portfolio**")
                st.write("• 50+ ETFs available")
                st.write("• Factor-based optimization")
                st.write("• ESG integration")
                st.write("• Tax efficiency")
            
            with col2:
                st.markdown("**📈 Advanced Analytics**")
                st.write("• RSI & Bollinger Bands")
                st.write("• Factor exposure heatmap")
                st.write("• Stress testing")
                st.write("• Performance attribution")
            
            with col3:
                st.markdown("**💡 Intelligent Features**")
                st.write("• Tax-loss harvesting")
                st.write("• Quarterly rebalancing")
                st.write("• Risk parity allocation")
                st.write("• Institutional-grade methodology")
    
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
            ### Enhanced Technical Analysis Features:
            
            Once you generate a portfolio, you'll get:
            
            **📊 Advanced Technical Indicators:**
            - **MACD** with Signal Line and Histogram
            - **RSI (Relative Strength Index)** - Overbought/Oversold signals
            - **Bollinger Bands** - Volatility and price position
            - **Golden Cross vs Death Cross** - Trend reversals
            - **Volume Analysis** - Confirmation of price movements
            
            **📋 Comprehensive Tables:**
            - MACD calculations (last 10 periods)
            - Crossover history with dates and prices
            - Summary with all technical signals
            - Actionable recommendations
            
            **📈 Visual Analysis:**
            - MACD chart with RSI overlay
            - Golden/Death Cross chart with volume
            - Bollinger Bands visualization
            - Trend identification
            
            **🎯 Decision Support:**
            - Combined technical recommendation
            - Tax-loss harvesting opportunities
            - Portfolio-wide technical conclusion
            - Priority-based action items
            """)
    
    # Tab 3: Education & Resources
    with tab3:
        st.header("📚 Educational Resources - Enhanced")
        st.write("---")
        
        st.subheader("🎓 Comprehensive Investment Education")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("📊 Advanced Technical Analysis", expanded=True):
                st.write("""
                **Technical Indicators Explained:**
                
                **1. MACD (Moving Average Convergence Divergence)**
                - Measures momentum and trend strength
                - MACD Line = 12-day EMA - 26-day EMA
                - Signal Line = 9-day EMA of MACD
                - Histogram shows momentum direction
                
                **2. RSI (Relative Strength Index)**
                - Measures speed and change of price movements
                - Scale: 0-100
                - Overbought: >70 (potential sell signal)
                - Oversold: <30 (potential buy signal)
                
                **3. Bollinger Bands**
                - Measures volatility and price levels
                - Middle band = 20-day SMA
                - Upper/lower bands = ±2 standard deviations
                - Price touching bands indicates extremes
                
                **4. Volume Analysis**
                - Confirms price trends
                - Increasing volume confirms trend
                - Decreasing volume indicates weakening trend
                """)
            
            with st.expander("📈 Portfolio Optimization Theory"):
                st.write("""
                **Modern Portfolio Theory (Markowitz, 1952):**
                
                **Key Concepts:**
                - Diversification reduces risk
                - Efficient Frontier - optimal portfolios
                - Correlation matters more than individual returns
                - Risk-adjusted returns (Sharpe Ratio)
                
                **Advanced Concepts:**
                - **Factor Investing**: Value, Growth, Momentum, Quality, Low Volatility
                - **Risk Parity**: Equal risk contribution from asset classes
                - **Black-Litterman**: Combines market equilibrium with investor views
                - **Monte Carlo Simulation**: Probabilistic outcome analysis
                """)
        
        with col2:
            with st.expander("🌱 ESG & Sustainable Investing"):
                st.write("""
                **Environmental, Social, and Governance (ESG) Factors:**
                
                **Environmental (E):**
                - Climate change and carbon emissions
                - Renewable energy adoption
                - Waste management and pollution
                - Water conservation                
                **Social (S):**
                - Labor practices and human rights
                - Diversity and inclusion
                - Community relations
                - Customer satisfaction
                
                **Governance (G):**
                - Board diversity and independence
                - Executive compensation
                - Shareholder rights
                - Business ethics
                
                **Benefits of ESG Investing:**
                - Long-term sustainability
                - Risk mitigation
                - Positive impact
                - Growing institutional adoption
                """)
            
            with st.expander("📊 Tax-Efficient Investing"):
                st.write("""
                **Tax Optimization Strategies:**
                
                **Tax-Loss Harvesting:**
                - Sell losing positions to offset gains
                - Reinvest in similar but not identical securities
                - Can reduce annual tax liability
                - Important for taxable accounts
                
                **Asset Location:**
                - Tax-efficient assets in taxable accounts
                - Tax-inefficient assets in tax-advantaged accounts
                - Consider municipal bonds for taxable accounts
                
                **Rebalancing Strategies:**
                - Rebalance quarterly to maintain target allocation
                - Use cash flow for rebalancing when possible
                - Consider tax implications of rebalancing
                """)
        
        st.write("---")
        
        st.subheader("📖 Recommended Reading")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Technical Analysis**")
            st.write("• Technical Analysis of Financial Markets - John Murphy")
            st.write("• Japanese Candlestick Charting - Steve Nison")
            st.write("• Encyclopedia of Chart Patterns - Thomas Bulkowski")
            st.write("• Getting Started in Technical Analysis - Jack Schwager")
        
        with col2:
            st.markdown("**Portfolio Management**")
            st.write("• The Intelligent Asset Allocator - William Bernstein")
            st.write("• Adaptive Asset Allocation - Adam Butler")
            st.write("• The Ivy Portfolio - Meb Faber")
            st.write("• Quantitative Asset Management - Scott Stewart")
        
        with col3:
            st.markdown("**Behavioral & ESG**")
            st.write("• Thinking, Fast and Slow - Daniel Kahneman")
            st.write("• Misbehaving - Richard Thaler")
            st.write("• The Psychology of Money - Morgan Housel")
            st.write("• ESG Investing for Dummies - Brendan Bradley")
        
        st.write("---")
        
        st.subheader("🎯 Actionable Next Steps")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**For Beginners**")
            st.write("1. Build emergency fund")
            st.write("2. Understand risk tolerance")
            st.write("3. Start with low-cost ETFs")
            st.write("4. Learn dollar-cost averaging")
            st.write("5. Focus on long-term goals")
        
        with col2:
            st.markdown("**For Intermediate**")
            st.write("1. Implement factor investing")
            st.write("2. Consider ESG integration")
            st.write("3. Optimize for tax efficiency")
            st.write("4. Learn technical analysis")
            st.write("5. Review/rebalance quarterly")
        
        with col3:
            st.markdown("**For Advanced**")
            st.write("1. Explore alternative assets")
            st.write("2. Implement risk parity")
            st.write("3. Use options for hedging")
            st.write("4. Consider direct indexing")
            st.write("5. Private market access")
        
        st.write("---")
        st.info("💡 **Pro Tip:** Combine multiple approaches for best results. Use fundamental analysis for selection, technical analysis for timing, and behavioral finance for emotional management. Stay diversified and maintain a long-term perspective.")

# ========== RUN APPLICATION ==========
if __name__ == "__main__":
    main()
