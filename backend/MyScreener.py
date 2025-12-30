import yfinance as yf
import pandas as pd
import logging
from typing import List, Dict, Any
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration Constants ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, 'stock_list.ods') # <--- Updated file extension with absolute path
TICKER_COLUMN = 'Ticker' # Must match the column header in your ODS file

# Define conversion constants
CRORE_CONVERSION_FACTOR = 10**7
PERCENTAGE_TO_DECIMAL_FACTOR = 100.0

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
        # Read the ODS file using the 'odf' engine
        df = pd.read_excel(file_path, engine='odf') 
        
        # Extract the list of tickers from the specified column
        # .str.strip() is used to remove any accidental whitespace
        tickers = df[column_name].astype(str).str.strip().tolist()
        
        logging.info(f"Successfully read {len(tickers)} tickers from {file_path}")
        return tickers
    except FileNotFoundError:
        logging.error(f"The file '{file_path}' was not found. Please ensure it is in the same folder as the script.")
        return []
    except KeyError:
        logging.error(f"Column '{column_name}' not found in the ODS file. Check that the header is exactly '{column_name}'.")
        return []
    except ImportError:
        logging.error("The 'odfpy' library is required to read .ods files.")
        logging.info("Please run: pip install odfpy")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred while reading the ODS file: {e}")
        return []

# --- 2. Define the screening criteria (Thresholds) ---
MIN_MARKET_CAP_CR = 10000.0  # Min Market Cap in Crores
MAX_DEBT_TO_EQUITY = 1.0     # Max Debt to Equity Ratio
MIN_ROE = 0.15               # Min Return on Equity (15%)
MAX_FORWARD_PE = 30.0        # Max Forward P/E Ratio

def screen_stocks(tickers: List[str]) -> List[Dict[str, Any]]:
    """
    Screens a list of stock tickers based on predefined fundamental criteria.
    
    Args:
        tickers (List[str]): A list of stock ticker symbols to screen.
        
    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                                represents a stock that passed the screening
                                and contains its relevant metrics.
    """
    passed_stocks: List[Dict[str, Any]] = []
    
    logging.info("--- Starting Fundamental Stock Screening ---")
    
    for ticker_symbol in tickers:
        # Skip empty or 'nan' entries from the ODS file
        if not ticker_symbol or ticker_symbol.upper() == 'NAN':
            logging.debug(f"Skipping invalid ticker entry: '{ticker_symbol}'")
            continue
            
        try:
            # Fetch data for the ticker
            ticker = yf.Ticker(ticker_symbol)
            data = ticker.info

            # --- Data Extraction and Cleanup ---
            # yfinance often gives Market Cap in raw currency value (Rupees)
            market_cap_in_crores = data.get('marketCap', 0) / CRORE_CONVERSION_FACTOR
            
            # Fundamental Ratios (Note: These keys might sometimes be missing or None)
            # Assuming debtToEquity from yfinance is a percentage, converting to decimal
            debt_to_equity = data.get('debtToEquity', float('inf')) / PERCENTAGE_TO_DECIMAL_FACTOR if data.get('debtToEquity') is not None else float('inf')
            roe = data.get('returnOnEquity', 0.0)
            forward_pe = data.get('forwardPE', float('inf'))

            # --- Screening Logic ---
            # Market Cap Filter
            if market_cap_in_crores < MIN_MARKET_CAP_CR:
                logging.debug(f"{ticker_symbol}: Failed Market Cap ({market_cap_in_crores:.2f} Cr)")
                continue
            
            # Debt-to-Equity Filter
            if debt_to_equity > MAX_DEBT_TO_EQUITY:
                logging.debug(f"{ticker_symbol}: Failed D/E Ratio ({debt_to_equity:.2f})")
                continue

            # ROE Filter
            if roe < MIN_ROE:
                logging.debug(f"{ticker_symbol}: Failed ROE ({roe*100:.2f}%)")
                continue

            # Forward P/E Filter
            if forward_pe > MAX_FORWARD_PE:
                logging.debug(f"{ticker_symbol}: Failed Fwd P/E ({forward_pe:.2f})")
                continue

            # If all checks pass
            passed_stocks.append({
                "ticker": ticker_symbol,
                "mkt_cap": f"{market_cap_in_crores:,.2f}",
                "de_ratio": f"{debt_to_equity:.2f}",
                "roe": f"{roe*100:.2f}",
                "pe": f"{forward_pe:.2f}",
            })
            logging.info(f"{ticker_symbol}: Passed all criteria.")
            
        except Exception as e:
            logging.error(f"ERROR fetching data for {ticker_symbol}: {e}")
            continue
    return passed_stocks

def run_screener():
    """Helper function to run the full screening process."""
    tickers = get_tickers_from_excel(EXCEL_FILE, TICKER_COLUMN)
    if not tickers:
        return []
    return screen_stocks(tickers)

if __name__ == "__main__":
    # 1. Get the list of stock tickers from the Excel file
    STOCK_TICKERS = get_tickers_from_excel(EXCEL_FILE, TICKER_COLUMN)

    # Check if any tickers were loaded before proceeding
    if not STOCK_TICKERS:
        logging.info("Screening aborted due to errors or empty ticker list.")
    else:
        # --- 3. Iterate through each stock, fetch data, and apply filters ---
        passed_stocks = screen_stocks(STOCK_TICKERS)

        # 4. Print the final results
        print("\n" + "="*50)
        print("✅ Fundamentally Strong Stocks (Screening Results)")
        print("="*50)

        if passed_stocks:
            # Use pandas to display results nicely
            results_df = pd.DataFrame(passed_stocks)
            print(results_df.to_string(index=False))
        else:
            logging.info("No stocks matched all the specified fundamental criteria.")

# --- End of Code ---