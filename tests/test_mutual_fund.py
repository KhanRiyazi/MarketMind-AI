import numpy as np
import pandas as pd
import pytest
from app.agents.mutual_fund_agent import MutualFundAgent


def make_nav(crash_years_ago=5, n=2000):
    idx = pd.bdate_range(end="2026-11-01", periods=n)
    rng = np.random.default_rng(3)
    r = rng.normal(0.0005, 0.005, n)
    crash_at = n - int(crash_years_ago * 252)
    r[crash_at:crash_at + 20] = -0.03          # an old crash
    return pd.Series(100 * np.exp(np.cumsum(r)), index=idx)


def test_old_crash_is_excluded_from_3y_risk():
    res = MutualFundAgent().analyze_series("Demo", make_nav(crash_years_ago=5))
    assert abs(res["metrics"]["max_drawdown"]) < 0.25


def test_recent_crash_is_included():
    res = MutualFundAgent().analyze_series("Demo", make_nav(crash_years_ago=1))
    assert abs(res["metrics"]["max_drawdown"]) > 0.30


def test_young_fund_does_not_crash():
    nav = make_nav()[-120:]
    res = MutualFundAgent().analyze_series("New", nav)
    assert res["metrics"]["cagr_3y"] is None and res["verdict"] in {"Strong", "Average", "Weak"}


def test_too_little_history_raises():
    with pytest.raises(ValueError):
        MutualFundAgent().analyze_series("Tiny", make_nav()[-10:])
