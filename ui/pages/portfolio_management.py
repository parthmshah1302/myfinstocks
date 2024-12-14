import streamlit as st
from datetime import datetime
from services.client_service import ClientService
from services.portfolio_service import PortfolioService
from ui.components import metric_card, format_currency

def portfolio_management_tab():
    st.header("Portfolio Management")
    
    # Initialize services
    client_service = ClientService(st.session_state.db)
    portfolio_service = PortfolioService(st.session_state.db)
    
    # Get all clients
    clients = client_service.get_all_clients()
    if clients.empty:
        st.warning("No clients found. Please add clients first!")
        return
    
    # Client selection
    selected_client = st.selectbox(
        "Select Client",
        options=clients['id'].tolist(),
        format_func=lambda x: f"{clients.loc[clients['id'] == x, 'name'].iloc[0]} "
                            f"({clients.loc[clients['id'] == x, 'family_name'].iloc[0]})"
    )
    
    st.markdown("---")
    
    # Add new holding section
    st.subheader("Add New Stock")
    with st.form("add_holding_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ticker = st.text_input(
                "Enter Stock Symbol",
                help="For Indian stocks (e.g., RELIANCE, TCS)"
            )
        
        with col2:
            quantity = st.number_input(
                "Quantity",
                min_value=1,
                value=1,
                help="Number of shares"
            )
        
        with col3:
            buy_date = st.date_input(
                "Purchase Date",
                value=datetime.now(),
                max_value=datetime.now()
            )
        
        submitted = st.form_submit_button("Add Stock")
        if submitted:
            if ticker and quantity and buy_date:
                success, message = portfolio_service.add_holding(
                    selected_client,
                    ticker,
                    quantity,
                    buy_date
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)
    
    # Display current portfolio summary
    st.markdown("---")
    st.subheader("Portfolio Summary")
    
    summary = portfolio_service.get_portfolio_summary(selected_client)
    
    col1, col2 = st.columns(2)
    
    with col1:
        metric_card(
            "Total Investment",
            format_currency(summary["total_investment"]),
            "Initial investment amount"
        )
    
    with col2:
        metric_card(
            "Current Value",
            format_currency(summary["current_value"]),
            f"Return: {summary['return_percentage']:.2f}%",
            "positive" if summary["return_percentage"] > 0 else "negative"
        )
    
    # Display current holdings
    st.markdown("---")
    st.subheader("Current Holdings")
    
    holdings = portfolio_service.get_holdings_with_current_prices(selected_client)
    if not holdings.empty:
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