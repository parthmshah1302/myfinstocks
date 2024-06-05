import streamlit as st
import yfinance as yf
import pandas as pd
import os
import json

def show():

    # Get the list of JSON files in the data folder
    files = [f for f in os.listdir('data') if f.endswith('.json')]

    # Create a button for each user
    selected_file = st.selectbox("Select a file", files)

    # Load the user data from the selected JSON file
    with open(f'data/{selected_file}') as f:
        user_data = json.load(f)
    
    user_name = user_data.get('name', 'Unknown')  # Get the user name from the JSON data
    
    st.title(f"Portfolio for {user_name} 📈")
    if st.button("Load"):
        # Load the user data from the selected JSON file
        with open(f'data/{selected_file}') as f:
            user_data = json.load(f)

            data = {}
            for ticker, stock_info in user_data['stocks'].items():
                stock = yf.Ticker(ticker)
                info = stock.info

                # Calculate the current value and gain/loss
                current_price = info.get('currentPrice', 'N/A')
                if current_price != 'N/A':
                    current_price = float(current_price)
                quantity = int(stock_info['quantity'])
                buying_price = float(stock_info['buying_price'])

                if current_price != 'N/A':
                    current_value = quantity * current_price
                    gain_loss = current_value - (quantity * buying_price)
                else:
                    current_value = 'N/A'
                    gain_loss = 'N/A'

                # Get additional data
                open_price = info.get('regularMarketOpen', 'N/A')
                previous_close = info.get('regularMarketPreviousClose', 'N/A')
                fifty_two_week_high = info.get('fiftyTwoWeekHigh', 'N/A')
                fifty_two_week_low = info.get('fiftyTwoWeekLow', 'N/A')

                # Get historical data
                history = stock.history(period='1y')

                # Calculate 1 day gain/loss
                one_day_gain_loss = round(current_price - history['Close'].iloc[-2], 2) if current_price != 'N/A' and len(history) > 1 else 'N/A'

                # Calculate fifty two week gain/loss
                fifty_two_week_gain_loss = round(current_price - history['Close'].iloc[0], 2) if current_price != 'N/A' and len(history) > 0 else 'N/A'
                if any(value == 'N/A' for value in [current_price, current_value, gain_loss, open_price, previous_close, one_day_gain_loss, fifty_two_week_high, fifty_two_week_low, fifty_two_week_gain_loss]):
                    continue
                
                data[ticker] = {
                    'Quantity': quantity,
                    'Buying Price': buying_price,
                    'Current Price': current_price,
                    'Current Value': current_value,
                    'Gain/Loss': gain_loss,
                    '1 Day Gain/Loss': one_day_gain_loss,
                    '52 Week Gain/Loss': fifty_two_week_gain_loss,
                    'Open': open_price,
                    'Previous Close': previous_close,
                    '52 Week High': fifty_two_week_high,
                    '52 Week Low': fifty_two_week_low,
                }

            df = pd.DataFrame(data).T

            # Calculate the sum of the specified columns and append it to the DataFrame
            df.loc['Total'] = df[['Buying Price', 'Current Value', 'Gain/Loss', '1 Day Gain/Loss', '52 Week Gain/Loss']].sum()

            df_to_display = df.drop(columns=['Buying Price','Gain/Loss'])

            st.write(df_to_display)