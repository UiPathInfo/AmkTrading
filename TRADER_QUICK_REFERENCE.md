# AMK Trading Platform - Quick Reference Card

## 🎯 Trading Setup Grading System

### Setup Grades (Confidence Levels)

| Grade | Criteria | Target Probability |
|-------|----------|-------------------|
| **AAA** | 5/5 confluence factors | 85-95% conviction |
| **A+** | 4/5 confluence factors | 70-85% conviction |
| **A** | 3/5 confluence factors | 60-70% conviction |
| **B** | 1-2 confluence factors | 40-60% conviction |

### Confluence Factors Checklist

- [ ] **Volatility**: Price releasing from RED/ORANGE TTM Squeeze
- [ ] **Structural**: Price above POC, entering LVN
- [ ] **Trend**: Trading above 200 EMA + Nifty 50 bullish
- [ ] **Institutional**: Delivery % >50% on up-day
- [ ] **ML Score**: Random Forest probability >0.80

---

## 📊 Technical Indicators Quick Reference

### TTM Squeeze Pro (Compression Levels)

```
RED    🔴 = Highest compression (BB inside 1.0 ATR)
       → Maximum energy storage, explosive breakout likely

ORANGE 🟠 = Mid compression (BB inside 1.5 ATR)
       → Building pressure, watch for release

GRAY   ⚫ = Low compression (BB inside 2.0 ATR)
       → Normal volatility, less predictable
```

**Action**: Watch histogram for momentum acceleration on release.

### Volume Profile Levels

- **POC** (Point of Control): Magnet price level - expect reversions
- **VAH** (Value Area High): Resistance on breakout above
- **VAL** (Value Area Low): Support on pullback in uptrend
- **HVN** (High Volume Node): Consolidation zones
- **LVN** (Low Volume Node): Fast movement zones

**80% Rule**: Price in VAL + 2 consecutive 30-min holds = 80% probability of full value area traverse.

### Momentum Signals

| Indicator | Bullish | Bearish |
|-----------|---------|---------|
| **RSI** | 40-70 (rising) | <30 (falling) |
| **MACD** | +Div, Crossover | -Div, Crossover |
| **Price vs 200 EMA** | Above + Rising | Below + Falling |
| **MACD Histogram** | Light green | Dark red |

### Divergence Patterns (Reversal Signals)

- **Bullish Div**: Price LL, RSI HL → Reversal imminent
- **Hidden Bullish**: Price HL, RSI LL → Strong continuation
- **Bearish Div**: Price HH, RSI LH → Reversal likely
- **Hidden Bearish**: Price LH, RSI HH → Strong downtrend

---

## 💰 Position Sizing Framework

### Risk Management Rules

**Step 1: Calculate Risk Per Trade**
```
Max Risk = Account Size × 1-2%
```

**Step 2: Determine Position Size**
```
Quantity = Max Risk / (Entry Price - Stop Loss)
```

**Step 3: Calculate Potential Return**
```
Target Return = Quantity × (Take Profit - Entry Price)
Return % = Target Return / Account Size
```

**Step 4: Validate Risk/Reward**
```
Risk/Reward Ratio should be ≥ 1:2
Example: 1% risk for 2%+ reward
```

### Example Calculation

```
Account: ₹100,000
Max Risk: ₹1,500 (1.5%)

Stock: INFY @ ₹1,500
Entry: ₹1,500
Stop Loss: ₹1,450 (50 points = 3.33%)
Take Profit: ₹1,600 (100 points = 6.67%)

Risk Per Trade: 50 points
Position Size: 1,500 / 50 = 30 shares
Potential Profit: 30 × 100 = ₹3,000 (3%)

Risk/Reward = 1,500 / 3,000 = 1:2 ✓ VALID
```

---

## 📈 Performance Tracking Dashboard

### Key Metrics to Monitor

