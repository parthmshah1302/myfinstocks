import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Dict
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class StockPriceService:
    """Service to fetch stock prices from Yahoo Finance"""
    
    @staticmethod
    def get_yahoo_symbol(symbol: str, exchange: str) -> str:
        """Convert Indian stock symbol to Yahoo Finance format"""
        suffix = ".NS" if exchange == "NSE" else ".BO"
        return f"{symbol}{suffix}"
    
    @staticmethod
    def fetch_stock_prices(symbol: str, exchange: str = "NSE") -> Optional[Dict]:
        """
        Fetch current and historical prices for a stock
        Returns dict with live_price, yesterday_price, price_30d_ago, price_1y_ago
        """
        try:
            yahoo_symbol = StockPriceService.get_yahoo_symbol(symbol, exchange)
            stock = yf.Ticker(yahoo_symbol)
            
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=400)
            
            hist = stock.history(start=start_date, end=end_date)
            
            if hist.empty:
                logger.warning(f"No data found for {yahoo_symbol}")
                return None
            
            # Get current price (last available)
            live_price = float(hist['Close'].iloc[-1])
            
            # Get yesterday's price
            yesterday_price = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else live_price
            
            # Get 30 days ago price
            if len(hist) >= 30:
                price_30d_ago = float(hist['Close'].iloc[-30])
            else:
                price_30d_ago = live_price
            
            # Get 1 year ago price
            if len(hist) >= 252:
                price_1y_ago = float(hist['Close'].iloc[-252])
            else:
                price_1y_ago = float(hist['Close'].iloc[0])
            
            return {
                "symbol": symbol,
                "live_price": Decimal(str(round(live_price, 2))),
                "yesterday_price": Decimal(str(round(yesterday_price, 2))),
                "price_30d_ago": Decimal(str(round(price_30d_ago, 2))),
                "price_1y_ago": Decimal(str(round(price_1y_ago, 2))),
                "exchange": exchange
            }
            
        except Exception as e:
            logger.error(f"Error fetching prices for {symbol}: {str(e)}")
            return None
    
    @staticmethod
    def fetch_multiple_stocks(symbols: list, exchange: str = "NSE") -> Dict[str, Dict]:
        """Fetch prices for multiple stocks"""
        results = {}
        for symbol in symbols:
            price_data = StockPriceService.fetch_stock_prices(symbol, exchange)
            if price_data:
                results[symbol] = price_data
        return results