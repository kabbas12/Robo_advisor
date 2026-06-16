"""
AI Robo-Advisor for Investment
Professional Portfolio Construction with Advanced Analytics
Author: Syed Kamran Abbas 

"""

# ========== IMPORT LIBRARIES ==========
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="Technical Analysis Tool",
    page_icon="📈",
    layout="wide"
)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    .buy-signal {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 10px 0;
    }
    .sell-signal {
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        margin: 10px 0;
    }
    .neutral-signal {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
        margin: 10px 0;
    }
    .golden-cross {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 5px;
        text-align: center;
        margin: 10px 0;
    }
    .death-cross {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 5px;
        text-align: center;
        margin: 10px 0;
    }
    .metric-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# ========== ETF DATABASE ==========
ETF_DATABASE = {
    "AAPL": {"name": "Apple Inc.", "sector": "Technology"},
    "MSFT": {"name": "Microsoft Corporation", "sector": "Technology"},
    "GOOGL": {"name": "Alphabet Inc.", "sector": "Technology"},
    "AMZN": {"name": "Amazon.com Inc.", "sector": "Consumer Cyclical"},
    "TSLA": {"name": "Tesla Inc.", "sector": "Automotive"},
    "NVDA": {"name": "NVIDIA Corporation", "sector": "Technology"},
    "META": {"name": "Meta Platforms Inc.", "sector": "Technology"},
    "SPY": {"name": "SPDR S&P 500 ETF", "sector": "ETF"},
    "QQQ": {"name": "Invesco QQQ Trust", "sector": "ETF"},
    "VTI": {"name": "Vanguard Total Stock Market ETF", "sector": "ETF"},
    "BND": {"name": "Vanguard Total Bond Market ETF", "sector": "ETF"},
    "GLD": {"name": "SPDR Gold Shares", "sector": "Commodity"},
    "VXUS": {"name": "Vanguard Total International Stock ETF", "sector": "ETF"},
    "IWM": {"name": "iShares Russell 2000 ETF", "sector": "ETF"},
    "TLT": {"name": "iShares 20+ Year Treasury Bond ETF", "sector": "ETF"},
    "JPM": {"name": "JPMorgan Chase & Co.", "sector": "Financial"},
    "VZ": {"name": "Verizon Communications Inc.", "sector": "Telecom"},
    "KO": {"name": "Coca-Cola Company", "sector": "Consumer Staples"},
    "PFE": {"name": "Pfizer Inc.", "sector": "Healthcare"},
    "XOM": {"name": "Exxon Mobil Corporation", "sector": "Energy"}
}

# ========== DATA FETCHING ==========
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

# ========== TECHNICAL INDICATOR CALCULATIONS ==========
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

# ========== MACD TABLE ==========
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

# ========== CROSS TABLE ==========
def calculate_cross_table(df):
    """Create Golden Cross and Death Cross history table"""
    golden_crosses = df[df['Golden_Cross'] == True]
    death_crosses = df[df['Death_Cross'] == True]
    
    cross_data = []
    
    for idx in golden_crosses.index:
        cross_data.append({
            'Date': idx.strftime('%Y-%m-%d'),
            'Type': '🟢 Golden Cross (BUY)',
            'Short MA (20)': round(golden_crosses.loc[idx, 'MA_Short'], 2),
            'Long MA (50)': round(golden_crosses.loc[idx, 'MA_Long'], 2),
            'Price at Signal': round(golden_crosses.loc[idx, 'Close'], 2)
        })
    
    for idx in death_crosses.index:
        cross_data.append({
            'Date': idx.strftime('%Y-%m-%d'),
            'Type': '🔴 Death Cross (SELL)',
            'Short MA (20)': round(death_crosses.loc[idx, 'MA_Short'], 2),
            'Long MA (50)': round(death_crosses.loc[idx, 'MA_Long'], 2),
            'Price at Signal': round(death_crosses.loc[idx, 'Close'], 2)
        })
    
    cross_df = pd.DataFrame(cross_data)
    if not cross_df.empty:
        cross_df = cross_df.sort_values('Date', ascending=False)
    
    return cross_df

# ========== MACD GRAPH ==========
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
                            marker=dict(color='green', size=12, symbol='triangle-up')), row=2, col=1)
    
    fig.add_trace(go.Scatter(x=bearish_cross.index, y=bearish_cross['MACD'],
                            mode='markers', name='Bearish Crossover',
                            marker=dict(color='red', size=12, symbol='triangle-down')), row=2, col=1)
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
    
    fig.update_layout(title=f"{ticker} - MACD Analysis",
                     height=600,
                     showlegend=True,
                     xaxis_title="Date",
                     hovermode='x unified')
    
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="MACD Value", row=2, col=1)
    
    return fig

