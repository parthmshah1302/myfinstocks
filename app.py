import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Stock Portfolio Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size:24px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .positive-return { color: #28a745; }
    .negative-return { color: #dc3545; }
    </style>
""", unsafe_allow_html=True)

def get_sample_data():
    return pd.DataFrame({
        'client_name': ['Raj Kumar', 'Priya Shah', 'Raj Kumar', 'Priya Shah'],
        'ticker': ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS'],
        'quantity': [100, 50, 75, 60],
        'buy_price': [2100.50, 3800.75, 1550.25, 1600.30],
        'buy_date': ['2023-06-15', '2023-08-20', '2023-07-10', '2023-09-05']
    })

def get_stock_data(ticker, start_date, end_date):
    """Fetch stock data using yfinance"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)
        if hist.empty:
            st.error(f"No data available for {ticker} in the specified date range")
            return None
        return hist
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {str(e)}")
        return None

def calculate_portfolio_value(holdings, start_date, end_date):
    """Calculate daily portfolio value and investment value"""
    all_values = []
    investment_values = []
    
    for _, row in holdings.iterrows():
        stock_data = get_stock_data(row['ticker'], start_date, end_date)
        if stock_data is not None and not stock_data.empty:
            daily_value = stock_data['Close'] * row['quantity']
            all_values.append(daily_value)
            # Calculate initial investment value
            investment_value = pd.Series(row['buy_price'] * row['quantity'], 
                                      index=daily_value.index)
            investment_values.append(investment_value)
    
    if not all_values:
        return pd.DataFrame(), pd.DataFrame()
    
    portfolio_value = pd.concat(all_values, axis=1).sum(axis=1)
    investment_value = pd.concat(investment_values, axis=1).sum(axis=1)
    
    return portfolio_value, investment_value

def format_change(value):
    """Format percentage changes with + or - sign"""
    if pd.isna(value):
        return "N/A"
    return f"+{value:,.2f}%" if value > 0 else f"{value:,.2f}%"

def format_gain_loss(value):
    """Format absolute gain/loss with currency symbol"""
    return f"+₹{value:,.2f}" if value > 0 else f"-₹{abs(value):,.2f}"

def main():
    # Sidebar - Client Selection
    st.sidebar.markdown("## Portfolio Settings")
    st.sidebar.markdown("---")
    
    # Load data
    df = get_sample_data()
    
    clients = sorted(df['client_name'].unique())
    selected_client = st.sidebar.selectbox(
        "Select Client",
        clients
    )
    
    # Main content
    st.markdown("<h1 style='text-align: center;'>Portfolio Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    end_date = datetime.now()
    start_date = min(pd.to_datetime(df['buy_date']))
    client_holdings = df[df['client_name'] == selected_client]
    
    # Calculate portfolio value for chart
    portfolio_value, investment_value = calculate_portfolio_value(client_holdings, start_date, end_date)
    
    if not portfolio_value.empty:
        # Calculate daily returns for chart
        returns_pct = ((portfolio_value - investment_value) / investment_value) * 100
        
        # Portfolio Value Chart
        st.subheader("Portfolio Performance")
        fig = go.Figure()
        
        # Add portfolio value line
        fig.add_trace(go.Scatter(
            x=portfolio_value.index,
            y=portfolio_value.values,
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.1)'
        ))
        
        # Add returns percentage line
        fig.add_trace(go.Scatter(
            x=returns_pct.index,
            y=returns_pct.values,
            mode='lines',
            name='Return %',
            line=dict(color='#2ca02c', width=2),
            yaxis='y2'
        ))
        
        # Update layout with secondary y-axis
        fig.update_layout(
            height=500,
            xaxis_title="Date",
            yaxis_title="Portfolio Value (₹)",
            yaxis2=dict(
                title="Return %",
                overlaying='y',
                side='right',
                showgrid=False,
                zeroline=True,
                zerolinecolor='rgba(0,0,0,0.2)'
            ),
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                showline=True,
                linecolor='rgba(0,0,0,0.2)'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                showline=True,
                linecolor='rgba(0,0,0,0.2)',
                tickformat=',.0f'
            ),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Current Holdings
    st.markdown("### Current Holdings")
    holdings_data = []
    
    for _, holding in client_holdings.iterrows():
        # Get current data
        current_data = get_stock_data(
            holding['ticker'], 
            end_date - timedelta(days=7),
            end_date
        )
        
        # Get 1-year data
        year_ago = end_date - timedelta(days=365)
        yearly_data = get_stock_data(
            holding['ticker'], 
            year_ago,
            end_date
        )
        
        if current_data is not None and not current_data.empty:
            current_price = current_data['Close'].iloc[-1]
            daily_change = current_data['Close'].pct_change().iloc[-1] * 100
            
            # Calculate 1-year return if data available
            year_return = None
            if yearly_data is not None and not yearly_data.empty and len(yearly_data) > 1:
                year_return = ((current_price - yearly_data['Close'].iloc[0]) / yearly_data['Close'].iloc[0]) * 100
            
            # Calculate absolute gains
            abs_gain = (current_price - holding['buy_price']) * holding['quantity']
            abs_gain_pct = ((current_price - holding['buy_price']) / holding['buy_price']) * 100
            
            holdings_data.append({
                'Ticker': holding['ticker'].replace('.NS', ''),
                'Quantity': holding['quantity'],
                'Buy Price': f"₹{holding['buy_price']:,.2f}",
                'Current Price': f"₹{current_price:,.2f}",
                '1D Change': format_change(daily_change),
                '1Y Return': format_change(year_return) if year_return is not None else "N/A",
                'Total Return %': format_change(abs_gain_pct),
                'Absolute Gain/Loss': format_gain_loss(abs_gain)
            })
    
    if holdings_data:
        holdings_df = pd.DataFrame(holdings_data)
        st.dataframe(
            holdings_df,
            column_config={
                "Ticker": st.column_config.TextColumn("Ticker", width="medium"),
                "Quantity": st.column_config.NumberColumn("Quantity", width="small"),
                "Buy Price": st.column_config.TextColumn("Buy Price", width="medium"),
                "Current Price": st.column_config.TextColumn("Current Price", width="medium"),
                "1D Change": st.column_config.TextColumn("1D Change", width="small"),
                "1Y Return": st.column_config.TextColumn("1Y Return", width="small"),
                "Total Return %": st.column_config.TextColumn("Total Return", width="medium"),
                "Absolute Gain/Loss": st.column_config.TextColumn("Absolute G/L", width="medium")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Portfolio Summary
        total_current_value = portfolio_value.iloc[-1] if not portfolio_value.empty else 0
        total_investment = investment_value.iloc[-1] if not investment_value.empty else 0
        total_return_pct = ((total_current_value - total_investment) / total_investment) * 100 if total_investment != 0 else 0
        
        # Market Overview
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <p style="color: #666; font-size: 1.1em;">Total Portfolio Value</p>
                    <p class="big-font">₹{total_current_value:,.2f}</p>
                    <p style="color: #666;">Initial Investment: ₹{total_investment:,.2f}</p>
                    <p class="{'positive-return' if total_return_pct > 0 else 'negative-return'}">
                        {format_change(total_return_pct)}
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        # Market Overview
        indices = {
            "NIFTY 50": "^NSEI",
            "SENSEX": "^BSESN"
        }
        
        for (index_name, symbol), col in zip(indices.items(), [col2, col3]):
            index_data = get_stock_data(symbol, end_date - timedelta(days=7), end_date)
            if index_data is not None and not index_data.empty:
                current_value = index_data['Close'].iloc[-1]
                change = index_data['Close'].pct_change().iloc[-1] * 100 if len(index_data) > 1 else 0
                with col:
                    st.markdown(f"""
                        <div class="metric-card">
                            <p style="color: #666; font-size: 1.1em;">{index_name}</p>
                            <p class="big-font">₹{current_value:,.2f}</p>
                            <p class="{'positive-return' if change > 0 else 'negative-return'}">
                                {format_change(change)}
                            </p>
                        </div>
                    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()