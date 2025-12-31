# AMK Trading Platform - Advanced Indian Equity Swing Trading System

**Version 2.0** | Production-Grade Quantitative Trading Ecosystem

## 🎯 Platform Overview

AMK Trading is a comprehensive swing trading platform designed for the Indian equity market (NSE/BSE). It combines technical analysis, machine learning, and quantitative journaling to identify high-probability trading setups and track performance systematically.

**Key Capabilities:**
- **Advanced Technical Analysis**: TTM Squeeze Pro, Volume Profile, Momentum Analysis
- **ML-Based Conviction Scoring**: XGBoost/Random Forest prediction engine
- **Comprehensive Trading Journal**: JSON-based trade logging with full P&L tracking
- **Performance Analytics**: Win rate, profit factor, expectancy, drawdown analysis
- **Mobile-First UI**: Fully responsive design for trading on mobile devices

---

## 📋 System Architecture

```
AmkTrading/
├── backend/                    # Python FastAPI backend
│   ├── main.py                # Enhanced API with journal & metrics endpoints
│   ├── config.py              # Platform configuration & parameters
│   ├── indicators.py          # Advanced technical indicators library
│   ├── conviction_engine.py   # ML-based conviction scoring
│   ├── journal.py             # Trading journal & performance metrics
│   ├── SwingScreener.py       # Enhanced swing trading screener
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx            # Main mobile-first UI component
│   │   ├── main.jsx           # React entry point
│   │   └── styles.css         # Responsive styling
│   ├── package.json           # NPM dependencies
│   └── index.html             # HTML template
│
└── README.md & KNOWLEDGE_BASE.md
```

---

## 🚀 Quick Start Guide

### Backend Setup

1. **Create Python Virtual Environment:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create Configuration File (Optional):**
   ```bash
   cp .env.example .env
   ```

4. **Run Backend Server:**
   ```bash
   python main.py
   ```
   Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Install Node Dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Development Server:**
   ```bash
   npm run dev
   ```
   Frontend will be available at `http://localhost:5173`

3. **Build for Production:**
   ```bash
   npm run build
   ```

---

## 📊 Technical Analysis Framework

### 1. TTM Squeeze Pro (3-Level Compression)

Detects volatility compression for explosive breakout identification.

**Compression Levels:**
- **RED** (High): Bollinger Bands inside 1.0 ATR - Maximum compression
- **ORANGE** (Mid): Bollinger Bands inside 1.5 ATR - Moderate compression
- **GRAY** (Low): Bollinger Bands inside 2.0 ATR - Minimal compression

**Formula:**
```
Squeeze_On = (LowerBB > LowerKC) ∧ (UpperBB < UpperKC)
UpperBB = SMA(20) + (2 × σ)
UpperKC = SMA(20) + (1.5 × ATR)
```

### 2. Volume Profile & Auction Market Theory

Maps volume at price levels to identify support/resistance and fair value.

**Key Levels:**
- **POC (Point of Control)**: Price level with highest traded volume - acts as magnet
- **VAH (Value Area High)**: Upper bound of 70% volume
- **VAL (Value Area Low)**: Lower bound of 70% volume
- **HVN (High Volume Node)**: Support/resistance consolidation zones
- **LVN (Low Volume Node)**: Low friction areas for rapid price movement

**80% Rule**: If price enters VAL and holds for 2 consecutive 30-min bars, 80% probability of traversing entire value area.

### 3. Momentum & Trend Confluence

**Indicators:**
- **200 EMA**: Institutional guardrail - buy signals only above this line
- **RSI (14)**: Overbought (>70) / Oversold (<30) with divergence detection
- **MACD**: Moving average convergence/divergence with histogram slope
- **Trend Regime**: Bullish / Bearish / Sideways based on price position

**Divergence Signals:**
- **Bullish Divergence**: Price lower low, RSI higher low → Reversal imminent
- **Hidden Bullish Divergence**: Price higher low, RSI lower low → Strong continuation

