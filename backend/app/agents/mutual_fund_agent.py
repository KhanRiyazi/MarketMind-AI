import numpy as np
from app.agents import BaseAgent
from app.analytics import returns, risk
from app.config import settings
from app.integrations import market_data


class MutualFundAgent(BaseAgent):
    name = "mutual_fund"
    role = "You are a mutual fund research analyst."

    def analyze(self, scheme_code) -> dict:
        name, nav = market_data.nav_series(scheme_code)
        return self.analyze_series(name, nav)

    def analyze_series(self, name, nav) -> dict:
        end = nav.index[-1]
        rets = nav.pct_change().dropna()
        trailing = {}
        for y in (1, 3, 5):
            past = nav[nav.index <= end - np.timedelta64(365 * y, "D")]
            trailing[f"cagr_{y}y"] = round(returns.cagr(float(past.iloc[-1]), float(nav.iloc[-1]), y), 4) if len(past) else None

        vol, sh = risk.volatility(rets), risk.sharpe(rets, settings.risk_free_rate)
        mdd = risk.max_drawdown(nav)
        base = trailing["cagr_3y"] if trailing["cagr_3y"] is not None else trailing["cagr_1y"]
        score = 50 + 20 * (sh - 0.5) + 50 * ((base or 0) - 0.12) - 40 * (abs(mdd) - 0.20)
        score = int(max(0, min(100, round(score))))
        verdict = "Strong" if score >= 70 else "Average" if score >= 45 else "Weak"

        metrics = {**trailing, "volatility": round(vol, 4), "sharpe": round(sh, 2),
                   "max_drawdown": round(mdd, 4), "score": score, "latest_nav": round(float(nav.iloc[-1]), 4)}
        c3 = trailing["cagr_3y"]
        fallback = (f"{name} scores {score}/100 ({verdict.lower()}). "
                    + (f"3-year CAGR is {c3:.1%}, " if c3 is not None else "Under 3 years of history, ")
                    + f"with {vol:.0%} volatility and a worst fall of {abs(mdd):.0%}. Compare against category peers before deciding.")
        step = max(1, len(nav) // 150)
        chart = [{"date": d.strftime("%Y-%m-%d"), "nav": round(float(v), 4)} for d, v in nav.iloc[::step].items()]
        return self.finish(verdict, metrics, fallback, scheme=name, chart=chart)
