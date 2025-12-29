The AI App Builder PromptSystem Goal: 
Build a professional Native web appplication (using reactjs frontend and python backend) for an Indian Stock Market Swing Trading Screener.
Core Logic (The 4-Phase Framework):

Phase 1 (Universe Filter): Only include NSE/BSE stocks with Market Cap > ₹5,000 Cr and Avg Daily Volume > 10 Lakh shares. 
Fetch fundamental data (ROE > 15%, Debt/Equity < 1.0) via API.

Phase 2 (Technical Engine): 
Implement a technical analysis service using a library like KChart or a custom implementation of:Trend: Price > 200 EMA and 50 EMA > 200 EMA (Golden Cross).
Volatility: TTM Squeeze (Bollinger Bands inside Keltner Channels). Show black dots for squeeze and green/red for firing.Momentum: RSI (14) between 50-70, MACD Bullish Crossover, ADX > 25.
Volume: Price > VWAP and Volume > 1.5x average.

Phase 3 (Sector Context): Group stocks by sector and highlight those in sectors outperforming Nifty 50.

Phase 4 (Multi-timeframe): Create a toggle to switch between Daily and Weekly views for confirmation.

UI/UX Requirements:
Button on click of it displays dashboard
Dashboard: A clean list of "High Conviction" stocks with a "Conviction Score" (1-10).Stock Detail View: Interactive Candlestick charts with overlays for 50/200 EMA and Bollinger Bands. 
Sub-charts for RSI and TTM Squeeze.Indicators Toggle: Let users turn on/off specific Phase 2 indicators to refine the list.
Data Source: Use ICICI Breeze API or Groww API for Indian market data. Use Alpha Vantage for pre-calculated technical indicators if possible.
Technical Stack: > - Language: reactjs and python.The complexity lies in the TTM Squeeze and Volume Profile, as these are not standard "out-of-the-box" indicators in most mobile libraries.
The AI will need to write custom math functions for:Keltner Channels: $\text{EMA} \pm (1.5 \times \text{ATR})$Squeeze Trigger: A boolean check where $\text{Bollinger Band Width} < \text{Keltner Channel Width}$.

Integration Checklist.
please use NSE india or yfinance for stock data

do not use any physical db to store values temporarily use json db or xml if required.