---

## 🤖 Machine Learning Conviction Engine

### Feature Engineering

**Price-Based:**
- Daily returns, distance from 200 EMA, ATR percentage
- Return momentum (5-day MA)

**Volume-Based:**
- Volume/MA ratio, On-Balance Volume (OBV)
- Chaikin Money Flow (CMF), Delivery % change

**Volatility State:**
- TTM Squeeze level (0-3), compression intensity
- Bollinger Band width percentile

**Market Structure:**
- Distance from POC, relative position in Value Area

**Momentum:**
- MACD histogram slope, RSI divergence, RSI overbought/oversold

### Model Architecture

**Supported Models:**
- XGBoost (Primary) - Superior handling of non-linear relationships
- Random Forest (Fallback) - Robust against outliers

**Prediction Target:**
- Probability of 5% price appreciation within 10 days

**Output:**
- Conviction Score: 0.0 to 1.0
- Recommendation: Strong Buy / Buy / Weak Buy / Hold / Weak Sell / Sell / Strong Sell
- Confidence Level: Very High / High / Medium / Low / Very Low

---

## 📖 Trading Journal Schema

### Trade Entry Format (JSON)

```json
{
  "trade_id": "STK-INFY-A1B2C3D4",
  "symbol": "INFY.NS",
  "direction": "Long",
  "setup": {
    "strategy": "Squeeze_Pro_Release",
    "conviction_score": 0.88,
    "indicators": {
      "ttm_squeeze": "Red",
      "price_above_200_ema": true,
      "rsi": 55.4,
      "macd_crossover": true
    },
    "volume_profile": {
      "poc": 1540.0,
      "price_above_vah": true
    }
  },
  "execution": {
    "entry_date": "2025-01-01T09:30:00Z",
    "entry_price": 1565.50,
    "quantity": 100,
    "stop_loss": 1520.0,
    "take_profit": 1680.0
  },
  "exit": {
    "exit_date": "2025-01-12T15:15:00Z",
    "exit_price": 1685.00,
    "pnl_percent": 7.63,
    "status": "Target_Reached"
  },
  "psychology": {
    "pre_trade_confidence": 4,
    "discipline_score": 5,
    "notes": "Strong sectoral tailwinds in Nifty IT favored the trade."
  }
}
```

---

## 📊 Performance Metrics

### Core Statistics

| Metric | Formula | Interpretation |
|--------|---------|-----------------|
| **Win Rate** | Winning Trades / Total Trades | % of profitable trades |
| **Profit Factor** | Gross Profits / \|Gross Losses\| | Ratio of wins to losses (>1.5 healthy) |
| **Expectancy (EV)** | (Win% × Avg Win) - (Loss% × Avg Loss) | Expected profit per trade |
| **Max Drawdown** | Largest peak-to-trough decline | Critical for risk management |
| **Consecutive Wins/Losses** | Longest streak | Psychological resilience |

### Analytics Dashboard

- **By Symbol**: Performance breakdown for each stock traded
- **By Setup Type**: Win rate and returns for each strategy variant
- **Time-Series**: Cumulative P&L over time, equity curve

---

## 🎨 Frontend Architecture

### Mobile-First Design Principles

1. **Responsive Grid System**: Adapts from 1 column (mobile) → 2 (tablet) → 3+ (desktop)
2. **Bottom Navigation**: Quick access to Screener, Watchlist, Journal, Analytics (mobile)
3. **Card-Based UI**: Dense information in scrollable cards instead of wide tables
4. **Touch-Optimized**: Larger tap targets (44px+), gesture support
5. **Performance**: Lightweight-charts library for smooth candlestick rendering

### Component Hierarchy

