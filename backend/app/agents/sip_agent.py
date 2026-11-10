from app.agents import BaseAgent
from app.analytics import returns
from app.integrations import market_data


class SIPAgent(BaseAgent):
    name = "sip"
    role = "You are a SIP and goal-planning advisor."

    def project(self, monthly, years, annual_return, step_up=0.0, inflation=0.06) -> dict:
        p = returns.sip_projection(monthly, years, annual_return, step_up, inflation)
        mult = p["value"] / p["invested"]
        verdict = "Realistic" if annual_return <= 0.12 else "Optimistic" if annual_return <= 0.15 else "Aggressive assumption"
        metrics = {k: p[k] for k in ("invested", "value", "gain", "real_value")} | {"multiple": round(mult, 2)}
        fallback = (f"Investing {monthly:,.0f} a month for {years} years at {annual_return:.0%} grows {p['invested']:,.0f} "
                    f"to about {p['value']:,.0f}. After {inflation:.0%} inflation that is worth roughly {p['real_value']:,.0f} today. "
                    "Actual returns will vary year to year.")
        return self.finish(verdict, metrics, fallback, series=p["series"])

    def goal(self, target, years, annual_return, step_up=0.0) -> dict:
        sip = returns.required_sip(target, years, annual_return, step_up)
        return self.finish("Plan", {"required_monthly": sip, "target": target, "years": years},
                           f"To reach {target:,.0f} in {years} years at {annual_return:.0%} you need about {sip:,.0f} a month"
                           + (f", rising {step_up:.0%} each year." if step_up else "."))

    def backtest(self, scheme_code, monthly, years) -> dict:
        name, nav = market_data.nav_series(scheme_code)
        bt = returns.sip_backtest(nav, monthly, years)
        x = bt["xirr"]
        verdict = "Beat lump sum" if bt["value"] > bt["lumpsum_value"] else "Lagged lump sum"
        metrics = {k: bt[k] for k in ("installments", "invested", "value", "xirr", "lumpsum_value")}
        fallback = (f"{name}: {bt['installments']} monthly installments of {monthly:,.0f} became {bt['value']:,.0f}"
                    + (f" (XIRR {x:.1%})." if x is not None else ".") + " Past performance does not predict future returns.")
        return self.finish(verdict, metrics, fallback, scheme=name, series=bt["series"])
