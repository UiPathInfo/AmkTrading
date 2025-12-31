"""
Trading Journal Database and Performance Metrics Engine

Manages:
- Trade entry/exit logging with JSON schema
- Performance metrics calculation (win rate, profit factor, expectancy, max drawdown)
- Journal persistence and retrieval
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TradeEntry:
    """Trade entry dataclass matching JSON schema."""
    trade_id: str
    symbol: str
    direction: str  # 'Long' or 'Short'
    setup: Dict[str, Any]
    execution: Dict[str, Any]
    exit: Optional[Dict[str, Any]] = None
    psychology: Optional[Dict[str, Any]] = None
    created_at: str = ""
    updated_at: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


class TradingJournal:
    """Manage trading journal entries and performance metrics."""
    
    def __init__(self, journal_path: str):
        """
        Initialize trading journal.
        
        Args:
            journal_path: Path to JSON file storing trades
        """
        self.journal_path = Path(journal_path)
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        self.trades: List[TradeEntry] = []
        self._load_journal()
    
    def _load_journal(self) -> None:
        """Load existing journal from file."""
        if self.journal_path.exists():
            try:
                with open(self.journal_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.trades = [TradeEntry(**t) for t in data]
                    elif isinstance(data, dict) and 'trades' in data:
                        self.trades = [TradeEntry(**t) for t in data['trades']]
                logger.info(f"Loaded {len(self.trades)} trades from journal")
            except Exception as e:
                logger.error(f"Error loading journal: {e}")
                self.trades = []
    
    def _save_journal(self) -> None:
        """Save journal to file."""
        try:
            with open(self.journal_path, 'w') as f:
                json.dump([t.to_dict() for t in self.trades], f, indent=2)
            logger.info(f"Journal saved with {len(self.trades)} trades")
        except Exception as e:
            logger.error(f"Error saving journal: {e}")
    
    def add_trade(self, trade_entry: TradeEntry) -> bool:
        """
        Add new trade entry.
        
        Args:
            trade_entry: TradeEntry object
            
        Returns:
            True if successful
        """
        try:
            trade_entry.created_at = datetime.utcnow().isoformat() + "Z"
            trade_entry.updated_at = trade_entry.created_at
            self.trades.append(trade_entry)
            self._save_journal()
            logger.info(f"Trade added: {trade_entry.trade_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding trade: {e}")
            return False
    
    def update_trade_exit(self, trade_id: str, exit_data: Dict[str, Any]) -> bool:
        """
        Update trade with exit information.
        
        Args:
            trade_id: ID of trade to update
            exit_data: Exit information (exit_date, exit_price, pnl_percent, status)
            
        Returns:
            True if successful
        """
        try:
            for trade in self.trades:
                if trade.trade_id == trade_id:
                    trade.exit = exit_data
                    trade.updated_at = datetime.utcnow().isoformat() + "Z"
                    self._save_journal()
                    logger.info(f"Trade exited: {trade_id}")
                    return True
            logger.warning(f"Trade not found: {trade_id}")
            return False
        except Exception as e:
            logger.error(f"Error updating trade: {e}")
            return False
    
    def get_trade(self, trade_id: str) -> Optional[TradeEntry]:
        """Get specific trade by ID."""
        for trade in self.trades:
            if trade.trade_id == trade_id:
                return trade
        return None
    
    def get_all_trades(self) -> List[TradeEntry]:
        """Get all trades."""
        return self.trades
    
    def get_closed_trades(self) -> List[TradeEntry]:
        """Get only closed trades (with exit data)."""
        return [t for t in self.trades if t.exit is not None]
    
    def get_open_trades(self) -> List[TradeEntry]:
        """Get only open trades (without exit data)."""
        return [t for t in self.trades if t.exit is None]
    
    def get_trades_by_symbol(self, symbol: str) -> List[TradeEntry]:
        """Get trades for specific symbol."""
        return [t for t in self.trades if t.symbol == symbol]
    
    def delete_trade(self, trade_id: str) -> bool:
        """Delete trade entry."""
        try:
            self.trades = [t for t in self.trades if t.trade_id != trade_id]
            self._save_journal()
            logger.info(f"Trade deleted: {trade_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting trade: {e}")
            return False


class PerformanceMetrics:
    """Calculate performance metrics from trading journal."""
    
    def __init__(self, journal: TradingJournal):
        self.journal = journal
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics.
        
        Returns:
            Dictionary with all performance metrics
        """
        closed_trades = self.journal.get_closed_trades()
        
        if not closed_trades:
            return self._empty_metrics()
        
        pnl_values = []
        win_trades = []
        loss_trades = []
        
        for trade in closed_trades:
            if trade.exit and 'pnl_percent' in trade.exit:
                pnl = trade.exit['pnl_percent']
                pnl_values.append(pnl)
                
                if pnl > 0:
                    win_trades.append(pnl)
                elif pnl < 0:
                    loss_trades.append(pnl)
        
        if not pnl_values:
            return self._empty_metrics()
        
        # Calculate metrics
        total_trades = len(closed_trades)
        winning_trades = len(win_trades)
        losing_trades = len(loss_trades)
        breakeven_trades = total_trades - winning_trades - losing_trades
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        loss_rate = losing_trades / total_trades if total_trades > 0 else 0
        
        avg_win = sum(win_trades) / len(win_trades) if win_trades else 0
        avg_loss = sum(loss_trades) / len(loss_trades) if loss_trades else 0
        
        # Profit Factor
        gross_profits = sum(win_trades) if win_trades else 0
        gross_losses = abs(sum(loss_trades)) if loss_trades else 0
        profit_factor = gross_profits / gross_losses if gross_losses > 0 else 0
        
        # Expectancy
        expectancy = (win_rate * avg_win) - (loss_rate * abs(avg_loss))
        
        # Max Drawdown
        max_drawdown = self._calculate_max_drawdown(pnl_values)
        
        # Total return
        total_return = sum(pnl_values)
        
        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "breakeven_trades": breakeven_trades,
            "win_rate_pct": round(win_rate * 100, 2),
            "loss_rate_pct": round(loss_rate * 100, 2),
            "avg_win_pct": round(avg_win, 2),
            "avg_loss_pct": round(avg_loss, 2),
            "gross_profits_pct": round(gross_profits, 2),
            "gross_losses_pct": round(gross_losses, 2),
            "profit_factor": round(profit_factor, 2),
            "expectancy_pct": round(expectancy, 2),
            "max_drawdown_pct": round(max_drawdown, 2),
            "total_return_pct": round(total_return, 2),
            "largest_win_pct": round(max(win_trades) if win_trades else 0, 2),
            "largest_loss_pct": round(min(loss_trades) if loss_trades else 0, 2),
            "consecutive_wins": self._max_consecutive_wins(closed_trades),
            "consecutive_losses": self._max_consecutive_losses(closed_trades),
        }
    
    def get_trade_statistics_by_symbol(self) -> Dict[str, Dict[str, Any]]:
        """Get performance metrics broken down by symbol."""
        symbols = set(t.symbol for t in self.journal.get_closed_trades())
        stats = {}
        
        for symbol in symbols:
            trades = [t for t in self.journal.get_closed_trades() if t.symbol == symbol]
            pnl_values = [t.exit['pnl_percent'] for t in trades if t.exit]
            
            stats[symbol] = {
                "trades": len(trades),
                "wins": sum(1 for p in pnl_values if p > 0),
                "losses": sum(1 for p in pnl_values if p < 0),
                "win_rate_pct": round((sum(1 for p in pnl_values if p > 0) / len(pnl_values) * 100), 2) if pnl_values else 0,
                "total_return_pct": round(sum(pnl_values), 2),
                "avg_return_pct": round(sum(pnl_values) / len(pnl_values), 2) if pnl_values else 0,
            }
        
        return stats
    
    def get_setup_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get performance metrics broken down by setup type."""
        setups = {}
        
        for trade in self.journal.get_closed_trades():
            setup_type = trade.setup.get('strategy', 'Unknown')
            if setup_type not in setups:
                setups[setup_type] = []
            
            if trade.exit:
                setups[setup_type].append(trade.exit.get('pnl_percent', 0))
        
        stats = {}
        for setup, pnl_values in setups.items():
            stats[setup] = {
                "trades": len(pnl_values),
                "wins": sum(1 for p in pnl_values if p > 0),
                "win_rate_pct": round((sum(1 for p in pnl_values if p > 0) / len(pnl_values) * 100), 2) if pnl_values else 0,
                "total_return_pct": round(sum(pnl_values), 2),
                "avg_return_pct": round(sum(pnl_values) / len(pnl_values), 2) if pnl_values else 0,
            }
        
        return stats
    
    @staticmethod
    def _calculate_max_drawdown(pnl_values: List[float]) -> float:
        """Calculate maximum drawdown from PnL values."""
        if not pnl_values:
            return 0.0
        
        cumulative = [pnl_values[0]]
        for i in range(1, len(pnl_values)):
            cumulative.append(cumulative[-1] + pnl_values[i])
        
        running_max = [cumulative[0]]
        for i in range(1, len(cumulative)):
            running_max.append(max(running_max[-1], cumulative[i]))
        
        drawdowns = [0]
        for i in range(len(cumulative)):
            drawdowns.append(cumulative[i] - running_max[i])
        
        return min(drawdowns)
    
    @staticmethod
    def _max_consecutive_wins(trades: List[TradeEntry]) -> int:
        """Calculate maximum consecutive winning trades."""
        if not trades:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for trade in trades:
            if trade.exit and trade.exit.get('pnl_percent', 0) > 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    @staticmethod
    def _max_consecutive_losses(trades: List[TradeEntry]) -> int:
        """Calculate maximum consecutive losing trades."""
        if not trades:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for trade in trades:
            if trade.exit and trade.exit.get('pnl_percent', 0) < 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    @staticmethod
    def _empty_metrics() -> Dict[str, Any]:
        """Return empty metrics dictionary."""
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "breakeven_trades": 0,
            "win_rate_pct": 0,
            "loss_rate_pct": 0,
            "avg_win_pct": 0,
            "avg_loss_pct": 0,
            "gross_profits_pct": 0,
            "gross_losses_pct": 0,
            "profit_factor": 0,
            "expectancy_pct": 0,
            "max_drawdown_pct": 0,
            "total_return_pct": 0,
            "largest_win_pct": 0,
            "largest_loss_pct": 0,
            "consecutive_wins": 0,
            "consecutive_losses": 0,
        }
