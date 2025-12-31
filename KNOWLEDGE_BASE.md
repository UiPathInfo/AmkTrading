# AMK Trading - Complete Knowledge Base

## Project Overview
AMK Trading is a fullstack web application for Indian stock market swing trading analysis. It combines fundamental stock screening with technical analysis to identify trading opportunities.

**Architecture:** Python FastAPI Backend + React + Vite Frontend
**Data Source:** Yahoo Finance via yfinance
**Market:** NSE (National Stock Exchange) - Indian stocks
**Deployment:** Docker-ready, can be deployed on any Linux server

---

## 📁 Project Structure

```
AmkTrading/
├── backend/
│   ├── main.py                 # FastAPI application & API endpoints
│   ├── MyScreener.py           # Fundamental stock screening logic
│   ├── SwingScreener.py        # Swing trading technical analysis
│   ├── requirements.txt        # Python dependencies
│   ├── stock_list.ods          # Excel file with stock tickers (data source)
│   └── screener_results.ods    # Output file with results
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React component with all UI logic
│   │   ├── main.jsx            # React entry point
│   │   └── styles.css          # CSS styling
│   ├── index.html              # HTML template
│   ├── package.json            # Node.js dependencies
│   └── dist/                   # Built production files
├── .venv/                      # Python virtual environment
└── readme.md                   # Project documentation
```

---

## 🔧 Backend Implementation

### Dependencies (requirements.txt)
```
fastapi>=0.95.0          # Web framework
uvicorn[standard]>=0.20.0 # ASGI server
pydantic>=1.10.0         # Data validation
pandas                   # Data manipulation
yfinance                 # Yahoo Finance API
odfpy                    # Read .ods files
pandas_ta                # Technical analysis indicators
```

### Main Application (main.py)

#### Application Initialization
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AMK Trading API")

# CORS Configuration - allows requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Dynamic Module Loading
Two screener modules are dynamically loaded:
1. **`_load_run_screener()`** - Loads MyScreener.py module
2. **`_load_run_swing_screener()`** - Loads SwingScreener.py module

This approach tries 3 methods:
- Package import (backend.MyScreener)
- Top-level import (MyScreener)
- Direct file path import using importlib

---

### API Endpoints

#### 1. Health Check Endpoint
```
GET /api/health
Response: {"status": "ok"}
Purpose: Check if API is running
```

#### 2. Items Management Endpoints (Sample CRUD operations)
```
GET /api/items
Returns: List of all items
Response: [{"id": 1, "name": "Sample Item", "description": "..."}]

POST /api/items
Body: {"name": "Item Name", "description": "Item Description"}
Returns: {"id": 2, "name": "Item Name", "description": "Item Description"}
Status Code: 201 (Created)
```

#### 3. Fundamental Stock Screener Endpoint
```
GET /api/screener

Purpose: Filters stocks based on fundamental criteria
Response: {
    "count": 5,
    "results": [
        {
            "ticker": "RELIANCE",
            "mkt_cap": "15,00,000.00",
            "de_ratio": "0.50",
            "roe": "25.50",
            "pe": "22.30"
        },
        ...
    ]
}

Filters Applied:
- Market Cap ≥ ₹10,000 Cr
- Debt-to-Equity ≤ 1.0
- ROE ≥ 15%
- Forward P/E ≤ 30
```

#### 4. Swing Trading Screener Endpoint
```
GET /api/swing-screener?limit=10

Query Parameters:
- limit (int, optional): Max number of stocks to analyze (1-50, default 10)

Purpose: Performs technical analysis on stocks for swing trading opportunities

Response: {
    "total_analyzed": 10,
    "successful": 8,
    "failed": 2,
    "results": [
        {
            "ticker": "RELIANCE",
            "current_price": 2850.50,
            "squeeze_status": "SQUEEZE ON (Red Dots)",
            "momentum": "Bullish",
            "poc_support": 2800.00,
            "rsi": 65.50,
            "regime": "Strong Bullish",
            "status": "success"
        },
        ...
    ]
}
```

---

### MyScreener.py - Fundamental Stock Screener