# ========== GOLDEN/DEATH CROSS GRAPH ==========
def plot_golden_death_cross_graph(df, ticker):
    """Plot Golden Cross vs Death Cross graph"""
    fig = go.Figure()
    
    # Price line
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], 
                            mode='lines', name='Close Price', 
                            line=dict(color='gray', width=1, dash='dot')))
    
    # Short MA
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_Short'], 
                            mode='lines', name='MA 20 (Short)', 
                            line=dict(color='orange', width=2)))
    
    # Long MA
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_Long'], 
                            mode='lines', name='MA 50 (Long)', 
                            line=dict(color='blue', width=2)))
    
    # Golden Cross markers
    golden_crosses = df[df['Golden_Cross'] == True]
    death_crosses = df[df['Death_Cross'] == True]
    
    fig.add_trace(go.Scatter(x=golden_crosses.index, y=golden_crosses['Close'],
                            mode='markers', name='🟢 Golden Cross (BUY)',
                            marker=dict(color='green', size=15, symbol='triangle-up', 
                                       line=dict(color='darkgreen', width=2))))
    
    fig.add_trace(go.Scatter(x=death_crosses.index, y=death_crosses['Close'],
                            mode='markers', name='🔴 Death Cross (SELL)',
                            marker=dict(color='red', size=15, symbol='triangle-down',
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

# ========== MAIN APP ==========
def main():
    st.title("📈 Technical Analysis Tool")
    st.caption("MACD & Golden Cross/Death Cross Analysis with Interactive Charts")
    st.write("---")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Security selection
        st.subheader("Select Security")
        
        # Search/filter functionality
        search_term = st.text_input("🔍 Search Ticker or Name", placeholder="e.g., AAPL, Apple, SPY")
        
        # Filter ETF database
        filtered_etfs = {}
        if search_term:
            search_lower = search_term.lower()
            for ticker, info in ETF_DATABASE.items():
                if search_lower in ticker.lower() or search_lower in info['name'].lower():
                    filtered_etfs[ticker] = info
        else:
            filtered_etfs = ETF_DATABASE
        
        # Create options for selectbox
        options = []
        for ticker, info in filtered_etfs.items():
            options.append(f"{ticker} - {info['name']} ({info['sector']})")
        
        if options:
            selected_option = st.selectbox("Select Security", options, index=0)
            selected_ticker = selected_option.split(" - ")[0]
        else:
            st.warning("No securities found matching your search")
            selected_ticker = "AAPL"
        
        # Time period selection
        st.subheader("Analysis Period")
        period_options = {
            "1 Month": 30,
            "3 Months": 90,
            "6 Months": 180,
            "1 Year": 365,
            "2 Years": 730,
            "3 Years": 1095,
            "5 Years": 1825
        }
        selected_period = st.selectbox("Select Period", list(period_options.keys()), index=3)
        days = period_options[selected_period]
        
        # Show security info
        st.write("---")
        st.subheader("📊 Security Info")
        if selected_ticker in ETF_DATABASE:
            info = ETF_DATABASE[selected_ticker]
            st.write(f"**Name:** {info['name']}")
            st.write(f"**Sector:** {info['sector']}")
        
        # Analyze button
        st.write("---")
        analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)
    
    # Main content area
    if analyze_button:
        with st.spinner(f"Fetching data for {selected_ticker}..."):
            # Fetch data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            data = fetch_stock_data(selected_ticker, start_date, end_date)
            
            if data is not None and not data.empty:
                # Calculate indicators
                df = calculate_technical_indicators(data)
                
                # Display current price and basic info
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
                
                # ===== MACD SECTION =====
                st.header("📈 MACD Analysis")
                st.write("Moving Average Convergence Divergence - Momentum Indicator")
                
                # MACD Graph
                st.subheader("📊 MACD Chart")
                macd_fig = plot_macd_graph(df, selected_ticker)
                st.plotly_chart(macd_fig, use_container_width=True)
                
                # MACD Table
                st.subheader("📋 MACD Recent Calculations (Last 10 Days)")
                macd_table = calculate_macd_table(df)
                if not macd_table.empty:
                    st.dataframe(macd_table, use_container_width=True, hide_index=True)
                
                # MACD Interpretation
                st.subheader("🔍 MACD Interpretation")
                current_macd = df['MACD'].iloc[-1]
                current_signal = df['Signal_Line'].iloc[-1]
                current_hist = df['MACD_Histogram'].iloc[-1]
                
                col1, col2 = st.columns(2)
                with col1:
                    if current_macd > current_signal:
                        st.markdown("""
                        <div class="buy-signal">
                            <strong>✅ BULLISH SIGNAL</strong><br>
                            MACD Line is above Signal Line<br>
                            <strong>MACD:</strong> {:.4f} | <strong>Signal:</strong> {:.4f}<br>
                            Indicates upward momentum and potential price appreciation
                        </div>
                        """.format(current_macd, current_signal), unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="sell-signal">
                            <strong>❌ BEARISH SIGNAL</strong><br>
                            MACD Line is below Signal Line<br>
                            <strong>MACD:</strong> {:.4f} | <strong>Signal:</strong> {:.4f}<br>
                            Indicates downward momentum and potential price depreciation
                        </div>
                        """.format(current_macd, current_signal), unsafe_allow_html=True)
                
                with col2:
                    if current_hist > 0 and current_hist > df['MACD_Histogram'].iloc[-2]:
                        st.markdown("""
                        <div class="buy-signal">
                            <strong>📈 STRENGTHENING BULLISH MOMENTUM</strong><br>
                            Histogram is positive and increasing<br>
                            <strong>Histogram:</strong> {:.4f}<br>
                            Confirms strong bullish momentum
                        </div>
                        """.format(current_hist), unsafe_allow_html=True)
                    elif current_hist < 0 and current_hist < df['MACD_Histogram'].iloc[-2]:
                        st.markdown("""
                        <div class="sell-signal">
                            <strong>📉 STRENGTHENING BEARISH MOMENTUM</strong><br>
                            Histogram is negative and decreasing<br>
                            <strong>Histogram:</strong> {:.4f}<br>
                            Confirms strong bearish momentum
                        </div>
                        """.format(current_hist), unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="neutral-signal">
                            <strong>⚠️ MIXED MOMENTUM SIGNALS</strong><br>
                            <strong>Histogram:</strong> {:.4f}<br>
                            Monitor for clearer trend confirmation
                        </div>
                        """.format(current_hist), unsafe_allow_html=True)
                
                st.write("---")
                
                # ===== GOLDEN/DEATH CROSS SECTION =====
                st.header("🟡 Golden Cross vs 🔴 Death Cross Analysis")
                st.write("Moving Average Crossovers - Trend Reversal Indicator")
                
                # Golden/Death Cross Graph
                st.subheader("📊 Golden Cross vs Death Cross Chart")
                cross_fig = plot_golden_death_cross_graph(df, selected_ticker)
                st.plotly_chart(cross_fig, use_container_width=True)
                
                # Cross Table
                st.subheader("📋 Crossover History")
                cross_table = calculate_cross_table(df)
                if not cross_table.empty:
                    st.dataframe(cross_table, use_container_width=True, hide_index=True)
                else:
                    st.info("ℹ️ No Golden Cross or Death Cross events detected in the analysis period.")
                
                # Cross Interpretation
                st.subheader("🔍 Crossover Interpretation")
                
                current_short_ma = df['MA_Short'].iloc[-1]
                current_long_ma = df['MA_Long'].iloc[-1]
                golden_count = len(df[df['Golden_Cross'] == True])
                death_count = len(df[df['Death_Cross'] == True])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Current MA Status:**")
                    if current_short_ma > current_long_ma:
                        st.markdown(f"""
                        <div class="golden-cross">
                            <strong>🟢 GOLDEN CROSS ACTIVE</strong><br>
                            MA 20: ${current_short_ma:.2f} > MA 50: ${current_long_ma:.2f}<br>
                            Difference: ${current_short_ma - current_long_ma:.2f}<br>
                            <strong>Signal:</strong> Bullish - Consider increasing exposure
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="death-cross">
                            <strong>🔴 DEATH CROSS ACTIVE</strong><br>
                            MA 20: ${current_short_ma:.2f} < MA 50: ${current_long_ma:.2f}<br>
                            Difference: ${current_long_ma - current_short_ma:.2f}<br>
                            <strong>Signal:</strong> Bearish - Consider reducing exposure
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("**Historical Crossovers:**")
                    st.write(f"• **Golden Crosses:** {golden_count} occurrences")
                    st.write(f"• **Death Crosses:** {death_count} occurrences")
                    
                    if golden_count > death_count:
                        st.success("More Golden Cross signals indicate overall bullish bias")
                    elif death_count > golden_count:
                        st.error("More Death Cross signals indicate overall bearish bias")
                    else:
                        st.warning("Equal number of bullish and bearish signals")
                
                st.write("---")
                
                # ===== COMBINED CONCLUSION =====
                st.header("🎯 Combined Technical Conclusion")
                
                macd_bullish = current_macd > current_signal
                cross_bullish = current_short_ma > current_long_ma
                
                if macd_bullish and cross_bullish:
                    st.markdown(f"""
                    <div class="buy-signal">
                        <h3>✅ STRONG BULLISH SIGNAL - {selected_ticker}</h3>
                        <p><strong>Recommendation:</strong> BUY / ACCUMULATE</p>
                        <p><strong>Rationale:</strong></p>
                        <ul>
                            <li>MACD indicates bullish momentum</li>
                            <li>Golden Cross active (bullish MA crossover)</li>
                            <li>Both primary indicators align positively</li>
                        </ul>
                        <p><strong>Action:</strong> Consider increasing position size. Set stop-loss below recent support.</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif macd_bullish or cross_bullish:
                    st.markdown(f"""
                    <div class="neutral-signal">
                        <h3>⚠️ MODERATE BULLISH SIGNAL - {selected_ticker}</h3>
                        <p><strong>Recommendation:</strong> HOLD / ACCUMULATE CAUTIOUSLY</p>
                        <p><strong>Rationale:</strong></p>
                        <ul>
                            <li>Mixed signals between MACD and MA crossovers</li>
                            <li>One indicator shows bullishness while other is neutral/bearish</li>
                            <li>Wait for confirmation before increasing exposure</li>
                        </ul>
                        <p><strong>Action:</strong> Maintain current position. Watch for confirmation.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="sell-signal">
                        <h3>❌ BEARISH SIGNAL - {selected_ticker}</h3>
                        <p><strong>Recommendation:</strong> SELL / REDUCE</p>
                        <p><strong>Rationale:</strong></p>
                        <ul>
                            <li>MACD indicates bearish momentum</li>
                            <li>Death Cross active (bearish MA crossover)</li>
                            <li>Both primary indicators align negatively</li>
                        </ul>
                        <p><strong>Action:</strong> Consider reducing position. Look for support levels before re-entry.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Summary metrics
                st.write("---")
                st.subheader("📊 Key Technical Metrics")
                
                metrics_cols = st.columns(5)
                with metrics_cols[0]:
                    st.metric("MACD Status", "Bullish" if macd_bullish else "Bearish")
                with metrics_cols[1]:
                    st.metric("MA Status", "Bullish" if cross_bullish else "Bearish")
                with metrics_cols[2]:
                    st.metric("Golden Crosses", golden_count)
                with metrics_cols[3]:
                    st.metric("Death Crosses", death_count)
                with metrics_cols[4]:
                    st.metric("Overall Signal", "BUY" if (macd_bullish and cross_bullish) else "SELL" if (not macd_bullish and not cross_bullish) else "HOLD")
                
            else:
                st.error(f"❌ Failed to fetch data for {selected_ticker}. Please try another security.")
                st.info("💡 Make sure the ticker symbol is valid and try again.")
    
    else:
        # Welcome message when no analysis has been run
        st.info("👈 Select a security from the sidebar and click 'Analyze' to begin")
        
        st.markdown("""
        ### 🎯 What this tool does:
        
        **📈 MACD Analysis**
        - Calculates MACD line, Signal line, and Histogram
        - Displays interactive chart with crossover markers
        - Shows recent calculations table
        - Provides bullish/bearish interpretation
        
        **🟡 Golden Cross vs 🔴 Death Cross**
        - Detects moving average crossovers (MA 20 & MA 50)
        - Shows historical crossover events
        - Visual chart with highlighted regions
        - Current trend status and signal
        
        **🎯 Combined Conclusion**
        - Aggregates both indicators
        - Provides actionable recommendation
        - Key metrics summary
        
        ### 📊 Available Securities:
        
        **Technology:** AAPL, MSFT, GOOGL, AMZN, NVDA, META
        **Financial:** JPM
        **Healthcare:** PFE
        **Consumer:** KO, VZ
        **Energy:** XOM
        **Automotive:** TSLA
        **ETFs:** SPY, QQQ, VTI, BND, VXUS, IWM, TLT
        **Commodity:** GLD
        """)
        
        # Display available securities in a table
        df_securities = pd.DataFrame([
            {"Ticker": ticker, "Name": info["name"], "Sector": info["sector"]}
            for ticker, info in ETF_DATABASE.items()
        ])
        st.dataframe(df_securities, use_container_width=True, hide_index=True)
    
    # Footer
    st.write("---")
    st.caption("📊 Data sourced from Yahoo Finance | Technical Analysis Tool v2.0")

if __name__ == "__main__":
    main()
