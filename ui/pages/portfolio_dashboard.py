import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from services.client_service import ClientService
from services.portfolio_service import PortfolioService
from ui.components import metric_card, format_currency, format_percentage
import yfinance as yf

def create_portfolio_chart(portfolio_service, client_id):
    """Create an interactive portfolio performance chart"""
    holdings = portfolio_service.get_holdings_with_current_prices(client_id)
    if holdings.empty:
        return None
    
    # Calculate daily portfolio values for the last year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    portfolio_values = []
    dates = []
    
    current_date = start_date
    while current_date <= end_date:
        daily_value = 0
        for _, holding in holdings.iterrows():
            stock = yf.Ticker(holding['ticker'])
            hist = stock.history(start=current_date, end=current_date + timedelta(days=1))
            if not hist.empty:
                daily_value += hist['Close'].iloc[0] * holding['quantity']
        
        if daily_value > 0:
            portfolio_values.append(daily_value)
            dates.append(current_date)
        
        current_date += timedelta(days=1)
    
    fig = go.Figure()
    
    # Add portfolio value line
    fig.add_trace(go.Scatter(
        x=dates,
        y=portfolio_values,
        mode='lines',
        name='Portfolio Value',
        line=dict(color='#1f77b4', width=2),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.1)'
    ))
    
    # Calculate and add return percentage line
    initial_value = portfolio_values[0] if portfolio_values else 0
    returns_pct = [(v - initial_value) / initial_value * 100 for v in portfolio_values]
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=returns_pct,
        mode='lines',
        name='Return %',
        line=dict(color='#2ca02c', width=2),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='Portfolio Performance',
        height=600,
        xaxis_title="Date",
        yaxis_title="Portfolio Value (₹)",
        yaxis2=dict(
            title="Return %",
            overlaying='y',
            side='right',
            showgrid=False
        ),
        hovermode='x unified',
        plot_bgcolor='white'
    )
    
    return fig

def portfolio_visualization_tab():
    st.header("Portfolio Dashboard")
    
    # Initialize services
    client_service = ClientService(st.session_state.db)
    portfolio_service = PortfolioService(st.session_state.db)
    
    # Client selection
    clients = client_service.get_all_clients()
    if clients.empty:
        st.warning("No clients found. Please add clients first!")
        return
    
    selected_client = st.selectbox(
        "Select Client",
        options=clients['id'].tolist(),
        format_func=lambda x: f"{clients.loc[clients['id'] == x, 'name'].iloc[0]} "
                            f"({clients.loc[clients['id'] == x, 'family_name'].iloc[0]})",
        key="dashboard_client_select"
    )
    
    # Get portfolio summary
    summary = portfolio_service.get_portfolio_summary(selected_client)
    
    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        metric_card(
            "Total Portfolio Value",
            format_currency(summary["current_value"]),
            "Current market value"
        )
    
    with col2:
        metric_card(
            "Total Investment",
            format_currency(summary["total_investment"]),
            "Initial investment"
        )
    
    with col3:
        metric_card(
            "Total Return",
            format_percentage(summary["return_percentage"]),
            format_currency(summary["total_return"]),
            "positive" if summary["return_percentage"] > 0 else "negative"
        )
    
    # Portfolio performance chart
    st.markdown("---")
    fig = create_portfolio_chart(portfolio_service, selected_client)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for portfolio visualization.")
    
    # Holdings breakdown
    st.markdown("---")
    st.subheader("Holdings Breakdown")
    
    holdings = portfolio_service.get_holdings_with_current_prices(selected_client)
    if not holdings.empty:
        # Create a pie chart of portfolio allocation
        allocation_fig = go.Figure(data=[go.Pie(
            labels=holdings['ticker'].apply(lambda x: x.replace('.NS', '')),
            values=holdings['current_value'],
            hole=0.4
        )])
        
        allocation_fig.update_layout(
            title='Portfolio Allocation',
            height=400
        )
        
        st.plotly_chart(allocation_fig, use_container_width=True)
        
        # Display holdings table with current values and returns
        st.markdown("### Holdings Details")
        st.dataframe(
            holdings,
            column_config={
                "ticker": st.column_config.TextColumn("Ticker", width="medium"),
                "quantity": st.column_config.NumberColumn("Quantity", width="small"),
                "buy_price": st.column_config.NumberColumn("Buy Price", format="₹%.2f"),
                "current_price": st.column_config.NumberColumn("Current Price", format="₹%.2f"),
                "total_investment": st.column_config.NumberColumn("Total Investment", format="₹%.2f"),
                "current_value": st.column_config.NumberColumn("Current Value", format="₹%.2f"),
                "return_percentage": st.column_config.NumberColumn("Return %", format="%+.2f%%")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No holdings found for this client.")