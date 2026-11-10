from datetime import date
import pytest
from app.analytics.returns import cagr, xirr


def test_cagr_doubling_in_six_years():
    assert cagr(100, 200, 6) == pytest.approx(0.1225, abs=1e-3)


def test_cagr_rejects_bad_input():
    with pytest.raises(ValueError):
        cagr(0, 10, 1)


def test_xirr_ten_percent():
    r = xirr([(date(2023, 1, 1), -1000), (date(2024, 1, 1), 1100)])
    assert r == pytest.approx(0.10, abs=1e-3)


def test_xirr_needs_both_signs():
    assert xirr([(date(2023, 1, 1), -1000), (date(2024, 1, 1), -5)]) is None
