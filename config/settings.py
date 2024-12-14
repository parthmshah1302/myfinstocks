from pathlib import Path
from datetime import datetime
import os

# Application Settings
APP_NAME = "Portfolio Management System"
VERSION = "1.0.0"
DEBUG = True

# Path Settings
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = os.path.join(BASE_DIR, "portfolio.db")

# Database Settings
DB_SETTINGS = {
    "sqlite": {
        "path": DATABASE_PATH,
        "timeout": 30,  # seconds
        "check_same_thread": False
    }
}

# Stock Market Settings
STOCK_EXCHANGE_SUFFIX = ".NS"  # For Indian stocks (NSE)
DEFAULT_CURRENCY = "₹"
MARKET_HOURS = {
    "open": "09:15",
    "close": "15:30"
}
MARKET_TIMEZONE = "Asia/Kolkata"

# Report Generation Settings
REPORT_SETTINGS = {
    "pdf": {
        "page_size": "A4",
        "margins": {
            "top": "0.75in",
            "right": "0.75in",
            "bottom": "0.75in",
            "left": "0.75in"
        },
        "encoding": "UTF-8"
    },
    "excel": {
        "engine": "openpyxl",
        "sheet_names": {
            "summary": "Portfolio Summary",
            "holdings": "Holdings Details",
            "performance": "Performance Analysis"
        }
    }
}

# Cache Settings
CACHE_SETTINGS = {
    "stock_data": {
        "ttl": 300,  # 5 minutes
        "max_size": 100  # number of items
    }
}

# UI Settings
UI_SETTINGS = {
    "theme": {
        "primaryColor": "#1f77b4",
        "backgroundColor": "#ffffff",
        "secondaryBackgroundColor": "#f8f9fa",
        "textColor": "#31333F",
        "font": "sans-serif"
    },
    "charts": {
        "default_height": 500,
        "colors": {
            "positive": "#28a745",
            "negative": "#dc3545",
            "neutral": "#6c757d"
        }
    },
    "tables": {
        "page_size": 10,
        "max_height": "600px"
    }
}

# API Rate Limits
RATE_LIMITS = {
    "yfinance": {
        "calls_per_minute": 30,
        "burst_limit": 60
    }
}

# Logging Settings
LOG_SETTINGS = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "app.log"),
            "mode": "a",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "file"],
            "level": "INFO",
            "propagate": True
        }
    }
}

# Feature Flags
FEATURES = {
    "enable_excel_export": True,
    "enable_pdf_export": True,
    "enable_real_time_updates": True,
    "enable_email_reports": False,
    "enable_advanced_analytics": True
}

def is_market_open():
    """Check if the market is currently open"""
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    return MARKET_HOURS["open"] <= current_time <= MARKET_HOURS["close"]

def get_db_uri():
    """Get database URI based on settings"""
    return f"sqlite:///{DB_SETTINGS['sqlite']['path']}"

def get_report_path():
    """Get path for saving reports"""
    reports_dir = os.path.join(BASE_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    return reports_dir

# Initialize required directories
os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "reports"), exist_ok=True)