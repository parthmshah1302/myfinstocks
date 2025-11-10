from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# ===== CLIENT SCHEMAS =====
class ClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class ClientResponse(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ===== HOLDING SCHEMAS =====
class HoldingBase(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=50)
    company_name: str = Field(..., min_length=1, max_length=200)
    quantity: int = Field(..., gt=0)
    exchange: str = Field(default="NSE", pattern="^(NSE|BSE)$")

class HoldingCreate(HoldingBase):
    client_id: int

class HoldingUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)
    company_name: Optional[str] = Field(None, min_length=1, max_length=200)

class HoldingResponse(HoldingBase):
    id: int
    client_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ===== PRICE SCHEMAS =====
class PriceData(BaseModel):
    symbol: str
    live_price: Optional[Decimal] = None
    yesterday_price: Optional[Decimal] = None
    price_30d_ago: Optional[Decimal] = None
    price_1y_ago: Optional[Decimal] = None
    last_updated: Optional[datetime] = None
    exchange: str = "NSE"
    
    class Config:
        from_attributes = True

class PriceUpdateRequest(BaseModel):
    symbol: str
    live_price: Decimal = Field(..., ge=0)
    yesterday_price: Optional[Decimal] = Field(None, ge=0)
    price_30d_ago: Optional[Decimal] = Field(None, ge=0)
    price_1y_ago: Optional[Decimal] = Field(None, ge=0)

# ===== PORTFOLIO SCHEMAS =====
class PortfolioHolding(BaseModel):
    id: int
    symbol: str
    company_name: str
    exchange: str
    quantity: int
    live_price: Optional[Decimal]
    yesterday_price: Optional[Decimal]
    price_30d_ago: Optional[Decimal]
    price_1y_ago: Optional[Decimal]
    current_value: Decimal
    yesterday_value: Decimal
    value_30d_ago: Decimal
    value_1y_ago: Decimal
    day_change: Decimal
    day_change_percent: Decimal
    price_updated_at: Optional[datetime]

class PortfolioSummary(BaseModel):
    client_id: int
    client_name: str
    client_email: Optional[str]
    total_current_value: Decimal
    total_yesterday_value: Decimal
    total_day_change: Decimal
    total_day_change_percent: Decimal
    holdings: List[PortfolioHolding]
    last_updated: datetime