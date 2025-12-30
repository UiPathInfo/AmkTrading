import React, { useEffect, useState } from 'react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function App() {
  const [items, setItems] = useState([])
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')
  const [screenerResults, setScreenerResults] = useState(null)
  const [screenerLoading, setScreenerLoading] = useState(false)
  const [screenerError, setScreenerError] = useState(null)
  const [swingResults, setSwingResults] = useState(null)
  const [swingLoading, setSwingLoading] = useState(false)
  const [swingError, setSwingError] = useState(null)
  const [swingLimit, setSwingLimit] = useState(10)

  useEffect(() => {
    fetchItems()
  }, [])

  async function fetchItems() {
    try {
      const res = await axios.get(`${API_BASE}/api/items`)
      setItems(res.data)
    } catch (e) {
      console.error(e)
    }
  }

  async function addItem(e) {
    e.preventDefault()
    try {
      const res = await axios.post(`${API_BASE}/api/items`, { name, description: desc })
      setItems(prev => [...prev, res.data])
      setName('')
      setDesc('')
    } catch (e) {
      console.error(e)
    }
  }

  async function fetchScreener() {
    setScreenerLoading(true)
    setScreenerError(null)
    try {
      const res = await axios.get(`${API_BASE}/api/screener`)
      setScreenerResults(res.data)
    } catch (e) {
      console.error(e)
      setScreenerError(e.message || 'Failed to fetch screener results')
    } finally {
      setScreenerLoading(false)
    }
  }

  async function fetchSwingScreener() {
    setSwingLoading(true)
    setSwingError(null)
    try {
      const res = await axios.get(`${API_BASE}/api/swing-screener?limit=${swingLimit}`)
      setSwingResults(res.data)
    } catch (e) {
      console.error(e)
      setSwingError(e.message || 'Failed to fetch swing screener results')
    } finally {
      setSwingLoading(false)
    }
  }

  return (
    <div className="container py-4">
      <div className="row">
        <div className="col-12 col-md-8 mx-auto">
          <h1 className="mb-4">AMK Trading</h1>

          {/* Fundamental Screener */}
          <div className="mb-4">
            <h5 className="mb-3">Fundamental Stock Screener</h5>
            <button
              className="btn btn-success mb-3 w-100"
              onClick={fetchScreener}
              disabled={screenerLoading}
            >
              {screenerLoading ? 'Loading Screener...' : 'Run Fundamental Screener'}
            </button>

            {screenerError && (
              <div className="alert alert-danger mb-3">
                Error: {screenerError}
              </div>
            )}

            {screenerResults && (
              <div className="alert alert-info mb-3">
                <h6>Screener Results</h6>
                <p><strong>Count:</strong> {screenerResults.count}</p>
                {screenerResults.error ? (
                  <p className="text-danger"><strong>Error:</strong> {screenerResults.error}</p>
                ) : (
                  <div>
                    <p className="mb-2"><strong>Results:</strong></p>
                    <pre className="bg-light p-2" style={{ maxHeight: '300px', overflowY: 'auto', fontSize: '0.875rem' }}>
                      {JSON.stringify(screenerResults.results, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Swing Trading Screener */}
          <div className="mb-4">
            <h5 className="mb-3">Swing Trading Screener</h5>
            <div className="input-group mb-3">
              <label className="input-group-text">Max Stocks:</label>
              <input
                type="number"
                className="form-control"
                min="1"
                max="50"
                value={swingLimit}
                onChange={e => setSwingLimit(Math.max(1, Math.min(50, parseInt(e.target.value) || 10)))}
                disabled={swingLoading}
              />
              <button
                className="btn btn-warning"
                onClick={fetchSwingScreener}
                disabled={swingLoading}
              >
                {swingLoading ? 'Analyzing...' : 'Run Swing Screener'}
              </button>
            </div>

            {swingError && (
              <div className="alert alert-danger mb-3">
                Error: {swingError}
              </div>
            )}

            {swingResults && (
              <div className="alert alert-warning mb-3">
                <h6>Swing Trade Analysis</h6>
                <p>
                  <strong>Total Analyzed:</strong> {swingResults.total_analyzed} |
                  <strong> Successful:</strong> {swingResults.successful} |
                  <strong> Failed:</strong> {swingResults.failed}
                </p>
                {swingResults.error ? (
                  <p className="text-danger"><strong>Error:</strong> {swingResults.error}</p>
                ) : swingResults.results && swingResults.results.length > 0 ? (
                  <div>
                    <div className="table-responsive" style={{ fontSize: '0.875rem' }}>
                      <table className="table table-sm mb-0">
                        <thead>
                          <tr>
                            <th>Ticker</th>
                            <th>Price</th>
                            <th>Squeeze</th>
                            <th>Momentum</th>
                            <th>POC</th>
                            <th>RSI</th>
                            <th>Regime</th>
                          </tr>
                        </thead>
                        <tbody>
                          {swingResults.results.map((stock, idx) => (
                            <tr key={idx}>
                              <td>{stock.ticker}</td>
                              <td>{stock.current_price || 'N/A'}</td>
                              <td>{stock.squeeze_status || 'N/A'}</td>
                              <td>{stock.momentum || 'N/A'}</td>
                              <td>{stock.poc_support || 'N/A'}</td>
                              <td>{stock.rsi || 'N/A'}</td>
                              <td>{stock.regime || 'N/A'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ) : (
                  <p>No results available</p>
                )}
              </div>
            )}
          </div>

          {/* Items Management */}
          <div className="mb-4">
            <h5 className="mb-3">Items</h5>
            <form onSubmit={addItem} className="mb-3">
              <div className="mb-2">
                <label className="form-label">Name</label>
                <input className="form-control" value={name} onChange={e => setName(e.target.value)} required />
              </div>
              <div className="mb-2">
                <label className="form-label">Description</label>
                <input className="form-control" value={desc} onChange={e => setDesc(e.target.value)} />
              </div>
              <button className="btn btn-primary" type="submit">Add Item</button>
            </form>

            <ul className="list-group">
              {items.map(it => (
                <li key={it.id} className="list-group-item">
                  <div className="d-flex justify-content-between align-items-start">
                    <div>
                      <div className="fw-bold">{it.name}</div>
                      <div className="text-muted small">{it.description}</div>
                    </div>
                    <div className="badge bg-secondary rounded-pill">#{it.id}</div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
