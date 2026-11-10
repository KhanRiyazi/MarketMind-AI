from app.agents import BaseAgent
from app.analytics import valuation


class IPOAgent(BaseAgent):
    name = "ipo"
    role = "You are an IPO analyst."

    def analyze(self, name, price_high, lot_size, eps, peer_pe, gmp=0.0, subscription_x=0.0) -> dict:
        fair = valuation.ipo_fair_value(eps, peer_pe) if eps > 0 else 0.0
        upside = fair / price_high - 1 if fair else -1.0
        gmp_pct = gmp / price_high
        issue_pe = price_high / eps if eps > 0 else None

        score = 0
        score += 2 if upside > 0.15 else 1 if upside > 0 else -2
        score += 2 if gmp_pct > 0.15 else 1 if gmp_pct > 0.05 else 0 if gmp_pct >= 0 else -1
        score += 2 if subscription_x >= 20 else 1 if subscription_x >= 5 else 0 if subscription_x >= 1 else -2
        if eps <= 0:
            score -= 2
        verdict = "Apply" if score >= 4 else "Neutral" if score >= 1 else "Avoid"

        metrics = {"fair_value": round(fair, 2), "upside_pct": round(upside * 100, 1) if fair else None,
                   "issue_pe": round(issue_pe, 1) if issue_pe else None, "gmp_pct": round(gmp_pct * 100, 1),
                   "est_listing_price": round(price_high + gmp, 2), "application_amount": round(price_high * lot_size, 2),
                   "score": score}
        fallback = (f"{name}: priced at {f'{issue_pe:.1f}x earnings' if issue_pe else 'a loss-making basis'} against a peer multiple of {peer_pe:.0f}x. "
                    f"Peer-based value is about {fair:,.0f} versus a {price_high:,.0f} issue price, and the grey market implies {gmp_pct:.0%}. "
                    "Grey market premiums are unofficial and can vanish before listing.")
        return self.finish(verdict, metrics, fallback)
