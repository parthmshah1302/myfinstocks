from typing import Tuple, Dict, Any
from datetime import datetime, timedelta, date
import pandas as pd
import yfinance as yf
import logging

logger = logging.getLogger(__name__)

class PortfolioService:
    def __init__(self, db):
        self.db = db

    def _get_valid_date_range(self) -> Tuple[datetime, datetime]:
        """Get valid date range for stock data"""
        current_date = datetime.now()
        # If it's a weekend or future date, adjust to last business day
        while current_date.weekday() > 4:  # 5 is Saturday, 6 is Sunday
            current_date = current_date - timedelta(days=1)
        
        # For historical data, go back one year
        start_date = current_date - timedelta(days=365)
        return start_date, current_date

    def _get_stock_data(self, ticker: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Fetch stock data with proper error handling"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)
            if hist.empty:
                logger.warning(f"No data available for {ticker} between {start_date} and {end_date}")
                return None
            return hist
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            return None

    def add_holding(self, client_id: int, ticker: str, quantity: int, buy_date: date) -> Tuple[bool, str]:
        """Add a new holding to a client's portfolio"""
        # Ensure ticker has .NS suffix for Indian stocks
        ticker_full = f"{ticker}.NS" if not ticker.endswith('.NS') else ticker
        
        try:
            # Validate buy date
            if buy_date > date.today():
                return False, "Cannot set purchase date in the future"
            
            # Convert buy_date to datetime for historical data fetch
            buy_datetime = datetime.combine(buy_date, datetime.min.time())
            
            # Fetch historical data to get buy price
            hist = self._get_stock_data(
                ticker_full,
                buy_datetime,
                buy_datetime + timedelta(days=1)
            )
            
            if hist is None or hist.empty:
                return False, "No price data available for the selected date"
            
            buy_price = hist['Close'].iloc[0]
            
            # Add holding to database
            query = """
                INSERT INTO holdings (client_id, ticker, quantity, buy_price, buy_date)
                VALUES (?, ?, ?, ?, ?)
            """
            self.db.execute_query(
                query,
                (client_id, ticker_full, quantity, buy_price, buy_date),
                fetch=False
            )
            return True, f"Holding added successfully at price ₹{buy_price:.2f}"
            
        except Exception as e:
            logger.error(f"Error adding holding: {str(e)}")
            return False, f"Error adding holding: {str(e)}"

    def get_portfolio_summary(self, client_id: int) -> Dict[str, Any]:
        """Get summary of client's portfolio"""
        holdings = self.db.get_client_holdings(client_id)
        if holdings.empty:
            return {
                "total_investment": 0,
                "current_value": 0,
                "total_return": 0,
                "return_percentage": 0
            }

        end_date, _ = self._get_valid_date_range()
        current_value = 0
        total_investment = 0

        for _, holding in holdings.iterrows():
            # Calculate investment value
            investment = holding['quantity'] * holding['buy_price']
            total_investment += investment

            # Get current price
            hist = self._get_stock_data(
                holding['ticker'],
                end_date - timedelta(days=7),
                end_date
            )
            
            if hist is not None and not hist.empty:
                current_price = hist['Close'].iloc[-1]
                current_value += holding['quantity'] * current_price

        return {
            "total_investment": total_investment,
            "current_value": current_value,
            "total_return": current_value - total_investment,
            "return_percentage": ((current_value - total_investment) / total_investment * 100)
            if total_investment > 0 else 0
        }

    def get_holdings_with_current_prices(self, client_id: int) -> pd.DataFrame:
        """Get all holdings with current prices and returns"""
        holdings = self.db.get_client_holdings(client_id)
        if holdings.empty:
            return pd.DataFrame()

        end_date, _ = self._get_valid_date_range()
        current_data = []

        for _, holding in holdings.iterrows():
            hist = self._get_stock_data(
                holding['ticker'],
                end_date - timedelta(days=7),
                end_date
            )
            
            if hist is not None and not hist.empty:
                current_price = hist['Close'].iloc[-1]
                current_data.append({
                    'ticker': holding['ticker'],
                    'quantity': holding['quantity'],
                    'buy_price': holding['buy_price'],
                    'current_price': current_price,
                    'total_investment': holding['quantity'] * holding['buy_price'],
                    'current_value': holding['quantity'] * current_price,
                    'return_percentage': ((current_price - holding['buy_price']) / holding['buy_price'] * 100)
                })

        return pd.DataFrame(current_data)