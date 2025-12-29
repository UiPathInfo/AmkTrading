import React, { useEffect, useState } from 'react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function App() {
  const [items, setItems] = useState([])
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')

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

  return (
    <div className="container py-4">
      <div className="row">
        <div className="col-12 col-md-6 mx-auto">
          <h1 className="mb-3">AMK Trading — Items</h1>

          <form onSubmit={addItem} className="mb-4">
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
  )
}
