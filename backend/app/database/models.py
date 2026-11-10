import json
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Text
from app.database.connection import Base, SessionLocal


class AnalysisLog(Base):
    __tablename__ = "analysis_logs"
    id = Column(Integer, primary_key=True)
    kind = Column(String(20), index=True)
    subject = Column(String(120))
    payload = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Watchlist(Base):
    __tablename__ = "watchlist"
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True)


def save_analysis(kind: str, subject: str, result: dict) -> None:
    """Best-effort audit log; never lets a DB problem break an API response."""
    try:
        with SessionLocal() as db:
            db.add(AnalysisLog(kind=kind, subject=subject, payload=json.dumps(result, default=str)))
            db.commit()
    except Exception:
        pass
