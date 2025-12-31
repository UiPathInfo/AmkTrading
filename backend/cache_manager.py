"""
Data caching manager to avoid yfinance rate limits
Stores market data in JSON format organized by date
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
import pandas as pd

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join(os.path.dirname(__file__), '.cache')
MARKET_DATA_CACHE = os.path.join(CACHE_DIR, 'market_data')
ANALYSIS_CACHE = os.path.join(CACHE_DIR, 'analysis')


def ensure_cache_dirs():
    """Create cache directories if they don't exist."""
    Path(CACHE_DIR).mkdir(exist_ok=True)
    Path(MARKET_DATA_CACHE).mkdir(exist_ok=True)
    Path(ANALYSIS_CACHE).mkdir(exist_ok=True)


def get_today_date() -> str:
    """Get today's date as YYYY-MM-DD string."""
    return datetime.now().strftime('%Y-%m-%d')


def get_cache_file_path(ticker: str, cache_type: str = 'market_data') -> str:
    """Get cache file path for a ticker on today's date."""
    ensure_cache_dirs()
    today = get_today_date()
    
    if cache_type == 'market_data':
        cache_file = os.path.join(MARKET_DATA_CACHE, f"{today}_{ticker}.json")
    elif cache_type == 'analysis':
        cache_file = os.path.join(ANALYSIS_CACHE, f"{today}_{ticker}.json")
    else:
        raise ValueError(f"Unknown cache type: {cache_type}")
    
    return cache_file


def save_market_data_cache(ticker: str, data: pd.DataFrame) -> bool:
    """
    Save market data to cache file.
    
    Args:
        ticker: Stock ticker
        data: DataFrame with OHLCV data
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        ensure_cache_dirs()
        cache_file = get_cache_file_path(ticker, 'market_data')
        
        # Convert DataFrame to JSON-serializable dict
        cache_data = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'data': data.reset_index().to_dict('records')
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
        
        logger.info(f"Cached market data for {ticker}: {cache_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error caching market data for {ticker}: {e}")
        return False


def load_market_data_cache(ticker: str) -> Optional[pd.DataFrame]:
    """
    Load cached market data if available.
    
    Args:
        ticker: Stock ticker
        
    Returns:
        DataFrame if cache exists, None otherwise
    """
    try:
        cache_file = get_cache_file_path(ticker, 'market_data')
        
        if not os.path.exists(cache_file):
            return None
        
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        # Convert back to DataFrame
        df = pd.DataFrame(cache_data['data'])
        
        # Convert date column to datetime index
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
        elif 'index' in df.columns:
            df['index'] = pd.to_datetime(df['index'])
            df.set_index('index', inplace=True)
        
        logger.info(f"Loaded market data cache for {ticker}: {cache_file}")
        return df
        
    except Exception as e:
        logger.error(f"Error loading market data cache for {ticker}: {e}")
        return None


def save_analysis_cache(ticker: str, analysis: Dict[str, Any]) -> bool:
    """
    Save analysis results to cache file.
    
    Args:
        ticker: Stock ticker
        analysis: Analysis result dictionary
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        ensure_cache_dirs()
        cache_file = get_cache_file_path(ticker, 'analysis')
        
        cache_data = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        logger.info(f"Cached analysis for {ticker}: {cache_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error caching analysis for {ticker}: {e}")
        return False


def load_analysis_cache(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Load cached analysis if available.
    
    Args:
        ticker: Stock ticker
        
    Returns:
        Analysis dict if cache exists, None otherwise
    """
    try:
        cache_file = get_cache_file_path(ticker, 'analysis')
        
        if not os.path.exists(cache_file):
            return None
        
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        logger.info(f"Loaded analysis cache for {ticker}: {cache_file}")
        return cache_data.get('analysis')
        
    except Exception as e:
        logger.error(f"Error loading analysis cache for {ticker}: {e}")
        return None


def clear_old_cache(days: int = 3) -> int:
    """
    Clear cache files older than specified days.
    
    Args:
        days: Number of days to keep cache
        
    Returns:
        Number of files deleted
    """
    ensure_cache_dirs()
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = 0
    
    for cache_type in ['market_data', 'analysis']:
        cache_path = os.path.join(CACHE_DIR, cache_type)
        if os.path.exists(cache_path):
            for file in os.listdir(cache_path):
                file_path = os.path.join(cache_path, file)
                file_date = os.path.getmtime(file_path)
                file_datetime = datetime.fromtimestamp(file_date)
                
                if file_datetime < cutoff_date:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except Exception as e:
                        logger.error(f"Error deleting cache file {file}: {e}")
    
    if deleted_count > 0:
        logger.info(f"Cleared {deleted_count} old cache files")
    
    return deleted_count


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    ensure_cache_dirs()
    stats = {
        'market_data_files': 0,
        'analysis_files': 0,
        'cache_dir': CACHE_DIR,
        'total_size_mb': 0
    }
    
    for cache_type in ['market_data', 'analysis']:
        cache_path = os.path.join(CACHE_DIR, cache_type)
        if os.path.exists(cache_path):
            files = os.listdir(cache_path)
            stats[f"{cache_type}_files"] = len(files)
            
            for file in files:
                file_path = os.path.join(cache_path, file)
                stats['total_size_mb'] += os.path.getsize(file_path) / (1024 * 1024)
    
    stats['total_size_mb'] = round(stats['total_size_mb'], 2)
    return stats
