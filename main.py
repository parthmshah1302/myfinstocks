from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import date, datetime
import pandas as pd
import io
import yfinance as yf

from database import get_db, create_tables, Client, ClientHolding, Stock

app = FastAPI(title="Stock Portfolio MVP")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve frontend
@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

# Create tables on startup
create_tables()

# Pydantic models
class ClientCreate(BaseModel):
    name: str
    email: str

class ClientResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

class HoldingCreate(BaseModel):
    stock_symbol: str
    quantity: int
    purchase_date: date

class PortfolioItem(BaseModel):
    stock_symbol: str
    quantity: int
    purchase_date: date
    current_price: float
    current_value: float
    gain_loss: float

# Client endpoints
@app.post("/clients", response_model=ClientResponse)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    db_client = db.query(Client).filter(Client.email == client.email).first()
    if db_client:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new client
    db_client = Client(name=client.name, email=client.email)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    
    return db_client

@app.get("/clients")
def get_all_clients(db: Session = Depends(get_db)):
    clients = db.query(Client).all()
    return clients

@app.get("/clients/{client_id}")
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

# Holdings endpoints
@app.post("/clients/{client_id}/holdings")
def add_holding(client_id: int, holding: HoldingCreate, db: Session = Depends(get_db)):
    # Check if client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Add holding
    db_holding = ClientHolding(
        client_id=client_id,
        stock_symbol=holding.stock_symbol.upper(),
        quantity=holding.quantity,
        purchase_date=holding.purchase_date
    )
    db.add(db_holding)
    
    # Add stock to stocks table if not exists
    stock = db.query(Stock).filter(Stock.symbol == holding.stock_symbol.upper()).first()
    if not stock:
        db_stock = Stock(symbol=holding.stock_symbol.upper())
        db.add(db_stock)
    
    db.commit()
    return {"message": "Holding added successfully"}

@app.post("/clients/{client_id}/holdings/upload")
async def upload_holdings_csv(client_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Check if client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read CSV
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate columns
        required_columns = {'stock_symbol', 'quantity', 'purchase_date'}
        if not required_columns.issubset(df.columns):
            raise HTTPException(status_code=400, detail=f"CSV must contain columns: {required_columns}")
        
        # Process each row
        added_count = 0
        for _, row in df.iterrows():
            # Add holding
            db_holding = ClientHolding(
                client_id=client_id,
                stock_symbol=row['stock_symbol'].upper(),
                quantity=int(row['quantity']),
                purchase_date=pd.to_datetime(row['purchase_date']).date()
            )
            db.add(db_holding)
            
            # Add stock to stocks table if not exists
            stock = db.query(Stock).filter(Stock.symbol == row['stock_symbol'].upper()).first()
            if not stock:
                db_stock = Stock(symbol=row['stock_symbol'].upper())
                db.add(db_stock)
            
            added_count += 1
        
        db.commit()
        return {"message": f"Successfully added {added_count} holdings"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")

@app.get("/clients/{client_id}/portfolio")
def get_client_portfolio(client_id: int, db: Session = Depends(get_db)):
    # Check if client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get holdings with current prices
    holdings = db.query(ClientHolding).filter(ClientHolding.client_id == client_id).all()
    
    portfolio = []
    total_value = 0
    
    for holding in holdings:
        # Get current price from stocks table
        stock = db.query(Stock).filter(Stock.symbol == holding.stock_symbol).first()
        current_price = stock.current_price if stock and stock.current_price else 0
        
        current_value = current_price * holding.quantity
        total_value += current_value
        
        portfolio.append({
            "stock_symbol": holding.stock_symbol,
            "quantity": holding.quantity,
            "purchase_date": holding.purchase_date,
            "current_price": current_price,
            "current_value": round(current_value, 2),
            "last_updated": stock.last_updated if stock else None
        })
    
    return {
        "client": {"id": client.id, "name": client.name},
        "portfolio": portfolio,
        "total_value": round(total_value, 2)
    }

@app.post("/update-prices")
def update_stock_prices(db: Session = Depends(get_db)):
    # Get all unique stock symbols
    stocks = db.query(Stock).all()
    
    updated_count = 0
    errors = []
    
    for stock in stocks:
        try:
            # Fetch current price
            ticker = yf.Ticker(stock.symbol)
            hist = ticker.history(period='1d')
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                stock.current_price = round(current_price, 2)
                stock.last_updated = datetime.now()
                updated_count += 1
            else:
                errors.append(f"No data for {stock.symbol}")
                
        except Exception as e:
            errors.append(f"Error updating {stock.symbol}: {str(e)}")
    
    db.commit()
    
    return {
        "message": f"Updated {updated_count} stock prices",
        "errors": errors
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)