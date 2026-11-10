import numpy as np
import pandas as pd
from app.analytics import indicators as ind, risk


def frame(n=120, seed=1):
    rng = np.random.default_rng(seed)
    close = 100 + rng.normal(0, 1, n).cumsum()
    idx = pd.date_range("2024-01-01 09:15", periods=n, freq="5min")
    return pd.DataFrame({"open": close, "high": close + 1, "low": close - 1, "close": close,
                         "volume": rng.integers(1000, 5000, n)}, index=idx)


def test_sma_known_values():
    assert ind.sma(pd.Series([1, 2, 3, 4, 5]), 3).iloc[-1] == 4


def test_rsi_bounds_and_uptrend():
    up = pd.Series(np.arange(1, 60, dtype=float))
    r = ind.rsi(up)
    assert r.between(0, 100).all() and r.iloc[-1] > 90


def test_add_all_columns():
    out = ind.add_all(frame())
    for c in ("ema9", "rsi", "macd", "bb_up", "atr", "vwap"):
        assert c in out.columns
    assert out["atr"].iloc[-1] > 0


def test_position_size_respects_risk():
    qty = risk.position_size(100_000, 1, entry=500, stop=490)
    assert qty == 100 and qty * 10 <= 1000


def test_max_drawdown():
    assert risk.max_drawdown(pd.Series([100, 120, 90, 110])) == -0.25


def test_intraday_agent_on_synthetic_data():
    from app.agents.intraday_agent import IntradayAgent
    r = IntradayAgent().analyze_frame("TEST", frame(), capital=100_000, risk_pct=1)
    assert r["verdict"] in {"Bullish", "Bearish", "Neutral"} and r["summary"]
    assert len(r["chart"]) == 100 or len(r["chart"]) == 120