#### Configuration Constants
```python
EXCEL_FILE = 'stock_list.ods'      # Excel file with tickers
TICKER_COLUMN = 'Ticker'            # Column name in Excel

# Screening Thresholds
MIN_MARKET_CAP_CR = 10000.0         # Minimum ₹10,000 Crores
MAX_DEBT_TO_EQUITY = 1.0            # Maximum D/E ratio
MIN_ROE = 0.15                      # Minimum 15% ROE
MAX_FORWARD_PE = 30.0               # Maximum P/E ratio

# Conversion Factors
CRORE_CONVERSION_FACTOR = 10**7     # Convert rupees to crores
PERCENTAGE_TO_DECIMAL_FACTOR = 100.0 # Convert % to decimal
```

#### Key Functions

**1. `get_tickers_from_excel(file_path, column_name)`**
- Reads stock tickers from .ods file
- Uses pandas with 'odf' engine
- Cleans whitespace with .str.strip()
- Error handling for missing files/columns
- Returns: List[str] of ticker symbols

**2. `screen_stocks(tickers)`**
- Main screening logic
- For each ticker:
  - Fetches data via yfinance (ticker + ".NS" for NSE)
  - Extracts fundamental metrics from ticker.info
  - Applies 4 filters in sequence
  - Returns: List of passed stocks with metrics

**3. `run_screener()`**
- Entry point for API
- Calls get_tickers_from_excel()
- Calls screen_stocks()
- Returns filtered results

#### Data Flow
```
Excel File (stock_list.ods)
    ↓
get_tickers_from_excel() → List of tickers
    ↓
For each ticker:
    ↓
yf.Ticker(ticker + ".NS") → Fetch fundamental data
    ↓
Apply Filters:
    1. Market Cap Check
    2. D/E Ratio Check
    3. ROE Check
    4. Forward P/E Check
    ↓
If Pass → Add to results
    ↓
Return results array
```

#### Excel File Format (stock_list.ods)
Required columns:
- **Ticker**: Stock symbol (e.g., "RELIANCE", "TCS", "INFY")

Optional columns for manual data entry (when avoiding yfinance rate limits):
- **marketCap**: Value in Rupees (e.g., 150000000000000 for ₹15 Lakh Crore)
- **debtToEquity**: Percentage value (e.g., 50 for 50%)
- **returnOnEquity**: Decimal format (e.g., 0.25 for 25%)
- **forwardPE**: Decimal format (e.g., 22.5)

---

### SwingScreener.py - Technical Analysis for Swing Trading

#### Configuration
```python
EXCEL_FILE = 'stock_list.ods'
TICKER_COLUMN = 'Ticker'
```

#### Key Functions

**1. `get_tickers_from_excel(file_path, column_name)`**
- Same as MyScreener
- Reads tickers from Excel file

**2. `analyze_stock(ticker)`**
- Comprehensive technical analysis for single stock
- Fetches 1 year of historical data from yfinance
- Performs 3 main analyses:

**Analysis 1: TTM Squeeze Indicator**
```python
# TTM Squeeze = Bollinger Bands vs Keltner Channels
sqz = ta.squeeze(data['High'], data['Low'], data['Close'], lazybear=True)

# Returns:
- SQZ_ON: 1 if squeeze is ON (Red Dots), 0 if OFF (Green Dots)
- SQZ_20_2.0_20_1.5: Momentum histogram (positive=Bullish, negative=Bearish)

Interpretation:
- Red Dots = Low volatility squeeze (breakout likely coming)
- Green Dots = Normal volatility range
- Momentum shows direction of breakout
```

**Analysis 2: Volume Profile (Point of Control)**
```python
# Find support level using volume concentration
recent_data = data.tail(30)  # Last 30 days
price_bins = pd.cut(recent_data['Close'], bins=20)  # 20 price bins
volume_profile = recent_data.groupby(price_bins)['Volume'].sum()
poc_interval = volume_profile.idxmax()  # Highest volume bin
poc_price = (poc_interval.left + poc_interval.right) / 2

Purpose: Identifies support level where volume concentrates
```

**Analysis 3: RSI (Relative Strength Index)**
```python
data['RSI'] = ta.rsi(data['Close'], length=14)

RSI Interpretation:
- RSI < 40: Bearish Regime (downtrend)
- 40 ≤ RSI ≤ 60: Bullish Regime - Support at 40 (uptrend with consolidation)
- RSI > 60: Strong Bullish (strong uptrend)
```

