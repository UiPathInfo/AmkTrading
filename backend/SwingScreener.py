import pandas as pd
import yfinance as yf
import pandas_ta as ta
import numpy as np
import logging
from typing import List, Dict, Any, Optional
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration Constants ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, 'stock_list.ods')
TICKER_COLUMN = 'Ticker'


def get_tickers_from_excel(file_path: str, column_name: str) -> List[str]:
    """
    Reads stock tickers from a specified column in an ODS file.
    
    Args:
        file_path (str): The path to the ODS file.
        column_name (str): The name of the column containing the stock tickers.
        
    Returns:
        List[str]: A list of cleaned stock ticker symbols.
    """
    try:
        df = pd.read_excel(file_path, engine='odf')
        tickers = df[column_name].astype(str).str.strip().tolist()
        logging.info(f"Successfully read {len(tickers)} tickers from {file_path}")
        return tickers
    except FileNotFoundError:
        logging.error(f"The file '{file_path}' was not found.")
        return []
    except KeyError:
        logging.error(f"Column '{column_name}' not found in the ODS file.")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred while reading the ODS file: {e}")
        return []


def analyze_stock(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Analyzes a single stock for swing trading using TTM Squeeze, Volume Profile, and RSI.
    
    Args:
        ticker (str): Stock ticker symbol (without .NS suffix)
        
    Returns:
        Dict[str, Any]: Analysis results or None if data fetch fails
    """
    try:
        # Fetch 1 year of data for accurate analysis
        symbol = ticker + ".NS"
        data = yf.download(symbol, period="1y", interval="1d", progress=False)
        
        if data.empty:
            logging.warning(f"No data fetched for {ticker}")
            return None

        # --- 1. TTM SQUEEZE ---
        # Calculates Bollinger Bands vs Keltner Channels
        sqz = ta.squeeze(data['High'], data['Low'], data['Close'], lazybear=True)
        data = pd.concat([data, sqz], axis=1)
        
        # Logic: Red Dots = Squeeze ON (SQZ_ON == 1)
        current_sqz = "SQUEEZE ON (Red Dots)" if data['SQZ_ON'].iloc[-1] == 1 else "Normal (Green Dots)"
        mom_direction = "Bullish" if data['SQZ_20_2.0_20_1.5'].iloc[-1] > 0 else "Bearish"

        # --- 2. VOLUME PROFILE (POC - Point of Control) ---
        # Find the price level with max volume in the last 30 days
        recent_data = data.tail(30)
        price_bins = pd.cut(recent_data['Close'], bins=20)
        volume_profile = recent_data.groupby(price_bins)['Volume'].sum()
        poc_interval = volume_profile.idxmax()
        poc_price = (poc_interval.left + poc_interval.right) / 2

        # --- 3. RSI RANGE SHIFTS (Cardwell) ---
        data['RSI'] = ta.rsi(data['Close'], length=14)
        current_rsi = data['RSI'].iloc[-1]
        
        regime = "Sideways"
        if current_rsi > 40 and current_rsi <= 60:
            regime = "Bullish Regime (Support at 40)"
        elif current_rsi > 60:
            regime = "Strong Bullish"
        elif current_rsi < 40:
            regime = "Bearish Regime"

        # Get current price
        current_price = data['Close'].iloc[-1]

        return {
            "ticker": ticker,
            "current_price": round(float(current_price), 2),
            "squeeze_status": current_sqz,
            "momentum": mom_direction,
            "poc_support": round(float(poc_price), 2),
            "rsi": round(float(current_rsi), 2),
            "regime": regime,
            "status": "success"
        }

    except Exception as e:
        logging.error(f"ERROR analyzing {ticker}: {e}")
        return {
            "ticker": ticker,
            "status": "error",
            "error": str(e)
        }


def run_swing_screener(max_stocks: int = 10) -> List[Dict[str, Any]]:
    """
    Run swing trading analysis on stocks from the Excel file.
    
    Args:
        max_stocks (int): Maximum number of stocks to analyze (default 10)
        
    Returns:
        List[Dict[str, Any]]: List of analysis results for each stock
    """
    tickers = get_tickers_from_excel(EXCEL_FILE, TICKER_COLUMN)
    
    if not tickers:
        logging.error("No tickers found. Aborting swing screener.")
        return []
    
    # Limit to max_stocks for performance
    tickers = tickers[:max_stocks]
    
    logging.info(f"--- Starting Swing Trading Analysis for {len(tickers)} stocks ---")
    
    results = []
    for ticker in tickers:
        if not ticker or ticker.upper() == 'NAN':
            logging.debug(f"Skipping invalid ticker: {ticker}")
            continue
        
        logging.info(f"Analyzing {ticker}...")
        report = analyze_stock(ticker)
        if report:
            results.append(report)
    
    return results


if __name__ == "__main__":
    results = run_swing_screener(max_stocks=5)
    if results:
        results_df = pd.DataFrame(results)
        print("\n--- Swing Trade Candidates ---")
        print(results_df.to_string(index=False))
    else:
        logging.info("No results generated.")