```
Daily Tracking
├── Win Rate % (Target: ≥50%)
├── Profit Factor (Target: ≥1.5)
├── Daily P&L
└── Consecutive Wins/Losses

Weekly Review
├── Total Trades this week
├── Winning % of setups
├── Best performing symbol
└── Worst performing setup

Monthly Analysis
├── Monthly Return %
├── Largest Win Trade
├── Largest Loss Trade
├── Max Drawdown
└── Win/Loss Ratio
```

### Red Flags ⚠️

| Signal | Action |
|--------|--------|
| 3+ consecutive losses | Pause trading, review setup |
| Win rate drops below 40% | Tighten confluence rules |
| Max drawdown >20% | Reduce position sizes |
| Profit factor <1.2 | Analyze losing trades |
| Avg loss > Avg win | Improve exits with TP levels |

---

## 🔄 Daily Trading Checklist

### Pre-Market (8:00-9:15 AM)

- [ ] Run swing screener: `GET /api/swing-screener?limit=20`
- [ ] Check watchlist: `GET /api/screener/watchlist`
- [ ] Review high-conviction setups (Score >0.75)
- [ ] Note key technical levels (POC, VAH, VAL)
- [ ] Identify support/resistance from Volume Profile
- [ ] Check Nifty 50 trend on 200 EMA

### Market Hours (9:15 AM-3:30 PM)

- [ ] Monitor open positions: `GET /api/journal/trades?status=open`
- [ ] Watch for TTM Squeeze releases
- [ ] Check confluence on existing positions
- [ ] Manage stop losses at -2% ATR or below support
- [ ] Update live P&L tracking

### On Trade Entry

- [ ] Log trade: `POST /api/journal/trades`
- [ ] Record setup type (Squeeze, VolProfile, MACD, etc.)
- [ ] Document conviction score
- [ ] Set alerts at stop loss and take profit
- [ ] Note psychological confidence level (1-5)

### On Trade Exit

- [ ] Close trade: `POST /api/journal/trades/{trade_id}/exit`
- [ ] Record actual exit price and P&L
- [ ] Note exit reason (target hit, SL hit, time stop)
- [ ] Update performance metrics immediately

### Post-Market (3:30-4:00 PM)

- [ ] Review closed trades
- [ ] Analyze P&L by setup type
- [ ] Check win rate for the day
- [ ] Note recurring patterns
- [ ] Plan tomorrow's setup focus areas

---

## 🎯 Setup Priority Ranking

### Highest Conviction (AAA Setups)
```
1. TTM Squeeze Release + RSI Bullish Div
2. Volume Profile Breakout + POC Confirmation
3. MACD Crossover + 200 EMA Breakout
4. Delivery Spike + Momentum Divergence
```

### High Conviction (A Setups)
```
1. TTM Squeeze Release (any level)
2. Volume Profile Support Hold
3. MACD Positive Divergence
4. Price above 200 EMA
```

### Medium Conviction (B Setups)
```
1. RSI Overbought/Oversold
2. Single confluence factor
3. Weak signals on lower conviction
```

---

## 💡 Common Entry Patterns

### Pattern 1: Squeeze Release + Bullish Divergence
```
Setup:
- Price compressed for 3+ days (RED dots)
- Histogram releases (light green)
- RSI makes higher low (divergence)

Entry: On momentum histogram color change
Stop: Below squeeze low
Target: +5-7% from entry
Win Rate: 70-75% historically
```

### Pattern 2: Volume Profile Support
```
Setup:
- Price pulls back to VAL
- High volume at support level
- Price holds for 2 bars

Entry: On move above VAL
Stop: Below VAL support
Target: VAH or +3-5%
Win Rate: 65-70% historically
```

### Pattern 3: MACD + 200 EMA Confluence
```
Setup:
- Price above 200 EMA (rising)
- MACD crosses above signal line
- MACD histogram turns positive

Entry: On MACD crossover confirmation
Stop: Below 200 EMA
Target: +4-6%
Win Rate: 60-65% historically
```

