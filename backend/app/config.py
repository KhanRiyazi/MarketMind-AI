import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    app_name = "MarketMind-AI"
    database_url = os.getenv("DATABASE_URL", "sqlite:///./marketmind.db")
    cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500,http://localhost:8080").split(",")]
    cache_ttl_seconds = int(os.getenv("CACHE_TTL_SECONDS", "60"))
    risk_free_rate = float(os.getenv("RISK_FREE_RATE", "0.065"))
    # Optional LLM narration (agents work without it)
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
    # Optional Google Workspace
    apps_script_url = os.getenv("GOOGLE_APPS_SCRIPT_URL", "")
    apps_script_token = os.getenv("GOOGLE_APPS_SCRIPT_TOKEN", "")
    google_service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    drive_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
    ipo_sheet_csv_url = os.getenv("IPO_SHEET_CSV_URL", "")


settings = Settings()
