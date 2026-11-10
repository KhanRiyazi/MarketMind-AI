"""Facade: collect -> clean -> validate, with a small in-memory TTL cache."""
import time
import pandas as pd
from app.config import settings
from app.data.collectors import price_collector, mf_collector
from app.data.validators.validators import validate_symbol, validate_interval, validate_ohlcv
from app.data.processors.processors import clean_ohlcv, nav_to_series

_cache: dict = {}


def _cached(key, fn):
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < settings.cache_ttl_seconds:
        return hit[1]
    val = fn()
    _cache[key] = (time.time(), val)
    return val


def history(symbol: str, period="1y", interval="1d", min_rows=30) -> pd.DataFrame:
    symbol, interval = validate_symbol(symbol), validate_interval(interval)
    raw = _cached(("h", symbol, period, interval), lambda: price_collector.fetch_history(symbol, period, interval))
    validate_ohlcv(raw.rename(columns=str.lower), 1)  # raises a clear error on empty/malformed data
    return validate_ohlcv(clean_ohlcv(raw), min_rows)


def quote(symbol: str) -> dict:
    df = history(symbol, period="5d", interval="1d", min_rows=2)
    last, prev = float(df["close"].iloc[-1]), float(df["close"].iloc[-2])
    return {"symbol": validate_symbol(symbol), "price": round(last, 2),
            "change": round(last - prev, 2), "change_pct": round((last / prev - 1) * 100, 2)}


def indices() -> list[dict]:
    out = []
    for name, sym in price_collector.INDICES.items():
        try:
            out.append({"name": name, **quote(sym)})
        except Exception as e:  # one failing index must not break the page
            out.append({"name": name, "symbol": sym, "error": str(e)})
    return out


def nav_series(scheme_code) -> tuple[str, pd.Series]:
    payload = _cached(("nav", str(scheme_code)), lambda: mf_collector.fetch_nav(scheme_code))
    s = nav_to_series(payload)
    if len(s) < 60:
        raise ValueError("Not enough NAV history for this scheme.")
    return payload.get("meta", {}).get("scheme_name", str(scheme_code)), s
