from fastapi import APIRouter, HTTPException, Query
from app.agents.intraday_agent import IntradayAgent
from app.database.models import save_analysis

router = APIRouter(prefix="/api/intraday", tags=["intraday"])
agent = IntradayAgent()


@router.get("/{symbol}")
def analyze(symbol: str, interval: str = "5m", period: str = "5d",
            capital: float = Query(100_000, gt=0), risk_pct: float = Query(1.0, gt=0, le=5)):
    try:
        result = agent.analyze(symbol, interval, period, capital, risk_pct)
    except ValueError as e:
        raise HTTPException(400, str(e))
    save_analysis("intraday", symbol.upper(), {k: v for k, v in result.items() if k != "chart"})
    return result