### Pattern 4: Delivery Institutional Accumulation
```
Setup:
- Delivery % >50% on up day
- Volume above 20-day average
- Price closes above previous high

Entry: Next day on strength
Stop: Below delivery support
Target: +5-8%
Win Rate: 65-72% historically
```

---

## 📱 Mobile Quick Actions

### Screener Tab
1. Adjust limit slider (1-50 stocks)
2. Tap "Run Screener"
3. Tap any card to see details
4. Tap "New Trade" to log entry

### Watchlist Tab
1. View filtered high-conviction setups
2. Tap card for full analysis
3. Review technical setup details

### Journal Tab
1. View all trades or filter by status
2. Tap trade to expand details
3. Tap "New Trade" to log entry
4. Swipe to delete (if needed)

### Analytics Tab
1. Tap "Refresh Metrics"
2. View 6-card metric summary
3. Review win rate and profit factor
4. Check max drawdown status

---

## 🚨 Risk Management Limits

```
DAILY LIMITS
├── Max Daily Loss: -2% account
├── Max Consecutive Losses: 3 trades
└── Daily Win Target: 1-2 trades

POSITION LIMITS
├── Max Position Size: 3% account
├── Min Risk/Reward: 1:2
└── Max Positions Open: 3-5 trades

SYSTEM LIMITS
├── Min Conviction: 0.60 (60%)
├── Max Slippage Tolerance: 0.5%
└── Min Liquidity: 500k daily volume
```

---

## 📞 Troubleshooting Quick Guide

| Issue | Solution |
|-------|----------|
| No screener results | Check internet, verify tickers in stock_list.ods |
| API connection error | Verify backend running on :8000 |
| Mobile layout broken | Clear cache (Cmd+Shift+R), refresh page |
| Trade not logging | Check symbol format (e.g., INFY not INFY.NS) |
| Metrics showing zero | Ensure trades have exit data logged |

---

## 📊 Sample Trade Journal Entry

```json
{
  "symbol": "INFY",
  "direction": "Long",
  "conviction_score": 0.88,
  "setup": "Squeeze_Pro_Release",
  "technical": {
    "ttm_squeeze": "Red",
    "price_above_200_ema": true,
    "rsi": 45,
    "macd_positive": true
  },
  "entry": {
    "date": "2025-01-31",
    "price": 1565.50,
    "quantity": 50,
    "sl": 1520.00,
    "tp": 1650.00
  },
  "exit": {
    "date": "2025-02-07",
    "price": 1645.00,
    "pnl_percent": 5.09
  }
}
```

---

## 🎓 Educational Resources

### Recommended Reading
- "Market Profile" by James Dalton
- "Come Into My Trading Room" by Alexander Elder
- "Systematic Trading" by Robert Carver

### Practice
- Backtest setups on historical data
- Paper trade for 1 month before live trading
- Review trades weekly for pattern recognition
- Keep trading journal consistently

### Continuous Learning
- Monitor win rate and profit factor weekly
- Adjust position sizes based on drawdown
- Refine entry/exit rules based on statistics
- Update ML model with new trade data quarterly

---

## ✅ Pre-Trade Checklist (Last Minute)

Before entering ANY trade:

- [ ] Is conviction score ≥0.75? (AAA or A+ grade)
- [ ] Is risk/reward ratio ≥1:2?
- [ ] Can I see 3+ confluence factors?
- [ ] Is daily loss limit not exceeded?
- [ ] Do I have <3 consecutive losses today?
- [ ] Is position size calculated correctly?
- [ ] Are stop loss and take profit set?
- [ ] Have I logged the setup details?

**If ANY checkbox is unchecked → SKIP THIS TRADE**

---

**Last Updated**: December 31, 2025  
**Version**: 2.0.0  
**Print Format**: A4 (fits on 3 pages)
