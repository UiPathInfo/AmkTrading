"""
Enhanced SwingScreener with comprehensive technical analysis and ML conviction scoring
Includes data caching to avoid yfinance rate limits
"""
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import numpy as np
import logging
from typing import List, Dict, Any, Optional
import os

from config import SCREENING_PARAMS, get_config
from indicators import (
    calculate_ttm_squeeze, calculate_volume_profile, calculate_momentum_indicators,
    calculate_trend_analysis, calculate_delivery_metrics, calculate_relative_strength,
    generate_analysis_report
)
from conviction_engine import ConvictionScorer
from cache_manager import (
    load_market_data_cache, save_market_data_cache,
    load_analysis_cache, save_analysis_cache
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, 'stock_list.ods')
TICKER_COLUMN = 'Ticker'


def get_tickers_from_excel(file_path: str, column_name: str) -> List[str]:
    """Read stock tickers from ODS file."""
    try:
        df = pd.read_excel(file_path, engine='odf')
        tickers = df[column_name].astype(str).str.strip().tolist()
        logger.info(f"Read {len(tickers)} tickers from {file_path}")
        return tickers
    except Exception as e:
        logger.error(f"Error reading ODS file: {e}")
        return []


def check_screening_criteria(ticker: str, data: pd.DataFrame, config: Dict[str, Any]) -> bool:
    """
    Check if stock meets minimum screening criteria:
    - Daily volume > 500k
    - ATR 2-5%
    - Market cap check (if available)
    """
    params = config['screening']
    
    # Check volume
    avg_volume = data['Volume'].tail(20).mean()
    if avg_volume < params['min_daily_volume']:
        logger.debug(f"{ticker}: Volume {avg_volume:.0f} below threshold")
        return False
    
    # Check ATR
    atr_pct = (data['ATR'].iloc[-1] / data['Close'].iloc[-1]) * 100
    if atr_pct < params['atr_min_pct'] or atr_pct > params['atr_max_pct']:
        logger.debug(f"{ticker}: ATR {atr_pct:.2f}% outside range")
        return False
    
    logger.debug(f"{ticker}: Passed screening criteria")
    return True


