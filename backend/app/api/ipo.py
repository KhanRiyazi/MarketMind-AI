from fastapi import APIRouter
from app.agents.ipo_agent import IPOAgent
from app.data.collectors import ipo_collector
from app.database.models import save_analysis
from app.schemas.analysis import IPORequest

router = APIRouter(prefix="/api/ipo", tags=["ipo"])
agent = IPOAgent()


@router.get("/upcoming")
def upcoming():
    return {"ipos": ipo_collector.fetch_ipos()}


@router.post("/analyze")
def analyze(req: IPORequest):
    out = agent.analyze(**req.model_dump())
    save_analysis("ipo", req.name, out)
    return out
