from fastapi import APIRouter, HTTPException
from app.agents.sip_agent import SIPAgent
from app.database.models import save_analysis
from app.schemas.portfolio import BacktestRequest, GoalRequest, SIPRequest

router = APIRouter(prefix="/api/sip", tags=["sip"])
agent = SIPAgent()


@router.post("/projection")
def projection(req: SIPRequest):
    out = agent.project(**req.model_dump())
    save_analysis("sip", f"{req.monthly}/m x {req.years}y", {k: v for k, v in out.items() if k != "series"})
    return out


@router.post("/goal")
def goal(req: GoalRequest):
    return agent.goal(**req.model_dump())


@router.post("/backtest")
def backtest(req: BacktestRequest):
    try:
        return agent.backtest(**req.model_dump())
    except ValueError as e:
        raise HTTPException(400, str(e))
