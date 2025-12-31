"""
Configuration and constants for AMK Trading Platform
"""
import os
from typing import Dict, Any

# --- File Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, 'stock_list.ods')
JOURNAL_DB_PATH = os.path.join(BASE_DIR, 'trading_journal.json')

# --- Screening Parameters ---
SCREENING_PARAMS = {
    "min_daily_volume": 500_000,  # Minimum daily trading volume
    "atr_min_pct": 2.0,  # Minimum ATR as % of price
    "atr_max_pct": 5.0,  # Maximum ATR as % of price
    "min_delivery_pct": 40.0,  # Minimum delivery percentage
    "market_cap_threshold": 5000,  # Minimum market cap in Cr
    "data_period": "1y",  # Historical data period for analysis
    "data_interval": "1d",  # Data interval (daily)
}

# --- Technical Indicator Parameters ---
INDICATOR_PARAMS = {
    "bollinger_length": 20,
    "bollinger_std": 2.0,
    "keltner_length": 20,
    "keltner_atr_mult": 1.5,
    "keltner_atr_length": 10,
    "rsi_length": 14,
    "rsi_overbought": 70,
    "rsi_oversold": 30,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "ema_200": 200,
    "volume_profile_bins": 20,
    "value_area_pct": 70,
}

# --- TTM Squeeze Levels ---
TTM_SQUEEZE_LEVELS = {
    "red": {
        "name": "High Compression",
        "atr_multiplier": 1.0,
        "color": "#FF0000",
        "compression_level": 3,
    },
    "orange": {
        "name": "Mid Compression",
        "atr_multiplier": 1.5,
        "color": "#FF6B00",
        "compression_level": 2,
    },
    "gray": {
        "name": "Low Compression",
        "atr_multiplier": 2.0,
        "color": "#808080",
        "compression_level": 1,
    },
}

# --- ML Model Parameters ---
ML_PARAMS = {
    "model_type": "xgboost",  # xgboost or random_forest
    "test_size": 0.2,
    "random_state": 42,
    "conviction_threshold": 0.75,
    "prediction_window": 10,  # days
    "target_return": 0.05,  # 5% expected return
    "train_lookback": 252,  # 1 year of trading days
}

# --- Performance Metrics Thresholds ---
PERFORMANCE_THRESHOLDS = {
    "min_profit_factor": 1.5,
    "min_win_rate": 0.50,
    "max_drawdown_pct": 20.0,
}

# --- API Configuration ---
API_CONFIG = {
    "title": "AMK Trading API",
    "version": "2.0.0",
    "description": "Advanced Indian Equity Swing Trading Platform",
    "host": "0.0.0.0",
    "port": 8000,
    "reload": False,
}

# --- Cache Configuration ---
CACHE_CONFIG = {
    "enabled": True,
    "ttl_seconds": 3600,  # 1 hour cache for technical indicators
    "max_size": 1000,
}

def get_config() -> Dict[str, Any]:
    """Get complete configuration dictionary."""
    return {
        "screening": SCREENING_PARAMS,
        "indicators": INDICATOR_PARAMS,
        "ttm_squeeze": TTM_SQUEEZE_LEVELS,
        "ml": ML_PARAMS,
        "performance": PERFORMANCE_THRESHOLDS,
        "api": API_CONFIG,
        "cache": CACHE_CONFIG,
    }