**3. `run_swing_screener(max_stocks=10)`**
- Reads tickers from Excel
- Analyzes each stock sequentially
- Returns results with success/error status

#### Return Value Format
```python
{
    "ticker": "RELIANCE",
    "current_price": 2850.50,
    "squeeze_status": "SQUEEZE ON (Red Dots)",
    "momentum": "Bullish",
    "poc_support": 2800.00,
    "rsi": 65.50,
    "regime": "Strong Bullish",
    "status": "success"  # or "error"
}
```

#### Data Flow
```
Excel File → Get Tickers
    ↓
For each ticker (max `max_stocks`):
    ↓
Fetch 1 year data via yfinance (ticker.NS)
    ↓
1. Calculate TTM Squeeze
2. Calculate Volume Profile
3. Calculate RSI
    ↓
Determine Trading Regime
    ↓
Return Analysis Results
```

---

## 🎨 Frontend Implementation

### Tech Stack
- **Framework**: React 18.2.0
- **Build Tool**: Vite 5.0.0
- **HTTP Client**: Axios 1.4.0
- **UI Framework**: Bootstrap (via CDN)
- **Plugin**: @vitejs/plugin-react

### File Structure
- **src/App.jsx**: Main React component (all logic & UI)
- **src/main.jsx**: React entry point
- **src/styles.css**: Custom styling
- **index.html**: HTML template with Bootstrap CDN
- **vite.config.js**: Vite configuration

### App.jsx - Main Component Structure

#### Imports & Constants
```jsx
import React, { useEffect, useState } from 'react'
import axios from 'axios'

// API base URL from environment or localhost
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
```

#### State Management
```jsx
// Items Management
const [items, setItems] = useState([])                  // List of items
const [name, setName] = useState('')                    // Item name input
const [desc, setDesc] = useState('')                    // Item description input

// Fundamental Screener State
const [screenerResults, setScreenerResults] = useState(null)
const [screenerLoading, setScreenerLoading] = useState(false)
const [screenerError, setScreenerError] = useState(null)

// Swing Trading Screener State
const [swingResults, setSwingResults] = useState(null)
const [swingLoading, setSwingLoading] = useState(false)
const [swingError, setSwingError] = useState(null)
const [swingLimit, setSwingLimit] = useState(10)        // Max stocks to analyze
```

#### Key Functions

**1. `fetchItems()`**
```jsx
// Called on component mount
// Fetches list of items from /api/items
// Updates items state
// Error handling: logs to console
```

**2. `addItem(e)`**
```jsx
// Form submission handler
// Makes POST request to /api/items
// Body: { name, description: desc }
// Updates items state with new item
// Clears form inputs
// Error handling: logs to console
```

**3. `fetchScreener()`**
```jsx
// GET /api/screener
// Sets loading state while fetching
// Updates screenerResults state
// Handles errors in screenerError state
// Finally block sets loading to false
```

**4. `fetchSwingScreener()`**
```jsx
// GET /api/swing-screener?limit={swingLimit}
// Same loading/error/finally pattern as fetchScreener()
// Query parameter allows user to control number of stocks analyzed
// Updates swingResults state
```

#### UI Structure

**Main Container**
```jsx
<div className="container py-4">
  <div className="row">
    <div className="col-12 col-md-8 mx-auto">
      {/* Content */}
    </div>
  </div>
</div>
```

**Section 1: Fundamental Stock Screener**
- Button: "Run Fundamental Screener" (green/success)
- Shows loading state: "Loading Screener..."
- Displays results count and stock details
- Error display: Red alert with error message
- Results: JSON formatted in scrollable box

**Section 2: Swing Trading Screener**
- Input: Number input for max stocks to analyze (1-50)
- Button: "Run Swing Screener" (yellow/warning)
- Shows loading state: "Analyzing..."
- Displays statistics:
  - Total Analyzed
  - Successful
  - Failed
- Results table with columns:
  - Ticker
  - Current Price
  - Squeeze Status
  - Momentum (Bullish/Bearish)
  - POC (Point of Control)
  - RSI
  - Trading Regime
