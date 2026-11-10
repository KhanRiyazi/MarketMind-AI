"""Agents: each one gathers data, runs deterministic analytics, then narrates the result.

The numbers always come from the analytics layer. The LLM (if configured) only explains
them in plain language, so a missing API key or an LLM failure never changes the analysis.
"""
import json
from app.config import settings

DISCLAIMER = "Educational analysis, not investment advice. Markets carry risk of loss."


class BaseAgent:
    name = "base"
    role = "You are a careful market analyst."

    def narrate(self, facts: dict, fallback: str) -> str:
        if not settings.anthropic_api_key:
            return fallback
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            msg = client.messages.create(
                model=settings.anthropic_model, max_tokens=400,
                system=(f"{self.role} Explain the computed facts in under 120 words, plain English, "
                        "for an Indian retail investor. Use only the numbers given. Never promise returns. "
                        "Mention the main risk."),
                messages=[{"role": "user", "content": json.dumps(facts, default=str)}])
            return "".join(b.text for b in msg.content if b.type == "text").strip() or fallback
        except Exception:
            return fallback

    def finish(self, verdict: str, metrics: dict, fallback: str, **extra) -> dict:
        facts = {"verdict": verdict, **metrics}
        return {"agent": self.name, "verdict": verdict, "summary": self.narrate(facts, fallback),
                "metrics": metrics, "disclaimer": DISCLAIMER, **extra}
