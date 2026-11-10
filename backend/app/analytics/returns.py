"""Return maths: CAGR, XIRR, SIP projections and back-tests."""
from datetime import date
import pandas as pd


def cagr(start: float, end: float, years: float) -> float:
    if start <= 0 or years <= 0:
        raise ValueError("start and years must be positive")
    return (end / start) ** (1 / years) - 1


def xirr(flows: list[tuple[date, float]], lo=-0.99, hi=10.0) -> float | None:
    """Annualised IRR for dated cash flows (bisection; robust, no scipy)."""
    if len(flows) < 2 or not (any(a < 0 for _, a in flows) and any(a > 0 for _, a in flows)):
        return None
    t0 = min(d for d, _ in flows)

    def npv(r):
        return sum(a / (1 + r) ** ((d - t0).days / 365.0) for d, a in flows)

    f_lo, f_hi = npv(lo), npv(hi)
    if f_lo * f_hi > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = npv(mid)
        if abs(f_mid) < 1e-7:
            return mid
        if f_lo * f_mid < 0:
            hi = mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2


def sip_projection(monthly: float, years: int, annual_return: float,
                   step_up: float = 0.0, inflation: float = 0.06) -> dict:
    """Month-start contributions, monthly compounding, optional yearly step-up."""
    r = (1 + annual_return) ** (1 / 12) - 1
    value = invested = 0.0
    amount = monthly
    series = []
    for m in range(1, years * 12 + 1):
        value = (value + amount) * (1 + r)
        invested += amount
        if m % 12 == 0:
            series.append({"year": m // 12, "invested": round(invested, 2), "value": round(value, 2)})
            amount *= 1 + step_up
    real = value / (1 + inflation) ** years
    return {"invested": round(invested, 2), "value": round(value, 2), "gain": round(value - invested, 2),
            "real_value": round(real, 2), "series": series}


def required_sip(target: float, years: int, annual_return: float, step_up: float = 0.0) -> float:
    unit = sip_projection(1.0, years, annual_return, step_up)["value"]
    return round(target / unit, 2)


def sip_backtest(nav: pd.Series, monthly: float, years: int) -> dict:
    """Buy on the first NAV of each month for `years`, value at the latest NAV."""
    nav = nav.sort_index()
    nav = nav[nav.index >= nav.index[-1] - pd.DateOffset(years=years)]
    firsts = nav.groupby([nav.index.year, nav.index.month]).head(1)
    units = monthly / firsts
    flows = [(d.date(), -monthly) for d in firsts.index]
    final_value = float(units.sum() * nav.iloc[-1])
    flows.append((nav.index[-1].date(), final_value))
    invested = monthly * len(firsts)
    lump_units = invested / float(nav.iloc[0])
    return {"installments": len(firsts), "invested": round(invested, 2), "value": round(final_value, 2),
            "xirr": xirr(flows), "lumpsum_value": round(lump_units * float(nav.iloc[-1]), 2),
            "series": [{"date": d.strftime("%Y-%m-%d"),
                        "invested": monthly * (i + 1),
                        "value": round(float(units.iloc[: i + 1].sum() * nav.loc[d]), 2)}
                       for i, d in enumerate(firsts.index)]}