```
App
├── Header (Title, Subtitle)
├── Main Content
│   ├── ScreenerTab
│   │   ├── Controls (Limit slider, Run button)
│   │   └── StockGrid (Dynamic cards)
│   ├── WatchlistTab (High-conviction stocks)
│   ├── JournalTab
│   │   ├── TradeForm (New trade entry)
│   │   └── TradesList (Entry/exit history)
│   └── AnalyticsTab (Performance metrics grid)
└── BottomNav (Mobile navigation)
```

### Styling Approach

- **Mobile First**: Styles start mobile, then enhanced with media queries
- **Tailwind-inspired**: Utility classes for consistency
- **Dark Mode Ready**: CSS variables for theme switching
- **Accessibility**: WCAG 2.1 AA compliance, proper contrast ratios

---

## 🔌 API Endpoints

### Health & Config
- `GET /api/health` - Health check
- `GET /api/config` - Platform configuration

### Screening
- `GET /api/swing-screener?limit=10` - Run comprehensive screener
- `GET /api/screener/watchlist` - Get high-conviction setups (>0.75)

### Trading Journal
- `POST /api/journal/trades` - Log new trade entry
- `GET /api/journal/trades` - List all trades (queryable by status)
- `GET /api/journal/trades/{trade_id}` - Get specific trade
- `POST /api/journal/trades/{trade_id}/exit` - Close trade with exit data
- `DELETE /api/journal/trades/{trade_id}` - Delete trade

### Analytics
- `GET /api/journal/metrics` - Overall performance metrics
- `GET /api/journal/metrics/by-symbol` - Symbol-wise statistics
- `GET /api/journal/metrics/by-setup` - Setup-wise statistics
- `GET /api/journal/export` - Full journal export as JSON

---

## ⚙️ Configuration Reference

### Screening Parameters (`config.py`)

```python
SCREENING_PARAMS = {
    "min_daily_volume": 500_000,      # Minimum daily trading volume
    "atr_min_pct": 2.0,               # Minimum ATR as % of price
    "atr_max_pct": 5.0,               # Maximum ATR as % of price
    "min_delivery_pct": 40.0,         # Minimum delivery percentage
    "market_cap_threshold": 5000,     # Minimum market cap in Cr
    "data_period": "1y",              # Historical data period
    "data_interval": "1d",            # Data interval (daily)
}
```

### ML Model Parameters

```python
ML_PARAMS = {
    "model_type": "xgboost",          # xgboost or random_forest
    "conviction_threshold": 0.75,     # High-conviction threshold
    "prediction_window": 10,          # days for target return
    "target_return": 0.05,            # 5% expected return
    "train_lookback": 252,            # 1 year of trading days
}
```

---

## 🔄 Workflow Examples

### Daily Screening Workflow

1. Run screener: `GET /api/swing-screener?limit=20`
2. Review results sorted by conviction score (descending)
3. Identify high-conviction setups (Grade AAA, Score >0.85)
4. Check watchlist: `GET /api/screener/watchlist`
5. Plan entries based on Volume Profile confluence

### Trade Execution & Journaling

1. Log trade entry: `POST /api/journal/trades`
   - Include technical setup details
   - Set stop loss and take profit levels
   - Record psychological state

2. Monitor trade: `GET /api/journal/trades/{trade_id}`

3. Close trade: `POST /api/journal/trades/{trade_id}/exit`
   - Record actual exit price and P&L
   - Note execution quality

4. Review metrics: `GET /api/journal/metrics`

### Performance Analysis

1. Fetch metrics: `GET /api/journal/metrics`
   - Check win rate (target: >50%)
   - Verify profit factor (target: >1.5)
   - Monitor max drawdown

2. Analyze by symbol: `GET /api/journal/metrics/by-symbol`

3. Analyze by setup: `GET /api/journal/metrics/by-setup`
   - Identify best-performing setups
   - Refine system based on historical data

---

## 🛡️ Risk Management Rules

### Position Sizing
- **Max Risk Per Trade**: 1-2% of account equity
- **Risk/Reward Ratio**: Minimum 1:2 (1% risk for 2% reward)

