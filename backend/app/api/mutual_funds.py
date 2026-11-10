import requests
from fastapi import APIRouter, HTTPException, Query
from app.agents.mutual_fund_agent import MutualFundAgent
from app.data.collectors import mf_collector
from app.database.models import save_analysis

router = APIRouter(prefix="/api/mutual-funds", tags=["mutual-funds"])
agent = MutualFundAgent()


@router.get("/search")
def search(q: str = Query(min_length=2, max_length=60)):
    try:
        results = mf_collector.search_schemes(q, limit=60)
    except requests.RequestException:
        raise HTTPException(502, "Fund data service is unreachable. Try again in a moment.")
    # IDCW payout plans pay out cash, which lowers NAV and makes NAV-based returns misleading.
    growth = [r for r in results if "growth" in r.get("schemeName", "").lower()]
    return {"results": (growth or results)[:15]}


@router.get("/{scheme_code}/analysis")
def analysis(scheme_code: int):
    try:
        out = agent.analyze(scheme_code)
    except requests.RequestException:
        raise HTTPException(502, "Fund data service is unreachable. Try again in a moment.")
    except ValueError as e:
        raise HTTPException(400, str(e))
    save_analysis("mutual_fund", str(scheme_code), {k: v for k, v in out.items() if k != "chart"})
    return out
