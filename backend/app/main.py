from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import intraday, ipo, market, mutual_funds, sip
from app.config import settings
from app.database.connection import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])
for r in (market.router, intraday.router, sip.router, mutual_funds.router, ipo.router):
    app.include_router(r)


@app.get("/health")
def health():
    return {"status": "ok", "llm": bool(settings.anthropic_api_key)}
