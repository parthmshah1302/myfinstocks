from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Holding, Client
from ..models.schemas import HoldingCreate, HoldingUpdate, HoldingResponse

router = APIRouter(prefix="/holdings", tags=["Holdings"])

@router.post("/", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED)
def create_holding(holding: HoldingCreate, db: Session = Depends(get_db)):
    """Add a stock to a client's portfolio"""
    client = db.query(Client).filter(Client.id == holding.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {holding.client_id} not found"
        )
    
    existing = db.query(Holding).filter(
        Holding.client_id == holding.client_id,
        Holding.symbol == holding.symbol
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Client already has holdings for {holding.symbol}"
        )
    
    db_holding = Holding(**holding.model_dump())
    db.add(db_holding)
    db.commit()
    db.refresh(db_holding)
    return db_holding

@router.get("/client/{client_id}", response_model=List[HoldingResponse])
def get_client_holdings(client_id: int, db: Session = Depends(get_db)):
    """Get all holdings for a specific client"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found"
        )
    
    holdings = db.query(Holding).filter(Holding.client_id == client_id).all()
    return holdings

@router.get("/{holding_id}", response_model=HoldingResponse)
def get_holding(holding_id: int, db: Session = Depends(get_db)):
    """Get a specific holding"""
    holding = db.query(Holding).filter(Holding.id == holding_id).first()
    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holding with id {holding_id} not found"
        )
    return holding

@router.put("/{holding_id}", response_model=HoldingResponse)
def update_holding(holding_id: int, holding_update: HoldingUpdate, db: Session = Depends(get_db)):
    """Update a holding (e.g., change quantity)"""
    db_holding = db.query(Holding).filter(Holding.id == holding_id).first()
    if not db_holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holding with id {holding_id} not found"
        )
    
    update_data = holding_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_holding, key, value)
    
    db.commit()
    db.refresh(db_holding)
    return db_holding

@router.delete("/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holding(holding_id: int, db: Session = Depends(get_db)):
    """Remove a holding from portfolio"""
    db_holding = db.query(Holding).filter(Holding.id == holding_id).first()
    if not db_holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holding with id {holding_id} not found"
        )
    
    db.delete(db_holding)
    db.commit()
    return None

@router.get("/stocks/search")
def search_stocks(query: str, db: Session = Depends(get_db)):
    """Search for stocks in the database"""
    
    holdings = db.query(Holding).filter(
        (Holding.symbol.ilike(f"%{query}%")) | 
        (Holding.company_name.ilike(f"%{query}%"))
    ).all()
    
    # Get unique stocks
    unique_stocks = {}
    for h in holdings:
        if h.symbol not in unique_stocks:
            unique_stocks[h.symbol] = {
                "symbol": h.symbol,
                "company_name": h.company_name,
                "exchange": h.exchange,
                "total_quantity": 0,
                "num_clients": 0
            }
        unique_stocks[h.symbol]["total_quantity"] += h.quantity
        unique_stocks[h.symbol]["num_clients"] += 1
    
    return {
        "query": query,
        "results": list(unique_stocks.values())
    }