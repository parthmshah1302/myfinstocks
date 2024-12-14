import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import sqlite3
import pdfkit
import io


def set_page_config():
    st.set_page_config(
        page_title="Portfolio Management System",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def apply_custom_css():
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

def init_db():
    with sqlite3.connect('portfolio.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS families (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                family_id INTEGER,
                FOREIGN KEY (family_id) REFERENCES families (id),
                UNIQUE(name, family_id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                ticker TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                buy_price REAL NOT NULL,
                buy_date DATE NOT NULL,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        conn.commit()

def execute_query(query, params=(), fetch=True):
    with sqlite3.connect('portfolio.db') as conn:
        df = pd.read_sql_query(query, conn, params=params) if fetch else None
    return df

def get_all_families():
    return execute_query("SELECT * FROM families")

def get_all_clients():
    return execute_query("""
        SELECT clients.id, clients.name, families.name as family_name 
        FROM clients 
        JOIN families ON clients.family_id = families.id
    """)

def add_family(name):
    try:
        execute_query("INSERT INTO families (name) VALUES (?)", (name,), fetch=False)
        return True
    except sqlite3.IntegrityError:
        return False

def add_client(name, family_id):
    try:
        execute_query("INSERT INTO clients (name, family_id) VALUES (?, ?)", (name, family_id), fetch=False)
        return True
    except sqlite3.IntegrityError:
        return False

def add_holding(client_id, ticker, quantity, buy_date):
    ticker_full = f"{ticker}.NS" if not ticker.endswith('.NS') else ticker
    stock = yf.Ticker(ticker_full)
    hist = stock.history(start=buy_date, end=buy_date + timedelta(days=1))
    
    if hist.empty:
        return False, "No price data available for the selected date"
    
    buy_price = hist['Close'].iloc[0]
    
    try:
        execute_query("""
            INSERT INTO holdings (client_id, ticker, quantity, buy_price, buy_date)
            VALUES (?, ?, ?, ?, ?)
        """, (client_id, ticker_full, quantity, buy_price, buy_date), fetch=False)
        return True, f"Holding added successfully at price ₹{buy_price:.2f}"
    except sqlite3.IntegrityError:
        return False, "Error adding holding"

def get_client_holdings(client_id):
    return execute_query("""
        SELECT ticker, quantity, buy_price, buy_date
        FROM holdings
        WHERE client_id = ?
    """, (client_id,))

def get_stock_data(ticker, start_date, end_date):
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

def format_change(value):
    if pd.isna(value):
        return "N/A"
    return f"+{value:,.2f}%" if value > 0 else f"{value:,.2f}%"

def format_gain_loss(value):
    return f"+₹{value:,.2f}" if value > 0 else f"-₹{abs(value):,.2f}"

def calculate_portfolio_value(holdings_df, start_date, end_date):
    all_values, investment_values = [], []
    
    for _, row in holdings_df.iterrows():
        stock_data = get_stock_data(row['ticker'], start_date, end_date)
        if stock_data is not None and not stock_data.empty:
            daily_value = stock_data['Close'] * row['quantity']
            all_values.append(daily_value)
            investment_value = pd.Series(row['buy_price'] * row['quantity'], index=daily_value.index)
            investment_values.append(investment_value)
    
    if not all_values:
        return pd.DataFrame(), pd.DataFrame()
    
    portfolio_value = pd.concat(all_values, axis=1).sum(axis=1)
    investment_value = pd.concat(investment_values, axis=1).sum(axis=1)
    
    return portfolio_value, investment_value

def generate_portfolio_report(client_id, holdings_df, portfolio_value, investment_value):
    client_info = execute_query("""
        SELECT clients.name as client_name, families.name as family_name
        FROM clients 
        JOIN families ON clients.family_id = families.id
        WHERE clients.id = ?
    """, (client_id,))
    
    client_name = client_info['client_name'].iloc[0]
    family_name = client_info['family_name'].iloc[0]

    total_current_value = portfolio_value.iloc[-1] if not portfolio_value.empty else 0
    total_investment = investment_value.iloc[-1] if not investment_value.empty else 0
    total_return_pct = ((total_current_value - total_investment) / total_investment) * 100 if total_investment != 0 else 0
    
    report = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .summary-box {{ 
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
            }}
            .positive {{ color: #28a745; }}
            .negative {{ color: #dc3545; }}
            table {{ 
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{ 
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{ background-color: #f8f9fa; }}
            .report-date {{
                text-align: right;
                color: #666;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="report-date">
            Report generated on: {datetime.now().strftime('%B %d, %Y %H:%M')}
        </div>
        
        <div class="header">
            <h1>Portfolio Report</h1>
            <h2>{client_name} - {family_name}</h2>
        </div>

        <div class="summary-box">
            <h3>Portfolio Summary</h3>
            <p>Current Portfolio Value: ₹{total_current_value:,.2f}</p>
            <p>Total Investment: ₹{total_investment:,.2f}</p>
            <p>Total Return: <span class="{'positive' if total_return_pct > 0 else 'negative'}">
                {format_change(total_return_pct)}</span></p>
        </div>

        <h3>Holdings Details</h3>
        <table>
            <tr>
                <th>Stock</th>
                <th>Quantity</th>
                <th>Buy Price</th>
                <th>Current Price</th>
                <th>Total Return</th>
                <th>Gain/Loss</th>
            </tr>
    """
    
    end_date = datetime.now()
    for _, holding in holdings_df.iterrows():
        current_data = get_stock_data(
            holding.get('ticker', ''),
            end_date - timedelta(days=7),
            end_date
        )
        
        if current_data is not None and not current_data.empty:
            current_price = current_data['Close'].iloc[-1]
            abs_gain = (current_price - holding.get('buy_price', 0)) * holding.get('quantity', 0)
            abs_gain_pct = ((current_price - holding.get('buy_price', 0)) / holding.get('buy_price', 1)) * 100
            
            report += f"""
                <tr>
                    <td>{holding.get('ticker', '').replace('.NS', '')}</td>
                    <td>{holding.get('quantity', 0)}</td>
                    <td>₹{holding.get('buy_price', 0):,.2f}</td>
                    <td>₹{current_price:,.2f}</td>
                    <td class="{'positive' if abs_gain_pct > 0 else 'negative'}">
                        {format_change(abs_gain_pct)}</td>
                    <td class="{'positive' if abs_gain > 0 else 'negative'}">
                        {format_gain_loss(abs_gain)}</td>
                </tr>
            """
    
    report += """
        </table>
        
        <div style="margin-top: 40px;">
            <p><em>Note: This report provides a snapshot of the portfolio at the time of generation. 
            Market values and returns are subject to change.</em></p>
        </div>
    </body>
    </html>
    """
    
    return report

def client_management_tab():
    st.header("Client Management")
    
    st.subheader("Create New Family")
    new_family = st.text_input("Enter Family Name")
    if st.button("Add Family"):
        if new_family:
            if add_family(new_family):
                st.success(f"Family '{new_family}' added successfully!")
            else:
                st.error("Family already exists!")
    
    families = get_all_families()
    if not families.empty:
        st.subheader("Existing Families")
        st.dataframe(families[['name']], hide_index=True)
    
    st.markdown("---")
    st.subheader("Create New Client")
    
    if not families.empty:
        new_client = st.text_input("Enter Client Name")
        selected_family = st.selectbox(
            "Select Family",
            options=families['id'].tolist(),
            format_func=lambda x: families.loc[families['id'] == x, 'name'].iloc[0],
            key="select_family"
        )
        
        if st.button("Add Client"):
            if new_client and selected_family:
                if add_client(new_client, selected_family):
                    st.success(f"Client '{new_client}' added successfully!")
                else:
                    st.error("Client already exists in this family!")
    else:
        st.warning("Please create a family first!")
    
    clients = get_all_clients()
    if not clients.empty:
        st.subheader("Existing Clients")
        st.dataframe(clients[['name', 'family_name']], hide_index=True)

def portfolio_management_tab():
    st.header("Portfolio Management")
    
    clients = get_all_clients()
    if clients.empty:
        st.warning("No clients found. Please add clients first!")
        return
    
    selected_client = st.selectbox(
        "Select Client",
        options=clients['id'].tolist(),
        format_func=lambda x: f"{clients.loc[clients['id'] == x, 'name'].iloc[0]} "
                            f"({clients.loc[clients['id'] == x, 'family_name'].iloc[0]})",
        key="select_client_portfolio"
    )
    
    st.subheader("Add New Stock")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.text_input("Enter Stock Symbol (e.g., RELIANCE, TCS)")
        quantity = st.number_input("Quantity", min_value=1, value=1)
    
    with col2:
        buy_date = st.date_input(
            "Purchase Date",
            value=datetime.now(),
            max_value=datetime.now()
        )
    
    if st.button("Add Stock"):
        if ticker and quantity and buy_date:
            success, message = add_holding(
                selected_client,
                ticker,
                quantity,
                buy_date
            )
            if success:
                st.success(message)
            else:
                st.error(message)

def portfolio_visualization_tab():
    st.header("Portfolio Dashboard")
    
    clients = get_all_clients()
    if clients.empty:
        st.warning("No clients found. Please add clients first!")
        return
    
    selected_client = st.sidebar.selectbox(
        "Select Client",
        options=clients['id'].tolist(),
        format_func=lambda x: f"{clients.loc[clients['id'] == x, 'name'].iloc[0]} "
                            f"({clients.loc[clients['id'] == x, 'family_name'].iloc[0]})",
        key="select_client_dashboard"
    )
    
    holdings_df = get_client_holdings(selected_client)
    
    if holdings_df.empty:
        st.warning("No holdings found for selected client.")
        return
    
    end_date = datetime.now()
    start_date = min(pd.to_datetime(holdings_df['buy_date']))
    portfolio_value, investment_value = calculate_portfolio_value(holdings_df, start_date, end_date)
    
    if not portfolio_value.empty:
        returns_pct = ((portfolio_value - investment_value) / investment_value) * 100
        
        st.subheader("Portfolio Performance")
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=portfolio_value.index,
            y=portfolio_value.values,
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.1)'
        ))
        
        fig.add_trace(go.Scatter(
            x=returns_pct.index,
            y=returns_pct.values,
            mode='lines',
            name='Return %',
            line=dict(color='#2ca02c', width=2),
            yaxis='y2'
        ))
        
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
        
        st.markdown("### Current Holdings")
        holdings_data = []
        
        for _, holding in holdings_df.iterrows():
            current_data = get_stock_data(
                holding.get('ticker', ''), 
                end_date - timedelta(days=7),
                end_date
            )
            
            year_ago = end_date - timedelta(days=365)
            yearly_data = get_stock_data(
                holding.get('ticker', ''), 
                year_ago,
                end_date
            )
            
            if current_data is not None and not current_data.empty:
                current_price = current_data['Close'].iloc[-1]
                daily_change = current_data['Close'].pct_change().iloc[-1] * 100
                
                year_return = None
                if yearly_data is not None and not yearly_data.empty and len(yearly_data) > 1:
                    year_return = ((current_price - yearly_data['Close'].iloc[0]) / yearly_data['Close'].iloc[0]) * 100
                
                abs_gain = (current_price - holding.get('buy_price', 0)) * holding.get('quantity', 0)
                abs_gain_pct = ((current_price - holding.get('buy_price', 0)) / holding.get('buy_price', 1)) * 100
                
                holdings_data.append({
                    'Ticker': holding.get('ticker', '').replace('.NS', ''),
                    'Quantity': holding.get('quantity', 0),
                    'Buy Price': f"₹{holding.get('buy_price', 0):,.2f}",
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
            
            total_current_value = portfolio_value.iloc[-1] if not portfolio_value.empty else 0
            total_investment = investment_value.iloc[-1] if not investment_value.empty else 0
            total_return_pct = ((total_current_value - total_investment) / total_investment) * 100 if total_investment != 0 else 0
            
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
                        st.markdown("---")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("Generate Portfolio Report", type="primary"):
                    report_html = generate_portfolio_report(
                        selected_client,
                        holdings_df,
                        portfolio_value,
                        investment_value
                    )
                    
                    try:
                        # Configure pdfkit options
                        options = {
                            'page-size': 'A4',
                            'margin-top': '0.75in',
                            'margin-right': '0.75in',
                            'margin-bottom': '0.75in',
                            'margin-left': '0.75in',
                            'encoding': "UTF-8",
                            'no-outline': None
                        }
                        
                        # Convert HTML to PDF
                        pdf = pdfkit.from_string(report_html, False, options=options)
                        
                        # Create a download button for PDF
                        st.download_button(
                            label="📥 Download PDF Report",
                            data=pdf,
                            file_name=f"portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error("Could not generate PDF. Falling back to HTML report.")
                        # Fallback to HTML download
                        st.download_button(
                            label="📥 Download HTML Report",
                            data=report_html,
                            file_name=f"portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                            mime="text/html"
                        )
            
            with col2:
                # Add Excel export functionality
                if st.button("Export Data to Excel", type="secondary"):
                    # Create Excel file in memory
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        # Portfolio Summary
                        summary_data = pd.DataFrame({
                            'Metric': ['Total Portfolio Value', 'Total Investment', 'Total Return'],
                            'Value': [
                                f"₹{total_current_value:,.2f}",
                                f"₹{total_investment:,.2f}",
                                format_change(total_return_pct)
                            ]
                        })
                        summary_data.to_excel(writer, sheet_name='Portfolio Summary', index=False)
                        
                        # Holdings Details
                        holdings_df.to_excel(writer, sheet_name='Holdings Details', index=False)
                        
                        # Performance Data
                        perf_data = pd.DataFrame({
                            'Date': portfolio_value.index,
                            'Portfolio Value': portfolio_value.values,
                            'Investment Value': investment_value.values,
                            'Returns %': returns_pct.values
                        })
                        perf_data.to_excel(writer, sheet_name='Performance Data', index=False)
                    
                    # Create download button
                    excel_data = output.getvalue()
                    st.download_button(
                        label="📥 Download Excel Report",
                        data=excel_data,
                        file_name=f"portfolio_data_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )


def main():
    set_page_config()
    apply_custom_css()
    init_db()
    
    tab1, tab2, tab3 = st.tabs([
        "Client Management",
        "Portfolio Management",
        "Portfolio Dashboard"
    ])
    
    with tab1:
        client_management_tab()
    
    with tab2:
        portfolio_management_tab()
    
    with tab3:
        portfolio_visualization_tab()

if __name__ == "__main__":
    main()