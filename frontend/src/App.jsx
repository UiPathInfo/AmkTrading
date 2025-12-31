import React, { useEffect, useState } from 'react'
import axios from 'axios'
import './styles.css'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function App() {
  // Navigation state
  const [activeTab, setActiveTab] = useState('home')
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768)
  
  // Home page state
  const [stats, setStats] = useState({
    lastUpdate: null,
    screenerReady: false,
    journalCount: 0,
    avgWinRate: 0
  })
  
  // Screener state
  const [screenerResults, setScreenerResults] = useState([])
  const [screenerLoading, setScreenerLoading] = useState(false)
  const [screenerError, setScreenerError] = useState(null)
  const [screenerLimit, setScreenerLimit] = useState(10)
  
  // Journal state
  const [trades, setTrades] = useState([])
  const [journalLoading, setJournalLoading] = useState(false)
  const [journalFilter, setJournalFilter] = useState('all')
  const [showTradeForm, setShowTradeForm] = useState(false)
  
  // Metrics state
  const [metrics, setMetrics] = useState(null)
  const [metricsLoading, setMetricsLoading] = useState(false)
  
  // Watchlist state
  const [watchlist, setWatchlist] = useState([])
  
  // Trade form state
  const [tradeForm, setTradeForm] = useState({
    symbol: '',
    direction: 'Long',
    entry_price: '',
    quantity: '',
    stop_loss: '',
    take_profit: '',
    conviction_score: 0.5
  })
  
  // Selected trade for details
  const [selectedTrade, setSelectedTrade] = useState(null)
  
  // Handle window resize
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])
  
  // Load home page stats
  useEffect(() => {
    loadStats()
  }, [])
  
  async function loadStats() {
    try {
      const res = await axios.get(`${API_BASE}/api/health`)
      setStats({
        lastUpdate: new Date().toLocaleTimeString(),
        screenerReady: res.data.status === 'ok',
        journalCount: 0,
        avgWinRate: 0
      })
      
      // Try to load metrics
      const metricsRes = await axios.get(`${API_BASE}/api/journal/metrics`)
      if (metricsRes.data.metrics) {
        setStats(prev => ({
          ...prev,
          journalCount: metricsRes.data.metrics.total_trades,
          avgWinRate: metricsRes.data.metrics.win_rate_pct
        }))
      }
    } catch (e) {
      console.error('Error loading stats:', e)
    }
  }
  
  // Fetch functions
  async function fetchScreener() {
    setScreenerLoading(true)
    setScreenerError(null)
    setActiveTab('screener')
    try {
      const res = await axios.get(`${API_BASE}/api/swing-screener?limit=${screenerLimit}`)
      setScreenerResults(res.data.results || [])
    } catch (e) {
      setScreenerError(e.message || 'Failed to fetch screener results')
    } finally {
      setScreenerLoading(false)
    }
  }
  
  async function fetchWatchlist() {
    setActiveTab('watchlist')
    try {
      const res = await axios.get(`${API_BASE}/api/screener/watchlist`)
      setWatchlist(res.data.watchlist || [])
    } catch (e) {
      console.error('Watchlist error:', e)
    }
  }
  
  async function fetchTrades() {
    setActiveTab('journal')
    setJournalLoading(true)
    try {
      const status = journalFilter !== 'all' ? `?status=${journalFilter}` : ''
      const res = await axios.get(`${API_BASE}/api/journal/trades${status}`)
      setTrades(res.data.trades || [])
    } catch (e) {
      console.error('Error fetching trades:', e)
    } finally {
      setJournalLoading(false)
    }
  }
  
  async function fetchMetrics() {
    setActiveTab('analytics')
    setMetricsLoading(true)
    try {
      const res = await axios.get(`${API_BASE}/api/journal/metrics`)
      setMetrics(res.data.metrics)
    } catch (e) {
      console.error('Error fetching metrics:', e)
    } finally {
      setMetricsLoading(false)
    }
  }
  
  async function addTrade(e) {
    e.preventDefault()
    try {
      const tradeData = {
        symbol: tradeForm.symbol,
        direction: tradeForm.direction,
        setup: {
          strategy: "Manual Entry",
          conviction_score: parseFloat(tradeForm.conviction_score),
        },
        execution: {
          entry_date: new Date().toISOString(),
          entry_price: parseFloat(tradeForm.entry_price),
          quantity: parseInt(tradeForm.quantity),
          stop_loss: parseFloat(tradeForm.stop_loss),
          take_profit: parseFloat(tradeForm.take_profit),
        },
      }
      
      const res = await axios.post(`${API_BASE}/api/journal/trades`, tradeData)
      alert(`Trade logged: ${res.data.trade_id}`)
      setTradeForm({
        symbol: '', direction: 'Long', entry_price: '', quantity: '',
        stop_loss: '', take_profit: '', conviction_score: 0.5
      })
      setShowTradeForm(false)
      fetchTrades()
    } catch (e) {
      alert(`Error: ${e.response?.data?.detail || e.message}`)
    }
  }
  
  useEffect(() => {
    fetchWatchlist()
  }, [])
  
  useEffect(() => {
    fetchTrades()
  }, [journalFilter])
  
  // Stock card component
  const StockCard = ({ stock, onClick }) => {
    const conviction = stock.conviction || {}
    const bgColor = conviction.conviction_score > 0.85 ? '#10b981' : 
                   conviction.conviction_score > 0.75 ? '#3b82f6' : '#6b7280'
    
    return (
      <div className="stock-card" onClick={onClick} style={{ borderLeftColor: bgColor }}>
        <div className="card-header">
          <div className="ticker">{stock.ticker}</div>
          <div className="price">₹{stock.price?.current?.toFixed(2) || 'N/A'}</div>
        </div>
        
        <div className="card-body">
          <div className="metric-row">
            <span className="label">Conviction</span>
            <span className="value">{(conviction.conviction_score * 100).toFixed(0)}%</span>
          </div>
          
          <div className="metric-row">
            <span className="label">Squeeze</span>
            <span className="badge" style={{ backgroundColor: stock.technical_analysis?.ttm_squeeze?.color }}>
              {stock.technical_analysis?.ttm_squeeze?.level?.toUpperCase() || 'N/A'}
            </span>
          </div>
          
          <div className="metric-row">
            <span className="label">Trend</span>
            <span className="value">{stock.technical_analysis?.trend?.regime || 'N/A'}</span>
          </div>
          
          <div className="metric-row">
            <span className="label">RSI</span>
            <span className="value">{stock.technical_analysis?.momentum?.rsi?.toFixed(1) || 'N/A'}</span>
          </div>
          
          <div className="metric-row">
            <span className="label">Grade</span>
            <span className="grade">{stock.technical_analysis?.confluence?.grade || 'B'}</span>
          </div>
        </div>
        
        <div className="card-footer">
          <span className="recommendation">{conviction.recommendation || 'Hold'}</span>
        </div>
      </div>
    )
  }
  
  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <h1 className="app-title">AMK Trading</h1>
          <p className="app-subtitle">Advanced Swing Trading Platform</p>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="main-content">
        {/* Home/Dashboard Tab */}
        {activeTab === 'home' && (
          <section className="tab-content">
            <h2>Dashboard</h2>
            
            <div className="dashboard-grid">
              {/* Stats Cards */}
              <div className="stats-section">
                <div className="stat-card">
                  <div className="stat-icon">📊</div>
                  <div className="stat-content">
                    <div className="stat-label">System Status</div>
                    <div className="stat-value">{stats.screenerReady ? 'Ready' : 'Offline'}</div>
                    <div className="stat-detail">{stats.lastUpdate}</div>
                  </div>
                </div>
                
                <div className="stat-card">
                  <div className="stat-icon">📈</div>
                  <div className="stat-content">
                    <div className="stat-label">Total Trades</div>
                    <div className="stat-value">{stats.journalCount}</div>
                    <div className="stat-detail">In journal</div>
                  </div>
                </div>
                
                <div className="stat-card">
                  <div className="stat-icon">🎯</div>
                  <div className="stat-content">
                    <div className="stat-label">Win Rate</div>
                    <div className="stat-value">{stats.avgWinRate}%</div>
                    <div className="stat-detail">Overall performance</div>
                  </div>
                </div>
              </div>
              
              {/* Tool Cards */}
              <div className="tools-section">
                <h3>Trading Tools</h3>
                
                <div className="tool-cards">
                  {/* Stock Screener Tool */}
                  <div className="tool-card" onClick={fetchScreener}>
                    <div className="tool-icon">🔍</div>
                    <div className="tool-header">
                      <h4>Stock Screener</h4>
                      <p>Find high-conviction swing trading setups</p>
                    </div>
                    <div className="tool-features">
                      <span className="feature">TTM Squeeze Analysis</span>
                      <span className="feature">ML Conviction Scoring</span>
                      <span className="feature">Volume Profile</span>
                    </div>
                    <button className="btn-launch">Launch →</button>
                  </div>
                  
                  {/* Watchlist Tool */}
                  <div className="tool-card" onClick={fetchWatchlist}>
                    <div className="tool-icon">⭐</div>
                    <div className="tool-header">
                      <h4>High-Conviction Watchlist</h4>
                      <p>Monitor filtered setups above 0.75 conviction</p>
                    </div>
                    <div className="tool-features">
                      <span className="feature">Auto-filtered Results</span>
                      <span className="feature">Real-time Updates</span>
                      <span className="feature">Quick Entry</span>
                    </div>
                    <button className="btn-launch">View →</button>
                  </div>
                  
                  {/* Trading Journal Tool */}
                  <div className="tool-card" onClick={fetchTrades}>
                    <div className="tool-icon">📔</div>
                    <div className="tool-header">
                      <h4>Trading Journal</h4>
                      <p>Log and track all your trades</p>
                    </div>
                    <div className="tool-features">
                      <span className="feature">Trade Entry/Exit</span>
                      <span className="feature">P&L Tracking</span>
                      <span className="feature">Psychology Notes</span>
                    </div>
                    <button className="btn-launch">Open →</button>
                  </div>
                  
                  {/* Performance Analytics Tool */}
                  <div className="tool-card" onClick={fetchMetrics}>
                    <div className="tool-icon">📊</div>
                    <div className="tool-header">
                      <h4>Performance Analytics</h4>
                      <p>Analyze your trading statistics and metrics</p>
                    </div>
                    <div className="tool-features">
                      <span className="feature">Win Rate Tracking</span>
                      <span className="feature">Profit Factor</span>
                      <span className="feature">Expectancy Analysis</span>
                    </div>
                    <button className="btn-launch">Analyze →</button>
                  </div>
                </div>
              </div>
              
              {/* Quick Actions */}
              <div className="quick-actions">
                <h3>Quick Actions</h3>
                <div className="action-buttons">
                  <button className="action-btn" onClick={() => { setShowTradeForm(!showTradeForm); setActiveTab('journal') }}>
                    ➕ New Trade
                  </button>
                  <button className="action-btn" onClick={loadStats}>
                    🔄 Refresh Stats
                  </button>
                  <button className="action-btn" onClick={() => setActiveTab('analytics')}>
                    📊 View Report
                  </button>
                </div>
              </div>
            </div>
          </section>
        )}
        
        {/* Screener Tab */}
        {activeTab === 'screener' && (
          <section className="tab-content">
            <h2>Stock Screener</h2>
            
            <div className="controls">
              <label>
                Max Stocks:
                <input 
                  type="number" 
                  min="1" 
                  max="50" 
                  value={screenerLimit}
                  onChange={(e) => setScreenerLimit(parseInt(e.target.value))}
                />
              </label>
              <button 
                onClick={fetchScreener}
                disabled={screenerLoading}
                className="btn-primary"
              >
                {screenerLoading ? 'Scanning...' : 'Run Screener'}
              </button>
            </div>
            
            {screenerError && (
              <div className="error-message">{screenerError}</div>
            )}
            
            <div className="stock-grid">
              {screenerResults.map(stock => (
                <StockCard 
                  key={stock.ticker}
                  stock={stock}
                  onClick={() => setSelectedTrade(stock)}
                />
              ))}
            </div>
            
            {screenerResults.length === 0 && !screenerLoading && (
              <p className="no-results">Run screener to see results</p>
            )}
          </section>
        )}
        
        {/* Watchlist Tab */}
        {activeTab === 'watchlist' && (
          <section className="tab-content">
            <h2>High-Conviction Watchlist</h2>
            
            <div className="stock-grid">
              {watchlist.map(stock => (
                <StockCard 
                  key={stock.ticker}
                  stock={stock}
                  onClick={() => setSelectedTrade(stock)}
                />
              ))}
            </div>
            
            {watchlist.length === 0 && (
              <p className="no-results">No high-conviction setups currently</p>
            )}
          </section>
        )}
        
        {/* Journal Tab */}
        {activeTab === 'journal' && (
          <section className="tab-content">
            <h2>Trading Journal</h2>
            
            <div className="controls">
              <select 
                value={journalFilter}
                onChange={(e) => setJournalFilter(e.target.value)}
              >
                <option value="all">All Trades</option>
                <option value="open">Open</option>
                <option value="closed">Closed</option>
              </select>
              <button 
                onClick={() => setShowTradeForm(!showTradeForm)}
                className="btn-primary"
              >
                {showTradeForm ? 'Cancel' : 'New Trade'}
              </button>
            </div>
            
            {showTradeForm && (
              <form onSubmit={addTrade} className="trade-form">
                <input
                  type="text"
                  placeholder="Symbol (e.g., INFY)"
                  value={tradeForm.symbol}
                  onChange={(e) => setTradeForm({...tradeForm, symbol: e.target.value})}
                  required
                />
                
                <select 
                  value={tradeForm.direction}
                  onChange={(e) => setTradeForm({...tradeForm, direction: e.target.value})}
                >
                  <option value="Long">Long</option>
                  <option value="Short">Short</option>
                </select>
                
                <input
                  type="number"
                  placeholder="Entry Price"
                  step="0.01"
                  value={tradeForm.entry_price}
                  onChange={(e) => setTradeForm({...tradeForm, entry_price: e.target.value})}
                  required
                />
                
                <input
                  type="number"
                  placeholder="Quantity"
                  value={tradeForm.quantity}
                  onChange={(e) => setTradeForm({...tradeForm, quantity: e.target.value})}
                  required
                />
                
                <input
                  type="number"
                  placeholder="Stop Loss"
                  step="0.01"
                  value={tradeForm.stop_loss}
                  onChange={(e) => setTradeForm({...tradeForm, stop_loss: e.target.value})}
                  required
                />
                
                <input
                  type="number"
                  placeholder="Take Profit"
                  step="0.01"
                  value={tradeForm.take_profit}
                  onChange={(e) => setTradeForm({...tradeForm, take_profit: e.target.value})}
                  required
                />
                
                <button type="submit" className="btn-primary">Log Trade</button>
              </form>
            )}
            
            <div className="trades-list">
              {trades.map(trade => (
                <div key={trade.trade_id} className="trade-item">
                  <div className="trade-header">
                    <span className="symbol">{trade.symbol}</span>
                    <span className="direction">{trade.direction}</span>
                    <span className={`status ${trade.exit ? 'closed' : 'open'}`}>
                      {trade.exit ? 'Closed' : 'Open'}
                    </span>
                  </div>
                  <div className="trade-details">
                    <span>Entry: ₹{trade.execution?.entry_price}</span>
                    {trade.exit && <span>Exit: ₹{trade.exit.exit_price}</span>}
                    {trade.exit && <span className="pnl">{trade.exit.pnl_percent > 0 ? '+' : ''}{trade.exit.pnl_percent.toFixed(2)}%</span>}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
        
        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <section className="tab-content">
            <h2>Performance Analytics</h2>
            
            <button 
              onClick={fetchMetrics}
              disabled={metricsLoading}
              className="btn-primary"
              style={{ marginBottom: '20px' }}
            >
              {metricsLoading ? 'Loading...' : 'Refresh Metrics'}
            </button>
            
            {metrics && (
              <div className="metrics-grid">
                <div className="metric-card">
                  <span className="label">Total Trades</span>
                  <span className="value">{metrics.total_trades}</span>
                </div>
                <div className="metric-card">
                  <span className="label">Win Rate</span>
                  <span className="value">{metrics.win_rate_pct}%</span>
                </div>
                <div className="metric-card">
                  <span className="label">Profit Factor</span>
                  <span className="value">{metrics.profit_factor.toFixed(2)}</span>
                </div>
                <div className="metric-card">
                  <span className="label">Expectancy</span>
                  <span className="value">{metrics.expectancy_pct.toFixed(2)}%</span>
                </div>
                <div className="metric-card">
                  <span className="label">Max Drawdown</span>
                  <span className="value negative">{metrics.max_drawdown_pct.toFixed(2)}%</span>
                </div>
                <div className="metric-card">
                  <span className="label">Total Return</span>
                  <span className={`value ${metrics.total_return_pct > 0 ? 'positive' : 'negative'}`}>
                    {metrics.total_return_pct > 0 ? '+' : ''}{metrics.total_return_pct.toFixed(2)}%
                  </span>
                </div>
              </div>
            )}
          </section>
        )}
      </main>
      
      {/* Bottom Navigation */}
      <nav className="bottom-nav">
        <button 
          className={`nav-item ${activeTab === 'home' ? 'active' : ''}`}
          onClick={() => setActiveTab('home')}
          title="Dashboard"
        >
          🏠 Home
        </button>
        <button 
          className={`nav-item ${activeTab === 'screener' ? 'active' : ''}`}
          onClick={() => setActiveTab('screener')}
          title="Stock Screener"
        >
          🔍 Screener
        </button>
        <button 
          className={`nav-item ${activeTab === 'watchlist' ? 'active' : ''}`}
          onClick={() => setActiveTab('watchlist')}
          title="High-Conviction Watchlist"
        >
          ⭐ Watchlist
        </button>
        <button 
          className={`nav-item ${activeTab === 'journal' ? 'active' : ''}`}
          onClick={() => setActiveTab('journal')}
          title="Trading Journal"
        >
          📔 Journal
        </button>
        <button 
          className={`nav-item ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
          title="Performance Analytics"
        >
          📊 Analytics
        </button>
      </nav>
      
      {/* Stock Detail Modal */}
      {selectedTrade && (
        <div className="modal-overlay" onClick={() => setSelectedTrade(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setSelectedTrade(null)}>×</button>
            
            <h3>{selectedTrade.ticker}</h3>
            <p>Price: ₹{selectedTrade.price?.current?.toFixed(2)}</p>
            
            <div className="modal-section">
              <h4>Conviction Analysis</h4>
              <p>Score: {(selectedTrade.conviction?.conviction_score * 100).toFixed(0)}%</p>
              <p>Recommendation: {selectedTrade.conviction?.recommendation}</p>
            </div>
            
            <div className="modal-section">
              <h4>Technical Setup</h4>
              <p>Squeeze: {selectedTrade.technical_analysis?.ttm_squeeze?.level?.toUpperCase()}</p>
              <p>Trend: {selectedTrade.technical_analysis?.trend?.regime}</p>
              <p>RSI: {selectedTrade.technical_analysis?.momentum?.rsi?.toFixed(1)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