### Stop Loss Placement
- **Intraday**: Below recent swing low or 2× ATR
- **Swing**: Below support level identified in Volume Profile
- **ATR-Based**: Entry - (1.5 × ATR)

### Exit Rules
- **Profit Taking**: At VAH or defined take-profit level
- **Stop Loss**: Strict exit on breach
- **Time-Based**: Exit if setup doesn't activate within defined period

### Drawdown Protection
- **Max Account Drawdown**: 20% circuit breaker
- **Max Consecutive Losses**: 3-5 consecutive losses → review setup
- **Daily Loss Limit**: 2% max daily loss before market break

---

## 📱 Mobile Usage Tips

### Optimal Experience

1. **Screen Orientation**: Portrait for scrolling, landscape for charts
2. **Gesture Controls**: 
   - Swipe left/right to navigate tabs
   - Tap card to expand details
   - Long-press for contextual menu
3. **Offline Mode**: (Planned) Local caching of recent data
4. **Push Notifications**: (Planned) Alert on high-conviction setups

### Device Recommendations

- **iOS**: iPhone 12 or later (iOS 15+)
- **Android**: Android 8.0+ with 2GB RAM minimum
- **Screen Size**: 5.5" or larger for optimal experience
- **Connection**: 4G or WiFi recommended

---

## 🚀 Deployment Guide

### Local Development

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Docker Deployment

```bash
# Build backend image
docker build -f backend/Dockerfile -t amktrading-backend .

# Build frontend image
docker build -f frontend/Dockerfile -t amktrading-frontend .

# Run with docker-compose
docker-compose up
```

### Cloud Deployment (Render/Heroku)

1. Backend: Deploy FastAPI app to Render/Heroku
2. Frontend: Deploy React app to Vercel/Netlify
3. Database: Use PostgreSQL for journal persistence
4. Caching: Enable Redis for indicator caching

---

## 📚 Learning Resources

### Technical Analysis Concepts

- **TTM Squeeze**: [TTM Squeeze Indicator Overview](https://www.threetmusketeersfx.com/)
- **Volume Profile**: [Auction Market Theory & Volume Profile](https://www.auctionmarkettheory.com/)
- **RSI Divergence**: [Investopedia - RSI Divergence](https://www.investopedia.com/)

### Indian Market Resources

- **NSE Data**: [NSE Website - Data & Statistics](https://www.nseindia.com/)
- **Market Holidays**: [NSE Holiday Calendar](https://www.nseindia.com/market-data/market-holidays)
- **Sectoral Indices**: [Nifty Sectoral Indices](https://www.nse-india.com/)

---

## 🐛 Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'pandas_ta'`
```bash
pip install pandas_ta==0.3.14
```

**Problem**: API returns 500 error on screener
- Check data availability from Yahoo Finance
- Verify ticker symbols have .NS suffix
- Check internet connection for data download

### Frontend Issues

**Problem**: "Cannot GET /api/..." error
- Verify backend is running on correct port (8000)
- Check CORS configuration in main.py
- Ensure API_BASE URL in .env matches backend URL

**Problem**: Mobile layout issues
- Clear browser cache (Cmd+Shift+R)
- Check viewport meta tag in index.html
- Test on actual mobile device

---

## 📝 License & Support

**Version**: 2.0.0  
**Last Updated**: December 31, 2025  
**Status**: Production-Ready

For support and feature requests, please refer to the project documentation or reach out through the official channels.

---

## 🎯 Future Roadmap

- [ ] Real-time WebSocket data streaming
- [ ] Mobile app (React Native)
- [ ] Options analysis integration
- [ ] Advanced portfolio optimization
- [ ] Automated trade alerts via Telegram/Discord
- [ ] Multi-timeframe analysis
- [ ] Sentiment analysis integration
- [ ] Performance attribution analytics
- [ ] Deep learning (LSTM) prediction models
- [ ] Community features & signal sharing