- Error handling: Red alert

**Section 3: Items Management**
- Form with inputs:
  - Name (required)
  - Description (optional)
- Submit button: "Add Item"
- List of items displayed as list-group with:
  - Item name (bold)
  - Description (muted)
  - Item ID badge

#### Styling & Responsive Design
- **Bootstrap Classes Used:**
  - Container & Grid: `container`, `row`, `col-12`, `col-md-8`, `mx-auto`
  - Spacing: `py-4`, `mb-3`, `mb-4`, `p-2`
  - Colors: `alert-success`, `alert-danger`, `alert-info`, `alert-warning`
  - Buttons: `btn`, `btn-success`, `btn-warning`, `btn-primary`
  - Forms: `form-label`, `form-control`, `input-group`
  - Tables: `table`, `table-sm`, `table-responsive`
  - Typography: `fw-bold`, `text-muted`, `small`
  - Badges: `badge`, `bg-secondary`, `rounded-pill`

---

## 🚀 Deployment Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- pip and npm

### Local Development Setup

**Backend Setup**
```bash
# Navigate to backend
cd backend

# Create Python virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python3 main.py
# Or with auto-reload:
uvicorn main:app --reload --port 8000
```

**Frontend Setup**
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server (Vite)
npm run dev
# Frontend runs on http://localhost:5173

# Build for production
npm run build
# Output: frontend/dist/
```

### Production Deployment

**Backend - Production**
```bash
# Install gunicorn for production ASGI server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000

# Options:
# -w 4: 4 worker processes
# --bind 0.0.0.0:8000: Listen on all interfaces, port 8000
```

**Frontend - Production**
```bash
# Build production files
npm run build

# Outputs to 'dist/' folder
# Serve with nginx or any static server:
# - Point nginx to dist/ folder
# - Set environment variable for API base URL
```

### Environment Variables

**Frontend (.env or .env.production)**
```
VITE_API_BASE=http://your-backend-url:8000
```

**Backend**
- No special environment variables needed
- All configuration in main.py (can be moved to .env)

---

## 📊 Data Files

### stock_list.ods (Input)
Excel file with NSE stock tickers to screen
- **Column Name**: "Ticker"
- **Format**: One ticker per row
- **Example**: RELIANCE, TCS, INFY, HDFC, ICICIBANK

### screener_results.ods (Output)
Optional output file where results can be exported

---

## 🔄 API Communication Flow

### Fundamental Screener Flow
```
User clicks "Run Fundamental Screener"
    ↓
fetchScreener() function triggered
    ↓
setScreenerLoading(true) - Show loading state
    ↓
axios.get('/api/screener')
    ↓
Backend: get_screener() endpoint
    ↓
Backend: MyScreener.run_screener()
    ↓
Read stock_list.ods tickers
    ↓
For each ticker: Fetch yfinance data
    ↓
Apply 4 filters (Market Cap, D/E, ROE, P/E)
    ↓
Return filtered results
    ↓
Frontend: setScreenerResults(data)
    ↓
Display results in UI
```

### Swing Screener Flow
```
User enters max stocks (default 10)
    ↓
User clicks "Run Swing Screener"
    ↓
fetchSwingScreener() function triggered
    ↓
setSwingLoading(true) - Show loading state
    ↓
axios.get('/api/swing-screener?limit=10')
    ↓
Backend: get_swing_screener(limit=10) endpoint
    ↓
Backend: SwingScreener.run_swing_screener(max_stocks=10)
    ↓
Read stock_list.ods tickers (limit 10)
    ↓
For each ticker: analyze_stock(ticker)
    ↓
    - Fetch 1 year data from yfinance
    - Calculate TTM Squeeze
    - Calculate Volume Profile
    - Calculate RSI
    - Determine trading regime
    ↓
Return analysis results with status
    ↓
Frontend: setSwingResults(data)
    ↓
Display results in table format
```

---

## 🛠️ How to Recreate This Project

### Step 1: Project Setup
```bash
mkdir AmkTrading
cd AmkTrading
python3 -m venv .venv
source .venv/bin/activate
```

### Step 2: Backend Setup
```bash
mkdir backend
cd backend
pip install fastapi uvicorn pandas yfinance odfpy pandas_ta pydantic

