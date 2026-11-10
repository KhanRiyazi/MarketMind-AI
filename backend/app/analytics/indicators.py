"""Technical indicators. All functions are pure and operate on pandas objects."""
import numpy as np
import pandas as pd


def sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n).mean()


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def rsi(s: pd.Series, n: int = 14) -> pd.Series:
    d = s.diff()
    gain = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    loss = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(100.0)


def macd(s: pd.Series, fast=12, slow=26, signal=9) -> pd.DataFrame:
    line = ema(s, fast) - ema(s, slow)
    sig = line.ewm(span=signal, adjust=False).mean()
    return pd.DataFrame({"macd": line, "signal": sig, "hist": line - sig})


def bollinger(s: pd.Series, n: int = 20, k: float = 2.0) -> pd.DataFrame:
    mid, sd = sma(s, n), s.rolling(n).std()
    return pd.DataFrame({"bb_mid": mid, "bb_up": mid + k * sd, "bb_low": mid - k * sd})


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    pc = df["close"].shift(1)
    tr = pd.concat([df["high"] - df["low"], (df["high"] - pc).abs(), (df["low"] - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def vwap(df: pd.DataFrame) -> pd.Series:
    """Session VWAP, reset each calendar day."""
    tp = (df["high"] + df["low"] + df["close"]) / 3
    day = pd.Series(df.index.date, index=df.index)
    pv = (tp * df["volume"]).groupby(day).cumsum()
    vv = df["volume"].groupby(day).cumsum().replace(0, np.nan)
    return (pv / vv).fillna(df["close"])


def pivots(high: float, low: float, close: float) -> dict:
    p = (high + low + close) / 3
    return {"pivot": p, "r1": 2 * p - low, "s1": 2 * p - high,
            "r2": p + (high - low), "s2": p - (high - low)}


def add_all(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ema9"], out["ema21"] = ema(out["close"], 9), ema(out["close"], 21)
    out["rsi"] = rsi(out["close"])
    out = out.join(macd(out["close"])).join(bollinger(out["close"]))
    out["atr"] = atr(out)
    out["vwap"] = vwap(out)
    return out
