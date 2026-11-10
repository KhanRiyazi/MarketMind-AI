"""Input and data validation."""
import re
import pandas as pd

REQUIRED = ["open", "high", "low", "close", "volume"]
_SYMBOL = re.compile(r"^[\^A-Za-z0-9&\-\.]{1,20}$")
INTERVALS = {"1m", "5m", "15m", "30m", "60m", "1d"}


def validate_symbol(symbol: str) -> str:
    if not _SYMBOL.match(symbol or ""):
        raise ValueError(f"Invalid symbol: {symbol!r}")
    return symbol.strip().upper()


def validate_interval(interval: str) -> str:
    if interval not in INTERVALS:
        raise ValueError(f"interval must be one of {sorted(INTERVALS)}")
    return interval


def validate_ohlcv(df: pd.DataFrame, min_rows: int = 30) -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError("No price data returned. Check the symbol and market hours.")
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if len(df) < min_rows:
        raise ValueError(f"Need at least {min_rows} bars, got {len(df)}.")
    bad = (df["high"] < df["low"]) | (df["close"] <= 0)
    if bad.any():
        raise ValueError(f"{int(bad.sum())} corrupt bars found (high<low or non-positive close).")
    return df
