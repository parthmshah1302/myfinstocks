from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import clients, holdings, prices, portfolio

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Stock Portfolio Management System for Indian Equities (NSE/BSE)",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clients.router, prefix=settings.API_PREFIX)
app.include_router(holdings.router, prefix=settings.API_PREFIX)
app.include_router(prices.router, prefix=settings.API_PREFIX)
app.include_router(portfolio.router, prefix=settings.API_PREFIX)

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "description": "Stock Portfolio Management System for Indian Equities",
        "docs": f"{settings.API_PREFIX}/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "MyFinStocks API"}