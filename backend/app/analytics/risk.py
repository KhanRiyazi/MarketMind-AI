"""Risk statistics and position sizing."""
import numpy as np
import pandas as pd


def volatility(returns: pd.Series, periods: int = 252) -> float:
    return float(returns.std() * np.sqrt(periods))


def sharpe(returns: pd.Series, rf: float = 0.065, periods: int = 252) -> float:
    vol = volatility(returns, periods)
    if vol == 0 or np.isnan(vol):
        return 0.0
    return float((returns.mean() * periods - rf) / vol)


def max_drawdown(prices: pd.Series) -> float:
    return float((prices / prices.cummax() - 1).min())


def var_historical(returns: pd.Series, level: float = 0.95) -> float:
    return float(np.percentile(returns.dropna(), (1 - level) * 100))


def beta(returns: pd.Series, benchmark: pd.Series) -> float:
    df = pd.concat([returns, benchmark], axis=1).dropna()
    var = df.iloc[:, 1].var()
    return float(df.iloc[:, 0].cov(df.iloc[:, 1]) / var) if var else 0.0


def position_size(capital: float, risk_pct: float, entry: float, stop: float) -> int:
    """Shares such that hitting the stop loses at most risk_pct of capital."""
    per_share = abs(entry - stop)
    if per_share == 0:
        return 0
    qty = int((capital * risk_pct / 100) / per_share)
    return max(0, min(qty, int(capital // entry)))
