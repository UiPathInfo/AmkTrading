from typing import Optional, List
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Robustly load `run_screener` from the screener file.
import importlib.util
import sys
import os


def _load_run_screener():
    """Attempt multiple ways to import `run_screener`:
    1. `backend.MyScreener` (when importable as package)
    2. `MyScreener` (simple import)
    3. Load from `backend/MyScreener.py` file path using importlib
    Returns the `run_screener` callable or `None`.
    """
    # 1) Try package import
    try:
        from backend.MyScreener import run_screener as _rs
        return _rs
    except Exception:
        pass

    # 2) Try top-level import
    try:
        from MyScreener import run_screener as _rs
        return _rs
    except Exception:
        pass

    # 3) Load directly from file path
    base = os.path.dirname(__file__)
    path = os.path.join(base, "MyScreener.py")
    if os.path.exists(path):
        try:
            spec = importlib.util.spec_from_file_location("backend._myscreener", path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = mod
            spec.loader.exec_module(mod)  # type: ignore
            return getattr(mod, "run_screener", None)
        except Exception:
            return None

    return None


def _load_run_swing_screener():
    """Attempt multiple ways to import `run_swing_screener`:
    1. `backend.SwingScreener` (when importable as package)
    2. `SwingScreener` (simple import)
    3. Load from `backend/SwingScreener.py` file path using importlib
    Returns the `run_swing_screener` callable or `None`.
    """
    # 1) Try package import
    try:
        from backend.SwingScreener import run_swing_screener as _rs
        return _rs
    except Exception:
        pass

    # 2) Try top-level import
    try:
        from SwingScreener import run_swing_screener as _rs
        return _rs
    except Exception:
        pass

    # 3) Load directly from file path
    base = os.path.dirname(__file__)
    path = os.path.join(base, "SwingScreener.py")
    if os.path.exists(path):
        try:
            spec = importlib.util.spec_from_file_location("backend._swing_screener", path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = mod
            spec.loader.exec_module(mod)  # type: ignore
            return getattr(mod, "run_swing_screener", None)
        except Exception:
            return None

    return None


run_screener = _load_run_screener()
run_swing_screener = _load_run_swing_screener()

app = FastAPI(title="AMK Trading API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None


_items: List[dict] = [{"id": 1, "name": "Sample Item", "description": "This is a sample item."}]
_next_id = 2


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/items")
def list_items():
    return _items


@app.post("/api/items", status_code=201)
def create_item(item: Item):
    global _next_id
    item.id = _next_id
    _next_id += 1
    _items.append(item.dict())
    return item.dict()


@app.get("/api/screener")
def get_screener():
    """Run the stock screener and return the results as JSON."""
    if run_screener is None:
        return {"error": "Screener not available. Ensure backend/MyScreener.py is present and importable."}

    try:
        results = run_screener()
        return {"count": len(results), "results": results}
    except Exception as e:
        return {"error": f"Screener execution failed: {e}"}


@app.get("/api/swing-screener")
def get_swing_screener(limit: int = 10):
    """Run the swing trading screener and return the results as JSON.
    
    Args:
        limit (int): Maximum number of stocks to analyze (default 10)
    """
    if run_swing_screener is None:
        return {"error": "Swing Screener not available. Ensure backend/SwingScreener.py is present and importable."}

    try:
        # Limit to reasonable range
        limit = max(1, min(limit, 50))
        results = run_swing_screener(max_stocks=limit)
        successful = [r for r in results if r.get("status") == "success"]
        failed = [r for r in results if r.get("status") == "error"]
        
        return {
            "total_analyzed": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "results": results
        }
    except Exception as e:
        return {"error": f"Swing screener execution failed: {e}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
