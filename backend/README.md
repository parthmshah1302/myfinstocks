# MyFinStocks API

Stock Portfolio Management System for Indian Equities (NSE/BSE)

## 🚀 Features

- ✅ Multi-client portfolio management
- 📊 Real-time stock price tracking (NSE/BSE)
- 💰 Automatic P&L calculations
- 📈 Historical price tracking (Yesterday, 30d, 1yr)
- 📄 PDF portfolio reports
- 🔄 Batch price refresh
- 📱 RESTful API with auto-generated docs

## 🛠️ Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL (Supabase)
- **Stock Data:** Yahoo Finance API (yfinance)
- **PDF Generation:** ReportLab

## 📋 API Endpoints

### Clients
- `GET /api/v1/clients` - List all clients
- `POST /api/v1/clients` - Create new client
- `GET /api/v1/clients/{id}` - Get client details
- `PUT /api/v1/clients/{id}` - Update client
- `DELETE /api/v1/clients/{id}` - Delete client

### Holdings
- `POST /api/v1/holdings` - Add stock to portfolio
- `GET /api/v1/holdings/client/{id}` - Get client's holdings
- `PUT /api/v1/holdings/{id}` - Update holding
- `DELETE /api/v1/holdings/{id}` - Remove holding
- `GET /api/v1/holdings/stocks/search?query=X` - Search stocks

### Prices
- `GET /api/v1/prices/{symbol}` - Get cached price
- `POST /api/v1/prices/update` - Manual price update
- `POST /api/v1/prices/refresh/{symbol}` - Fetch from Yahoo Finance
- `POST /api/v1/prices/refresh-all-holdings` - Refresh all prices (background)

### Portfolio
- `GET /api/v1/portfolio/client/{id}` - Get full portfolio with calculations
- `GET /api/v1/portfolio/export/{id}` - Download portfolio PDF
- `GET /api/v1/portfolio/dashboard` - Get dashboard summary

## 🚀 Quick Start

1. **Clone & Setup:**
```bash
git clone <your-repo>
cd myfinstocks-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure:**
Create `.env` file:
```env
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
APP_NAME=MyFinStocks API
DEBUG=True
API_PREFIX=/api/v1
```

3. **Run:**
```bash
uvicorn app.main:app --reload
```

4. **Access:**
- API Docs: http://localhost:8000/api/v1/docs
- API: http://localhost:8000/api/v1/

## 📖 Usage Examples

### Add a Client
```bash
curl -X POST http://localhost:8000/api/v1/clients \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

### Add Holdings
```bash
curl -X POST http://localhost:8000/api/v1/holdings \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "symbol": "RELIANCE",
    "company_name": "Reliance Industries Ltd",
    "quantity": 100,
    "exchange": "NSE"
  }'
```

### Refresh Prices
```bash
curl -X POST http://localhost:8000/api/v1/prices/refresh-all-holdings
```

### Get Portfolio
```bash
curl http://localhost:8000/api/v1/portfolio/client/1
```

### Export PDF
```bash
curl http://localhost:8000/api/v1/portfolio/export/1 --output portfolio.pdf
```

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `APP_NAME` - Application name
- `DEBUG` - Debug mode (True/False)
- `API_PREFIX` - API prefix (/api/v1)

## 📊 Database Schema

- **clients** - Client information
- **holdings** - Stock holdings per client
- **price_cache** - Cached stock prices
- **portfolio_view** - Calculated portfolio view

## 🚢 Deployment

### Render
```bash
# Build: pip install -r requirements.txt
# Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Railway
Connect GitHub repo and deploy automatically.

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## 📄 License

MIT

## 🆘 Support

For issues: [GitHub Issues](your-repo-url)