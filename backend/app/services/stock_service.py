import yfinance as yf
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
            logger.info(f"Fetching data for {yahoo_symbol}")
            
            # Create ticker and fetch history
            ticker = yf.Ticker(yahoo_symbol)
            hist = ticker.history(period="1y")
            
            if hist.empty:
                logger.warning(f"No data for {yahoo_symbol}")
                return None
            
            # Extract prices
            live_price = float(hist['Close'].iloc[-1])
            yesterday_price = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else live_price
            
            # 30 days ago (~22 trading days)
            price_30d_ago = float(hist['Close'].iloc[-22]) if len(hist) >= 22 else live_price
            
            # 1 year ago (~252 trading days)
            if len(hist) >= 252:
                price_1y_ago = float(hist['Close'].iloc[-252])
            else:
                price_1y_ago = float(hist['Close'].iloc[0])
            
            logger.info(f"✅ Success: {yahoo_symbol} = {live_price}")
            
            return {
                "symbol": symbol,
                "live_price": Decimal(str(round(live_price, 2))),
                "yesterday_price": Decimal(str(round(yesterday_price, 2))),
                "price_30d_ago": Decimal(str(round(price_30d_ago, 2))),
                "price_1y_ago": Decimal(str(round(price_1y_ago, 2))),
                "exchange": exchange
            }
            
        except Exception as e:
            logger.error(f"Error: {symbol} - {str(e)}")
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