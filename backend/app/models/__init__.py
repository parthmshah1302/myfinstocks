from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Numeric, ForeignKey, BigInteger, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    email = Column(Text, unique=True)
    phone = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationship
    holdings = relationship("Holding", back_populates="client", cascade="all, delete-orphan")

class Holding(Base):
    __tablename__ = "holdings"
    
    id = Column(BigInteger, primary_key=True, index=True)
    client_id = Column(BigInteger, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(Text, nullable=False)
    company_name = Column(Text, nullable=False)
    quantity = Column(Integer, nullable=False)
    exchange = Column(Text, default="NSE")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationship
    client = relationship("Client", back_populates="holdings")
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        CheckConstraint("exchange IN ('NSE', 'BSE')", name='check_exchange_valid'),
    )

class PriceCache(Base):
    __tablename__ = "price_cache"
    
    symbol = Column(Text, primary_key=True)
    live_price = Column(Numeric(12, 2))
    yesterday_price = Column(Numeric(12, 2))
    price_30d_ago = Column(Numeric(12, 2))
    price_1y_ago = Column(Numeric(12, 2))
    last_updated = Column(TIMESTAMP, server_default=func.now())
    exchange = Column(Text, default="NSE")