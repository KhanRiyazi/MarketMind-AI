"""Upload JSON reports to Google Drive using a service account (optional dependency)."""
import io
import json
from app.config import settings


def upload_json(name: str, payload: dict) -> str | None:
    if not (settings.google_service_account_json and settings.drive_folder_id):
        return None
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    creds = Credentials.from_service_account_file(
        settings.google_service_account_json, scopes=["https://www.googleapis.com/auth/drive.file"])
    drive = build("drive", "v3", credentials=creds)
    media = MediaIoBaseUpload(io.BytesIO(json.dumps(payload, indent=2).encode()), mimetype="application/json")
    f = drive.files().create(body={"name": name, "parents": [settings.drive_folder_id]},
                             media_body=media, fields="id").execute()
    return f["id"]
