import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def show():
    if st.button('Go back to Home'):
        st.write('Home Page content goes here')
        return

    st.title('Stock search 📈')

    # Get the tickers from the user
    tickers = st.text_input('Enter the stock tickers (comma separated):', 'ZOMATO')

    # Split the tickers and append '.BO' to each ticker
    tickers = [ticker + '.BO' for ticker in tickers.split(',')]

    data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        data[ticker] = {
            'Current Price': info.get('currentPrice', 'N/A'),
            'Open': info.get('regularMarketOpen', 'N/A'),
            'Previous Close': info.get('regularMarketPreviousClose', 'N/A'),
            'Day Low': info.get('dayLow', 'N/A'),
            'Day High': info.get('dayHigh', 'N/A'),
            '52 Week High': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52 Week Low': info.get('fiftyTwoWeekLow', 'N/A')
        }

    df = pd.DataFrame(data).T
    st.write(df)

    for ticker in tickers:
        stock = yf.Ticker(ticker)

        # Get historical data
        history = stock.history(period='1y')

        # Plot line chart
        plt.plot(history.index, history['Close'], label=ticker)

    plt.xlabel('Date')
    plt.ylabel('Closing Price')
    plt.title('Historical Stock Prices')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(plt)