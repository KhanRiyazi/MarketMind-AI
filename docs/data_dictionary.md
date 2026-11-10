# Data dictionary

| Field | Meaning |
|---|---|
| vwap | Volume-weighted average price, reset each day |
| atr | 14-bar average true range (volatility in price units) |
| rsi | 14-bar relative strength index, 0-100 |
| score (intraday) | Sum of signal votes, -4 to +4. At or above +2 Bullish, at or below -2 Bearish |
| cagr_Ny | Compound annual growth rate of NAV over N years (decimal) |
| volatility | Annualised standard deviation of daily returns |
| sharpe | (annual return - risk-free rate) / volatility; risk-free default 6.5% |
| max_drawdown | Worst peak-to-trough fall (negative decimal) |
| score (fund) | 0-100 blend of Sharpe, 3-year CAGR and drawdown |
| xirr | Annualised return of dated SIP cash flows |
| real_value | SIP value discounted by inflation |
| fair_value (IPO) | EPS x peer P/E x (1 - 15% IPO discount) |
| gmp_pct | Grey market premium as a share of the upper price band |
| score (IPO) | Sum of valuation, GMP and subscription points; 4+ Apply, 1-3 Neutral, below 1 Avoid |

Database tables: `analysis_logs(kind, subject, payload, created_at)`, `watchlist(symbol)`.
