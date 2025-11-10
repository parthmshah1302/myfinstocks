FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for pandas/yfinance if needed
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy backend code
COPY backend backend

# Make Python see /app/backend so `import app` works
ENV PYTHONPATH=/app/backend

# Expose the app port
EXPOSE 8080

# Start FastAPI (your app lives at backend/app/main.py as `app`)
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
