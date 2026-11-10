"""Mutual fund NAV data from the free mfapi.in service."""
import requests

BASE = "https://api.mfapi.in/mf"


def search_schemes(query: str, limit: int = 15) -> list[dict]:
    r = requests.get(f"{BASE}/search", params={"q": query}, timeout=15)
    r.raise_for_status()
    return r.json()[:limit]


def fetch_nav(scheme_code: int | str) -> dict:
    r = requests.get(f"{BASE}/{scheme_code}", timeout=30)
    r.raise_for_status()
    return r.json()
