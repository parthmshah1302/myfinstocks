from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./portfolio.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationship
    holdings = relationship("ClientHolding", back_populates="client")

class ClientHolding(Base):
    __tablename__ = "client_holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    stock_symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    purchase_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    client = relationship("Client", back_populates="holdings")

class Stock(Base):
    __tablename__ = "stocks"
    
    symbol = Column(String, primary_key=True, index=True)
    current_price = Column(Float, nullable=True)
    last_updated = Column(DateTime, nullable=True)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()