# Create requirements.txt with all dependencies
```

### Step 3: Create Backend Files

**main.py**
- Copy entire FastAPI app setup
- Implement dynamic module loading for MyScreener and SwingScreener
- Create all 4 API endpoints (health, items, screener, swing-screener)
- Add CORS middleware

**MyScreener.py**
- Implement get_tickers_from_excel()
- Implement screen_stocks() with 4 filters
- Implement run_screener()
- Set thresholds (market cap, D/E, ROE, P/E)

**SwingScreener.py**
- Implement get_tickers_from_excel()
- Implement analyze_stock() with 3 analyses:
  - TTM Squeeze
  - Volume Profile
  - RSI
- Implement run_swing_screener()

**stock_list.ods**
- Create Excel file with "Ticker" column
- Add NSE stock symbols

### Step 4: Frontend Setup
```bash
cd ../frontend
npm create vite@latest . -- --template react
npm install axios

# Or if using React 18 directly:
npm install react react-dom axios
npm install -D vite @vitejs/plugin-react
```

### Step 5: Create Frontend Files

**index.html**
- Include Bootstrap 5 CDN
- Include main.jsx script
- Basic HTML structure

**src/main.jsx**
- React 18 createRoot setup
- Mount App component

**src/App.jsx**
- Copy entire component
- All state management
- All functions
- Complete UI structure

**src/styles.css**
- Any custom styling (optional, Bootstrap covers most)

**package.json scripts**
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

### Step 6: Run and Test
```bash
# Terminal 1 - Backend
cd backend
python3 main.py

# Terminal 2 - Frontend
cd frontend
npm run dev

# Visit http://localhost:5173
```

---

## 🐛 Troubleshooting

### Backend Issues

**"Screener not available" error**
- Check if stock_list.ods exists in backend folder
- Verify "Ticker" column exists in Excel file
- Check if MyScreener.py is in correct path

**"odfpy library required" error**
- Run: `pip install odfpy`

**"Module not found" for pandas_ta**
- Run: `pip install pandas_ta`

**yfinance rate limit issues**
- yfinance has rate limiting (default ~2000 requests/hour)
- Solution: Manually populate Excel with fundamental data
- Or: Add delays between requests with time.sleep()

### Frontend Issues

**CORS errors**
- Backend CORS middleware is configured for all origins (*)
- If still failing, check API_BASE URL in App.jsx
- Ensure backend is running before frontend

**Blank page after build**
- Check that API_BASE environment variable is set
- Verify dist/ folder was created by `npm run build`
- Check browser console for errors

---

## 📈 Performance Optimization

### Backend
- Add caching for yfinance data (avoid repeated API calls)
- Implement batch processing for multiple stocks
- Add request timeout handling

### Frontend
- Implement result pagination for large datasets
- Add loading skeletons instead of plain text
- Cache results locally in localStorage

---

## 🔐 Security Considerations

### Current State (Development)
- CORS allows all origins (not for production)
- No authentication implemented
- API is public

### For Production
- Implement API key authentication
- Restrict CORS to specific origins
- Add rate limiting
- Use HTTPS
- Validate all user inputs
- Add logging and monitoring

---

## 📝 Summary

This project demonstrates a complete fullstack trading analysis application:

**Backend (Python FastAPI)**
- Two independent screeners (Fundamental & Swing)
- Dynamic module loading for flexibility
- Integration with yfinance for market data
- Excel file integration for stock lists

**Frontend (React + Vite)**
- Two separate analysis interfaces
- Real-time API communication
- Responsive Bootstrap UI
- State management with React hooks

**Data Flow**
- User inputs → API Request → Backend Processing → Results Display

**Deployment Ready**
- Can be Dockerized
- Scalable with gunicorn
- Frontend optimized with Vite
- Ready for production deployment

---

## 📚 Additional Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- React Documentation: https://react.dev/
- Vite Documentation: https://vitejs.dev/
- yfinance Documentation: https://github.com/ranaroussi/yfinance
- pandas_ta Documentation: https://github.com/twopirllc/pandas-ta
- Bootstrap Documentation: https://getbootstrap.com/

---

**Last Updated**: 30 December 2025
**Version**: 1.0
