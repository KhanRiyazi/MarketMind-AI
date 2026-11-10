# API

Interactive docs at `/docs` when the server runs. All errors return `{"detail": "..."}` (400 bad input, 422 schema error).

| Method | Path | Notes |
|---|---|---|
| GET | `/health` | `{status, llm}` |
| GET | `/api/market/overview` | NIFTY 50, SENSEX, BANK NIFTY, NIFTY IT |
| GET | `/api/market/quote/{symbol}` | `RELIANCE` auto-maps to `RELIANCE.NS` |
| GET | `/api/market/history/{symbol}?period=6mo&interval=1d` | close, 50/200-day averages |
| GET | `/api/intraday/{symbol}?interval=5m&period=5d&capital=100000&risk_pct=1` | verdict, plan, levels, chart |
| POST | `/api/sip/projection` | `{monthly, years, annual_return, step_up, inflation}`; rates as decimals (0.12) |
| POST | `/api/sip/goal` | `{target, years, annual_return, step_up}` |
| POST | `/api/sip/backtest` | `{scheme_code, monthly, years}` |
| GET | `/api/mutual-funds/search?q=` | up to 15 schemes |
| GET | `/api/mutual-funds/{code}/analysis` | score, CAGR, risk, NAV chart |
| GET | `/api/ipo/upcoming` | sample or sheet-backed |
| POST | `/api/ipo/analyze` | `{name, price_high, lot_size, eps, peer_pe, gmp, subscription_x}` |

Agent responses share one shape: `{agent, verdict, summary, metrics, disclaimer, ...extras}`.
