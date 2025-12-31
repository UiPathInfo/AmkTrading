from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
import importlib.util
import sys
import os
import logging

from config import get_config, JOURNAL_DB_PATH
from journal import TradingJournal, TradeEntry, PerformanceMetrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load screener functions
def _load_module_function(file_name: str, func_name: str):
    """Robustly load function from module file."""
    try:
        # Try package import first
        module_name = file_name.replace(".py", "")
        exec(f"from {module_name} import {func_name} as _fn")
        return locals()["_fn"]
    except Exception:
        pass

    # Try direct file import
    try:
        base = os.path.dirname(__file__)
        path = os.path.join(base, file_name)
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location(f"backend.{module_name}", path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = mod
            spec.loader.exec_module(mod)
            return getattr(mod, func_name, None)
    except Exception as e:
        logger.error(f"Error loading {func_name} from {file_name}: {e}")
    
    return None


run_swing_screener = _load_module_function("SwingScreener.py", "run_swing_screener")

# Initialize journal and metrics
journal = TradingJournal(JOURNAL_DB_PATH)
config = get_config()

app = FastAPI(
    title=config['api']['title'],
    version=config['api']['version'],
    description=config['api']['description']
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Models
class ItemSchema(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None


class TradeEntrySchema(BaseModel):
    symbol: str
    direction: str  # 'Long' or 'Short'
    setup: Dict[str, Any]
    execution: Dict[str, Any]
    psychology: Optional[Dict[str, Any]] = None


class TradeExitSchema(BaseModel):
    exit_date: str
    exit_price: float
    pnl_percent: float
    status: str


# Health & Status Endpoints
@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "version": config['api']['version']}


@app.get("/api/config")
def get_api_config():
    """Get platform configuration."""
    return config


# Screener Endpoints
@app.get("/api/swing-screener")
def get_swing_screener(limit: int = 10, full_config: bool = False):
    """
    Run enhanced swing trading screener with technical analysis and ML conviction.
    
    Args:
        limit: Maximum number of stocks to analyze (1-50)
        full_config: Return full configuration with results
    """
    if run_swing_screener is None:
        raise HTTPException(status_code=500, detail="Swing screener not available")

    try:
        limit = max(1, min(limit, 50))
        screener_config = config if full_config else None
        results = run_swing_screener(max_stocks=limit, config=config)
        
        successful = [r for r in results if r.get('status') == 'success']
        failed = [r for r in results if r.get('status') != 'success']
        
        # Sort by conviction score
        successful.sort(key=lambda x: x.get('conviction', {}).get('conviction_score', 0), reverse=True)
        
        return {
            "status": "success",
            "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
            "total_analyzed": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "results": successful + failed,
            "config": screener_config
        }
    except Exception as e:
        logger.error(f"Screener error: {e}")
        raise HTTPException(status_code=500, detail=f"Screener execution failed: {e}")


@app.get("/api/screener/watchlist")
def get_watchlist():
    """Get current watchlist (high-conviction stocks from last scan)."""
    try:
        results = run_swing_screener(max_stocks=20, config=config)
        successful = [r for r in results if r.get('status') == 'success']
        
        # Filter for high conviction (>0.75)
        high_conviction = [r for r in successful 
                          if r.get('conviction', {}).get('conviction_score', 0) > 0.75]
        
        return {
            "watchlist": high_conviction,
            "count": len(high_conviction)
        }
    except Exception as e:
        logger.error(f"Watchlist error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Trading Journal Endpoints
@app.post("/api/journal/trades", status_code=201)
def create_trade_entry(trade: TradeEntrySchema):
    """Log a new trade entry."""
    try:
        import uuid
        trade_id = f"STK-{trade['symbol']}-{uuid.uuid4().hex[:8].upper()}"
        
        entry = TradeEntry(
            trade_id=trade_id,
            symbol=trade['symbol'],
            direction=trade['direction'],
            setup=trade['setup'],
            execution=trade['execution'],
            psychology=trade.get('psychology')
        )
        
        if journal.add_trade(entry):
            return {
                "status": "success",
                "trade_id": trade_id,
                "message": "Trade entry logged"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to add trade")
    except Exception as e:
        logger.error(f"Error creating trade: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/journal/trades")
def list_all_trades(status: Optional[str] = None):
    """
    Get trades from journal.
    
    Args:
        status: 'open', 'closed', or None for all
    """
    try:
        if status == 'open':
            trades = journal.get_open_trades()
        elif status == 'closed':
            trades = journal.get_closed_trades()
        else:
            trades = journal.get_all_trades()
        
        return {
            "status": "success",
            "count": len(trades),
            "trades": [t.to_dict() for t in trades]
        }
    except Exception as e:
        logger.error(f"Error retrieving trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/journal/trades/{trade_id}")
def get_trade(trade_id: str):
    """Get specific trade by ID."""
    try:
        trade = journal.get_trade(trade_id)
        if not trade:
            raise HTTPException(status_code=404, detail="Trade not found")
        return {"status": "success", "trade": trade.to_dict()}
    except Exception as e:
        logger.error(f"Error retrieving trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/journal/trades/{trade_id}/exit", status_code=200)
def close_trade(trade_id: str, exit_data: TradeExitSchema):
    """Close a trade with exit information."""
    try:
        if journal.update_trade_exit(trade_id, exit_data.dict()):
            return {
                "status": "success",
                "message": f"Trade {trade_id} closed"
            }
        else:
            raise HTTPException(status_code=404, detail="Trade not found")
    except Exception as e:
        logger.error(f"Error closing trade: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/journal/trades/{trade_id}")
def delete_trade(trade_id: str):
    """Delete a trade entry."""
    try:
        if journal.delete_trade(trade_id):
            return {"status": "success", "message": "Trade deleted"}
        else:
            raise HTTPException(status_code=404, detail="Trade not found")
    except Exception as e:
        logger.error(f"Error deleting trade: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Performance Analytics Endpoints
@app.get("/api/journal/metrics")
def get_performance_metrics():
    """Get comprehensive performance metrics from all closed trades."""
    try:
        metrics_calculator = PerformanceMetrics(journal)
        metrics = metrics_calculator.calculate_metrics()
        return {
            "status": "success",
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/journal/metrics/by-symbol")
def get_symbol_statistics():
    """Get performance metrics broken down by symbol."""
    try:
        metrics_calculator = PerformanceMetrics(journal)
        stats = metrics_calculator.get_trade_statistics_by_symbol()
        return {
            "status": "success",
            "symbol_stats": stats
        }
    except Exception as e:
        logger.error(f"Error calculating symbol stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/journal/metrics/by-setup")
def get_setup_statistics():
    """Get performance metrics broken down by setup type."""
    try:
        metrics_calculator = PerformanceMetrics(journal)
        stats = metrics_calculator.get_setup_statistics()
        return {
            "status": "success",
            "setup_stats": stats
        }
    except Exception as e:
        logger.error(f"Error calculating setup stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Export journal data
@app.get("/api/journal/export")
def export_journal():
    """Export full journal as JSON."""
    try:
        trades = journal.get_all_trades()
        return {
            "status": "success",
            "export_date": __import__('datetime').datetime.utcnow().isoformat(),
            "total_trades": len(trades),
            "trades": [t.to_dict() for t in trades]
        }
    except Exception as e:
        logger.error(f"Error exporting journal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config['api']['host'], port=config['api']['port'], 
                reload=config['api']['reload'])
