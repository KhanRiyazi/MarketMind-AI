"""Log analyses to Google Sheets through the Apps Script web app (see google_workspace/)."""
import requests
from app.config import settings


def append_row(sheet: str, row: list) -> bool:
    if not settings.apps_script_url:
        return False
    r = requests.post(settings.apps_script_url,
                      json={"token": settings.apps_script_token, "sheet": sheet, "row": row}, timeout=15)
    return r.ok and r.json().get("ok", False)


def read_rows(sheet: str, limit: int = 50) -> list[list]:
    if not settings.apps_script_url:
        return []
    r = requests.get(settings.apps_script_url,
                     params={"token": settings.apps_script_token, "sheet": sheet, "limit": limit}, timeout=15)
    r.raise_for_status()
    return r.json().get("rows", [])
