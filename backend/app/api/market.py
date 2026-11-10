from fastapi import APIRouter, HTTPException
from app.analytics import indicators as ind
from app.data.processors.processors import to_records
from app.integrations import market_data

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/overview")
def overview():
    return {"indices": market_data.indices()}


@router.get("/quote/{symbol}")
def get_quote(symbol: str):
    try:
        return market_data.quote(symbol)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/history/{symbol}")
def get_history(symbol: str, period: str = "2y", interval: str = "1d", show: int = 125):
    try:
        df = market_data.history(symbol, period, interval)
    except ValueError as e:
        raise HTTPException(400, str(e))
    df = df.assign(sma50=ind.sma(df["close"], 50), sma200=ind.sma(df["close"], 200)).tail(show)
    return {"symbol": symbol.upper(), "candles": to_records(df[["close", "sma50", "sma200"]])}
