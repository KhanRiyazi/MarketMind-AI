# Spreadsheet schema

One Google Sheet, one tab per agent. `Code.gs` creates missing tabs with these headers on first write.
The backend sends every row without the timestamp; the script prepends it.

| Tab | Columns |
|---|---|
| Intraday | timestamp, symbol, verdict, entry, stop, target1, quantity |
| SIP | timestamp, monthly, years, expected_return, invested, value |
| MutualFunds | timestamp, scheme_code, scheme, verdict, score, cagr_3y |
| IPO | timestamp, name, verdict, fair_value, gmp_pct, score |
| Watchlist | symbol, added_on, note |

## Setup
1. Create the sheet, then Extensions > Apps Script and paste `apps_script/Code.gs`.
2. Project Settings > Script properties: add `TOKEN` with a long random value.
3. Deploy > New deployment > Web app. Execute as *Me*, access *Anyone*. Copy the URL.
4. In `.env`: `GOOGLE_APPS_SCRIPT_URL=<url>` and `GOOGLE_APPS_SCRIPT_TOKEN=<token>`.

## IPO feed (optional)
Add an `IPO_Feed` tab with columns `name, price_high, lot_size, eps, peer_pe, gmp, subscription_x, open`,
use File > Share > Publish to web > CSV, and set `IPO_SHEET_CSV_URL` to that link.
