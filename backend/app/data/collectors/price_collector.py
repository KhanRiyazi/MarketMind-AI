"""Price data collection via yfinance (imported lazily so tests run offline)."""
import pandas as pd

INDICES = {"NIFTY 50": "^NSEI", "SENSEX": "^BSESN", "BANK NIFTY": "^NSEBANK", "NIFTY IT": "^CNXIT"}


def normalise_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    return s if s.startswith("^") or "." in s else f"{s}.NS"


def fetch_history(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    import yfinance as yf
    return yf.Ticker(normalise_symbol(symbol)).history(period=period, interval=interval, auto_adjust=False)
