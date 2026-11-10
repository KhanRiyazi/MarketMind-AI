import pandas as pd
import pytest
from app.data.processors.processors import clean_ohlcv, nav_to_series, to_records
from app.data.validators.validators import validate_interval, validate_ohlcv, validate_symbol


def test_symbol_rules():
    assert validate_symbol("reliance") == "RELIANCE"
    assert validate_symbol("M&M") == "M&M"
    for bad in ("", "a b", "x;drop", "A" * 40):
        with pytest.raises(ValueError):
            validate_symbol(bad)


def test_interval_rules():
    assert validate_interval("5m") == "5m"
    with pytest.raises(ValueError):
        validate_interval("2h")


def test_ohlcv_rejects_empty_short_and_corrupt():
    with pytest.raises(ValueError):
        validate_ohlcv(pd.DataFrame())
    df = pd.DataFrame({"open": [1] * 40, "high": [2.0] * 40, "low": [1.0] * 40, "close": [1.5] * 40, "volume": [1] * 40})
    assert validate_ohlcv(df) is df
    with pytest.raises(ValueError):
        validate_ohlcv(df.head(5))
    df.loc[3, "high"] = 0.5
    with pytest.raises(ValueError):
        validate_ohlcv(df)


def test_clean_and_json_safety():
    idx = pd.to_datetime(["2024-01-02", "2024-01-01", "2024-01-01"])
    raw = pd.DataFrame({"Open": [1, 2, 3], "High": [2, 3, 4], "Low": [1, 1, 1], "Close": [1, None, 3], "Volume": [5, 6, None]}, index=idx)
    out = clean_ohlcv(raw)
    assert out.index.is_monotonic_increasing and out.index.is_unique
    rec = to_records(out.assign(x=float("nan")))
    assert rec[0]["x"] is None and "index" in rec[0]


def test_nav_parsing():
    s = nav_to_series({"data": [{"date": "02-01-2024", "nav": "11.5"}, {"date": "01-01-2024", "nav": "11.0"}]})
    assert list(s.values) == [11.0, 11.5]
