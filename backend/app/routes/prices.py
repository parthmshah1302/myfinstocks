from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import PriceCache, Holding
from ..models.schemas import PriceData, PriceUpdateRequest
from ..services.stock_service import StockPriceService
from datetime import datetime

router = APIRouter(prefix="/prices", tags=["Prices"])

@router.get("/{symbol}", response_model=PriceData)
def get_price(symbol: str, db: Session = Depends(get_db)):
    """Get cached price for a symbol"""
    price = db.query(PriceCache).filter(PriceCache.symbol == symbol).first()
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No price data found for {symbol}"
        )
    return price

@router.post("/update", response_model=PriceData)
def manual_price_update(price_update: PriceUpdateRequest, db: Session = Depends(get_db)):
    """Manually update price for a symbol"""
    price = db.query(PriceCache).filter(PriceCache.symbol == price_update.symbol).first()
    
    if price:
        price.live_price = price_update.live_price
        if price_update.yesterday_price:
            price.yesterday_price = price_update.yesterday_price
        if price_update.price_30d_ago:
            price.price_30d_ago = price_update.price_30d_ago
        if price_update.price_1y_ago:
            price.price_1y_ago = price_update.price_1y_ago
        price.last_updated = datetime.now()
    else:
        price = PriceCache(**price_update.model_dump(), last_updated=datetime.now())
        db.add(price)
    
    db.commit()
    db.refresh(price)
    return price

@router.post("/refresh/{symbol}", response_model=PriceData)
def refresh_price_from_api(symbol: str, exchange: str = "NSE", db: Session = Depends(get_db)):
    """Fetch latest price from Yahoo Finance and update cache"""
    price_data = StockPriceService.fetch_stock_prices(symbol, exchange)
    
    if not price_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch price data for {symbol}"
        )
    
    price = db.query(PriceCache).filter(PriceCache.symbol == symbol).first()
    
    if price:
        price.live_price = price_data["live_price"]
        price.yesterday_price = price_data["yesterday_price"]
        price.price_30d_ago = price_data["price_30d_ago"]
        price.price_1y_ago = price_data["price_1y_ago"]
        price.last_updated = datetime.now()
        price.exchange = exchange
    else:
        price = PriceCache(
            symbol=symbol,
            live_price=price_data["live_price"],
            yesterday_price=price_data["yesterday_price"],
            price_30d_ago=price_data["price_30d_ago"],
            price_1y_ago=price_data["price_1y_ago"],
            exchange=exchange,
            last_updated=datetime.now()
        )
        db.add(price)
    
    db.commit()
    db.refresh(price)
    return price

def refresh_all_prices_task(db: Session):
    """Background task to refresh all prices"""
    holdings = db.query(Holding).all()
    unique_symbols = {(h.symbol, h.exchange) for h in holdings}
    
    for symbol, exchange in unique_symbols:
        try:
            price_data = StockPriceService.fetch_stock_prices(symbol, exchange)
            if price_data:
                price = db.query(PriceCache).filter(PriceCache.symbol == symbol).first()
                if price:
                    price.live_price = price_data["live_price"]
                    price.yesterday_price = price_data["yesterday_price"]
                    price.price_30d_ago = price_data["price_30d_ago"]
                    price.price_1y_ago = price_data["price_1y_ago"]
                    price.last_updated = datetime.now()
                else:
                    price = PriceCache(**price_data, last_updated=datetime.now())
                    db.add(price)
        except Exception as e:
            print(f"Error refreshing {symbol}: {e}")
            continue
    
    db.commit()

@router.post("/refresh-all")
def refresh_all_prices(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Refresh prices for all holdings (runs in background)"""
    background_tasks.add_task(refresh_all_prices_task, db)
    return {"message": "Price refresh initiated in background"}