tep 3: Make sure Actions is enabled
Go to Settings → Actions → General.
Under “Actions permissions”, choose Allow all actions and reusable workflows, then click Save.
Step 4: Run the workflow
Open the Actions tab.
In the left sidebar, click deploy-pages. It only appears there once the file exists on main.
Click the Run workflow dropdown on the right, keep branch main, and click the green Run workflow button.
Wait about a minute until the run shows a green check.

If the run fails, click it, open the failed step, and send me the error text.


cd C:\Users\Dell\Desktop\MarketMind-AI\frontend
python -m http.server 5500

uvicorn app.main:app --reload

# MarketMind-AI

Four analysis agents for Indian retail investors, behind a FastAPI backend and a plain HTML/JS dashboard.

| Agent | What it does |
|---|---|
| Intraday | Scores VWAP, EMA, MACD and RSI, then proposes entry, stop, targets and a position size that caps loss at your risk % |
| SIP | Projects a SIP (with step-up and inflation), solves the monthly amount for a goal, back-tests a real fund's NAV history with XIRR |
| Mutual fund | CAGR, volatility, Sharpe, max drawdown and a 0-100 score from live NAVs (mfapi.in) |
| IPO | Peer-multiple fair value, grey market premium and subscription into a verdict |

**How the agents work:** numbers come only from the deterministic code in `analytics/`. If `ANTHROPIC_API_KEY` is set, Claude rewrites the computed facts as a short explanation. Without a key, or if the call fails, a templated explanation is used. The analysis never depends on the LLM.

## Run it
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
cd backend && uvicorn app.main:app --reload          # http://localhost:8000/docs

# second terminal
cd frontend && python -m http.server 5500             # http://localhost:5500
```
Run tests from the repo root: `python -m pytest tests -q` (offline, no API keys needed).

## Deploy
- **Frontend:** push to `main`; `deploy-pages.yml` publishes `frontend/` to GitHub Pages (enable Pages > Source: GitHub Actions). Enter your backend URL in the sidebar field.
- **Backend:** any host that runs `uvicorn app.main:app` (Render, Railway, Fly.io). Add your Pages URL to `CORS_ORIGINS`.
- **Google Sheets logging (optional):** see `google_workspace/spreadsheet_schema.md`.

## Known limits
- Stock prices come from Yahoo Finance via `yfinance`: delayed, unofficial and occasionally broken. Swap in a licensed feed in `data/collectors/price_collector.py`.
- Intraday bars outside market hours (NSE: 9:15-15:30 IST) are stale.
- IPO data is sample data until you set `IPO_SHEET_CSV_URL`. Grey market premiums are unofficial.
- The signals are simple rules, not a proven edge. Back-test before risking money.

Educational analysis, not investment advice. Markets carry risk of loss.