def analyze_stock(ticker: str, config: Dict[str, Any], 
                  conviction_scorer: Optional[ConvictionScorer] = None,
                  use_cache: bool = True) -> Optional[Dict[str, Any]]:
    """
    Comprehensive technical and ML analysis for a stock.
    
    Args:
        ticker: Stock ticker without .NS suffix
        config: Configuration dictionary
        conviction_scorer: Optional ML conviction scorer
        use_cache: Whether to use cached data if available
        
    Returns:
        Analysis result dictionary or None if failed
    """
    try:
        # Check cache first
        if use_cache:
            cached_analysis = load_analysis_cache(ticker)
            if cached_analysis:
                logger.info(f"Using cached analysis for {ticker}")
                return cached_analysis
        
        # Try to load cached market data first
        data = None
        if use_cache:
            data = load_market_data_cache(ticker)
            if data is not None:
                logger.info(f"Using cached market data for {ticker}")
        
        # Fetch from yfinance if not in cache
        if data is None:
            symbol = f"{ticker}.NS"
            data = yf.download(symbol, period=config['screening']['data_period'], 
                              interval=config['screening']['data_interval'], progress=False)
            
            if data.empty or len(data) < 50:
                logger.warning(f"{ticker}: Insufficient data")
                return None
            
            # Save to cache
            if use_cache:
                save_market_data_cache(ticker, data)
        
        # Check screening criteria
        if not check_screening_criteria(ticker, data, config):
            return None
        
        # Calculate technical indicators
        data = calculate_ttm_squeeze(data, config)
        data = calculate_momentum_indicators(data, config)
        data = calculate_trend_analysis(data, config)
        
        # Volume profile analysis
        volume_profile = calculate_volume_profile(data, config)
        
        # Relative strength (vs Nifty 50) - also use cache
        nifty_data = None
        if use_cache:
            nifty_data = load_market_data_cache("NIFTY50")
        
        if nifty_data is None:
            nifty_data = yf.download("^NSEI", period=config['screening']['data_period'],
                                    interval=config['screening']['data_interval'], progress=False)
            if not nifty_data.empty and use_cache:
                save_market_data_cache("NIFTY50", nifty_data)
        
        relative_strength = calculate_relative_strength(data, nifty_data) if not nifty_data.empty else {}
        
        # Prepare technical analysis report
        momentum = {
            "rsi": float(data['RSI'].iloc[-1]) if 'RSI' in data.columns else 50,
            "macd_hist": float(data['MACD_Hist'].iloc[-1]) if 'MACD_Hist' in data.columns else 0,
            "rsi_divergence": str(data['RSI_Div'].iloc[-1]) if 'RSI_Div' in data.columns else 'None',
        }
        
        technical_analysis = generate_analysis_report(
            ticker, data, config, volume_profile, momentum, relative_strength
        )
        
        # Calculate ML conviction score (if scorer available)
        conviction_data = {}
        if conviction_scorer:
            conviction_data = conviction_scorer.calculate_score(data, technical_analysis)
        else:
            # Fallback to simple rule-based score
            confluence = technical_analysis['confluence']['total_confluent_factors']
            base_score = (confluence / 3.0) * 0.5  # 0 to 0.5 from confluence
            conviction_data = {
                "ml_score": 0.5,
                "technical_score": min(0.95, base_score + 0.4),
                "conviction_score": min(0.95, base_score + 0.4),
                "recommendation": "Buy" if base_score > 0.33 else "Hold",
                "confidence_level": "High" if base_score > 0.33 else "Medium",
            }
        
        result = {
            "ticker": ticker,
            "status": "success",
            "timestamp": str(data.index[-1]),
            "price": {
                "current": float(data['Close'].iloc[-1]),
                "change_pct": float((data['Close'].iloc[-1] - data['Close'].iloc[-20]) / data['Close'].iloc[-20] * 100),
            },
            "technical_analysis": technical_analysis,
            "conviction": conviction_data,
            "screening_metrics": {
                "avg_volume": float(data['Volume'].tail(20).mean()),
                "atr_pct": float(data['ATR_Pct'].iloc[-1]) if 'ATR_Pct' in data.columns else 0,
                "delivery_pct": float(data['Delivery_Pct'].iloc[-1]) if 'Delivery_Pct' in data.columns else 0,
            }
        }
        
        # Cache the analysis result
        if use_cache:
            save_analysis_cache(ticker, result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}")
        return {
            "ticker": ticker,
            "status": "error",
            "error": str(e)
        }


def run_swing_screener(max_stocks: int = 10, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Run comprehensive swing trading screener.
    
    Args:
        max_stocks: Maximum number of stocks to analyze
        config: Configuration dictionary (uses defaults if None)
        
    Returns:
        List of analysis results for each stock
    """
    if config is None:
        config = get_config()
    
    tickers = get_tickers_from_excel(EXCEL_FILE, TICKER_COLUMN)
    
    if not tickers:
        logger.error("No tickers found")
        return []
    
    # Limit to max_stocks for performance
    tickers = tickers[:max_stocks]
    
    logger.info(f"Starting swing screener analysis for {len(tickers)} stocks")
    
    # Initialize ML conviction scorer
    conviction_scorer = ConvictionScorer(config)
    # Note: Model training would require historical data - skipping for now
    
    results = []
    for ticker in tickers:
        if not ticker or ticker.upper() == 'NAN':
            logger.debug(f"Skipping invalid ticker: {ticker}")
            continue
        
        logger.info(f"Analyzing {ticker}...")
        report = analyze_stock(ticker, config, conviction_scorer)
        if report:
            results.append(report)
    
    # Sort by conviction score
    successful = [r for r in results if r.get('status') == 'success']
    successful.sort(key=lambda x: x.get('conviction', {}).get('conviction_score', 0), reverse=True)
    
    logger.info(f"Screener complete: {len(successful)} successful, {len(results) - len(successful)} failed")
    
    return successful + [r for r in results if r.get('status') != 'success']


if __name__ == "__main__":
    config = get_config()
    results = run_swing_screener(max_stocks=5, config=config)
    
    for result in results:
        if result.get('status') == 'success':
            print(f"\n{result['ticker']}: Conviction {result['conviction']['conviction_score']:.2f}")
            print(f"  Price: {result['price']['current']}")
            print(f"  Grade: {result['technical_analysis']['confluence']['grade']}")
