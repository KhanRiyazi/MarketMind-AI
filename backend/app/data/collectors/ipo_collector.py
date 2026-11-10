"""IPO calendar. Reads a published Google Sheet CSV if configured, else sample data.

SAMPLE_IPOS values are illustrative. Point IPO_SHEET_CSV_URL at a real feed before relying on it.
"""
import csv
import io
import requests
from app.config import settings

SAMPLE_IPOS = [
    {"name": "Sample Retail Ltd", "price_high": 480, "lot_size": 31, "eps": 18.0, "peer_pe": 32, "gmp": 60, "subscription_x": 14.2, "open": "TBD"},
    {"name": "Sample Infra Ltd", "price_high": 310, "lot_size": 48, "eps": 9.5, "peer_pe": 24, "gmp": 5, "subscription_x": 2.1, "open": "TBD"},
    {"name": "Sample Tech Ltd", "price_high": 920, "lot_size": 16, "eps": 21.0, "peer_pe": 38, "gmp": 110, "subscription_x": 48.0, "open": "TBD"},
]


def fetch_ipos() -> list[dict]:
    if not settings.ipo_sheet_csv_url:
        return SAMPLE_IPOS
    r = requests.get(settings.ipo_sheet_csv_url, timeout=15)
    r.raise_for_status()
    rows = []
    for row in csv.DictReader(io.StringIO(r.text)):
        for k in ("price_high", "lot_size", "eps", "peer_pe", "gmp", "subscription_x"):
            row[k] = float(row.get(k) or 0)
        rows.append(row)
    return rows
