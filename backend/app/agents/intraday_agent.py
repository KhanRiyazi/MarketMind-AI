import pandas as pd
from app.agents import BaseAgent
from app.analytics import indicators as ind, risk
from app.data.processors.processors import to_records
from app.integrations import market_data


class IntradayAgent(BaseAgent):
    name = "intraday"
    role = "You are an intraday equity analyst."

    def analyze(self, symbol, interval="5m", period="5d", capital=100_000, risk_pct=1.0) -> dict:
        df = market_data.history(symbol, period=period, interval=interval)
        return self.analyze_frame(symbol, df, capital, risk_pct)

    def analyze_frame(self, symbol, df: pd.DataFrame, capital=100_000, risk_pct=1.0) -> dict:
        d = ind.add_all(df)
        last = d.iloc[-1]
        price, a = float(last["close"]), float(last["atr"])

        score, reasons = 0, []

        def vote(points, text):
            nonlocal score
            score += points
            reasons.append(text)

        vote(1 if price > last["vwap"] else -1, "Price above VWAP" if price > last["vwap"] else "Price below VWAP")
        vote(1 if last["ema9"] > last["ema21"] else -1, "EMA9 above EMA21" if last["ema9"] > last["ema21"] else "EMA9 below EMA21")
        vote(1 if last["hist"] > 0 else -1, "MACD histogram positive" if last["hist"] > 0 else "MACD histogram negative")
        if last["rsi"] > 70:
            vote(-1, f"RSI {last['rsi']:.0f}: overbought, chase risk")
        elif last["rsi"] < 30:
            vote(1, f"RSI {last['rsi']:.0f}: oversold, bounce possible")
        else:
            reasons.append(f"RSI {last['rsi']:.0f}: neutral zone")

        bias = "Bullish" if score >= 2 else "Bearish" if score <= -2 else "Neutral"

        plan = None
        if bias != "Neutral" and a > 0:
            sign = 1 if bias == "Bullish" else -1
            stop = price - sign * 1.5 * a
            r = abs(price - stop)
            plan = {"side": "BUY" if sign == 1 else "SELL", "entry": round(price, 2), "stop": round(stop, 2),
                    "target1": round(price + sign * 1.5 * r, 2), "target2": round(price + sign * 2.5 * r, 2),
                    "quantity": risk.position_size(capital, risk_pct, price, stop),
                    "max_loss": round(capital * risk_pct / 100, 2)}

        days = sorted(set(d.index.date))
        levels = None
        if len(days) >= 2:
            prev = d[[x == days[-2] for x in d.index.date]]
            levels = {k: round(v, 2) for k, v in ind.pivots(prev["high"].max(), prev["low"].min(), prev["close"].iloc[-1]).items()}

        metrics = {"price": round(price, 2), "vwap": round(float(last["vwap"]), 2), "rsi": round(float(last["rsi"]), 1),
                   "atr": round(a, 2), "score": score, "reasons": reasons}
        fallback = (f"{symbol.upper()} reads {bias.lower()} (score {score:+d}): " + "; ".join(reasons[:3]) + ". "
                    + (f"Stop sits {abs(price - plan['stop']):.2f} away, sized to risk {risk_pct}% of capital."
                       if plan else "Signals conflict, so no trade is suggested."))
        return self.finish(bias, metrics, fallback, plan=plan, levels=levels,
                           chart=to_records(d.tail(120)[["close", "vwap", "ema9", "ema21"]]))
