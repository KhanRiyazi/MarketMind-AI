import pandas as pd
import pytest
from app.analytics.returns import required_sip, sip_backtest, sip_projection


def test_zero_return_is_plain_sum():
    p = sip_projection(1000, 5, 0.0)
    assert p["invested"] == p["value"] == 60000


def test_growth_beats_invested():
    p = sip_projection(10000, 15, 0.12)
    assert p["value"] > p["invested"] and len(p["series"]) == 15


def test_step_up_increases_corpus():
    assert sip_projection(10000, 10, 0.12, 0.1)["value"] > sip_projection(10000, 10, 0.12)["value"]


def test_goal_round_trip():
    sip = required_sip(5_000_000, 12, 0.11)
    assert sip_projection(sip, 12, 0.11)["value"] == pytest.approx(5_000_000, rel=1e-3)


def test_backtest_flat_nav_has_no_gain():
    nav = pd.Series(10.0, index=pd.date_range("2021-01-01", periods=900, freq="D"))
    bt = sip_backtest(nav, 1000, 2)
    assert bt["value"] == pytest.approx(bt["invested"], rel=1e-6)
