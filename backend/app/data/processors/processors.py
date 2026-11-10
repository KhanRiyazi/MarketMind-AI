"""Data cleaning and JSON-safe conversion."""
import pandas as pd


def clean_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    out = df.rename(columns=str.lower)[["open", "high", "low", "close", "volume"]].copy()
    out = out[~out.index.duplicated(keep="last")].sort_index().dropna(subset=["close"])
    out["volume"] = out["volume"].fillna(0)
    return out


def nav_to_series(payload: dict) -> pd.Series:
    rows = payload.get("data", [])
    s = pd.Series({pd.to_datetime(r["date"], format="%d-%m-%Y"): float(r["nav"]) for r in rows})
    return s.sort_index().astype(float)


def to_records(df: pd.DataFrame, round_to: int = 2) -> list[dict]:
    """DataFrame -> list of dicts with NaN converted to None (valid JSON)."""
    out = df.round(round_to).astype(object).where(pd.notna(df), None).reset_index()
    out.columns = ["index", *out.columns[1:]]
    out.iloc[:, 0] = out.iloc[:, 0].astype(str)
    return out.to_dict("records")
