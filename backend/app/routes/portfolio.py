from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from decimal import Decimal
from app.database import get_db
from app.models import Client
from app.models.schemas import PortfolioSummary, PortfolioHolding
from app.services.pdf_service import PDFService
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
    """Export portfolio as PDF"""
    
    # Get portfolio data
    portfolio = get_client_portfolio(client_id, db)
    
    # Convert to dict for PDF generation
    portfolio_dict = {
        "client_name": portfolio.client_name,
        "client_email": portfolio.client_email,
        "total_current_value": float(portfolio.total_current_value),
        "total_yesterday_value": float(portfolio.total_yesterday_value),
        "total_day_change": float(portfolio.total_day_change),
        "total_day_change_percent": float(portfolio.total_day_change_percent),
        "holdings": [
            {
                "symbol": h.symbol,
                "company_name": h.company_name,
                "quantity": h.quantity,
                "live_price": h.live_price,
                "current_value": h.current_value,
                "day_change": h.day_change,
                "day_change_percent": h.day_change_percent,
            }
            for h in portfolio.holdings
        ]
    }
    
    # Generate PDF
    pdf_buffer = PDFService.generate_portfolio_pdf(portfolio_dict)
    
    # Return as downloadable file
    filename = f"portfolio_{portfolio.client_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.get("/dashboard")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get overall dashboard with all clients and total values"""
    
    clients = db.query(Client).all()
    
    total_portfolio_value = Decimal("0.00")
    total_day_change = Decimal("0.00")
    client_summaries = []
    
    for client in clients:
        portfolio = get_client_portfolio(client.id, db)
        
        client_summaries.append({
            "client_id": client.id,
            "client_name": client.name,
            "portfolio_value": portfolio.total_current_value,
            "day_change": portfolio.total_day_change,
            "day_change_percent": portfolio.total_day_change_percent,
            "num_holdings": len(portfolio.holdings)
        })
        
        total_portfolio_value += portfolio.total_current_value
        total_day_change += portfolio.total_day_change
    
    total_change_percent = Decimal("0.00")
    if total_portfolio_value > 0:
        total_change_percent = (total_day_change / (total_portfolio_value - total_day_change)) * 100
    
    return {
        "total_clients": len(clients),
        "total_portfolio_value": total_portfolio_value,
        "total_day_change": total_day_change,
        "total_day_change_percent": round(total_change_percent, 2),
        "clients": client_summaries,
        "last_updated": datetime.now()
    }
