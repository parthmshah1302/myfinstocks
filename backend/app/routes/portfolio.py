from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from decimal import Decimal
from app.database import get_db
from app.models import Client
from app.models.schemas import PortfolioSummary, PortfolioHolding
from datetime import datetime

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

@router.get("/client/{client_id}", response_model=PortfolioSummary)
def get_client_portfolio(client_id: int, db: Session = Depends(get_db)):
    """Get complete portfolio for a client with calculated values"""
    
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found"
        )
    
    query = text("""
        SELECT * FROM portfolio_view 
        WHERE client_id = :client_id
        ORDER BY symbol
    """)
    
    result = db.execute(query, {"client_id": client_id})
    rows = result.fetchall()
    
    if not rows:
        return PortfolioSummary(
            client_id=client_id,
            client_name=client.name,
            client_email=client.email,
            total_current_value=Decimal("0.00"),
            total_yesterday_value=Decimal("0.00"),
            total_day_change=Decimal("0.00"),
            total_day_change_percent=Decimal("0.00"),
            holdings=[],
            last_updated=datetime.now()
        )
    
    holdings = []
    total_current = Decimal("0.00")
    total_yesterday = Decimal("0.00")
    
    for row in rows:
        holding = PortfolioHolding(
            id=row.id,
            symbol=row.symbol,
            company_name=row.company_name,
            exchange=row.exchange,
            quantity=row.quantity,
            live_price=row.live_price,
            yesterday_price=row.yesterday_price,
            price_30d_ago=row.price_30d_ago,
            price_1y_ago=row.price_1y_ago,
            current_value=row.current_value or Decimal("0.00"),
            yesterday_value=row.yesterday_value or Decimal("0.00"),
            value_30d_ago=row.value_30d_ago or Decimal("0.00"),
            value_1y_ago=row.value_1y_ago or Decimal("0.00"),
            day_change=row.day_change or Decimal("0.00"),
            day_change_percent=row.day_change_percent or Decimal("0.00"),
            price_updated_at=row.price_updated_at
        )
        holdings.append(holding)
        total_current += holding.current_value
        total_yesterday += holding.yesterday_value
    
    total_change = total_current - total_yesterday
    total_change_percent = Decimal("0.00")
    if total_yesterday > 0:
        total_change_percent = (total_change / total_yesterday) * 100
    
    return PortfolioSummary(
        client_id=client_id,
        client_name=client.name,
        client_email=client.email,
        total_current_value=total_current,
        total_yesterday_value=total_yesterday,
        total_day_change=total_change,
        total_day_change_percent=round(total_change_percent, 2),
        holdings=holdings,
        last_updated=datetime.now()
    )

@router.get("/export/{client_id}")
def export_portfolio_pdf(client_id: int, db: Session = Depends(get_db)):
    """Export portfolio as PDF (placeholder for now)"""
    portfolio = get_client_portfolio(client_id, db)
    
    return {
        "message": "PDF generation will be implemented in Phase 2",
        "client_id": client_id,
        "portfolio_summary": {
            "total_value": str(portfolio.total_current_value),
            "total_holdings": len(portfolio.holdings)
        }
    }