/* Rendering. All API text goes through textContent, so nothing from the network is parsed as HTML. */
const UI = {
  el(tag, props = {}, ...kids) {
    const n = Object.assign(document.createElement(tag), props);
    kids.flat().forEach(k => n.append(k instanceof Node ? k : document.createTextNode(k ?? "")));
    return n;
  },
  inr: v => v == null ? "n/a" : "₹" + Number(v).toLocaleString("en-IN", { maximumFractionDigits: 0 }),
  num: (v, d = 2) => v == null ? "n/a" : Number(v).toLocaleString("en-IN", { maximumFractionDigits: d }),
  pct: (v, d = 1) => v == null ? "n/a" : (v * 100).toFixed(d) + "%",
  tone: v => ["Bullish", "Strong", "Apply", "Beat lump sum", "Realistic"].includes(v) ? "pos"
           : ["Bearish", "Weak", "Avoid", "Lagged lump sum", "Aggressive assumption"].includes(v) ? "neg" : "mid",

  verdict(r) {
    return this.el("div", { className: "verdict " + this.tone(r.verdict) },
      this.el("div", { className: "word" }, r.verdict), this.el("p", {}, r.summary));
  },
  table(title, rows) {
    return this.el("div", { className: "panel" }, this.el("h2", {}, title),
      this.el("table", {}, rows.map(([k, v]) => this.el("tr", {}, this.el("td", {}, k), this.el("td", {}, v)))));
  },
  chartBox(id) { return this.el("div", { className: "panel" }, this.el("div", { className: "chart" }, this.el("canvas", { id }))); },
  show(target, ...nodes) { const t = document.getElementById(target); t.replaceChildren(...nodes); return t; },
  loading(target) { this.show(target, this.el("p", { className: "msg" }, "Working on it...")); },
  error(target, e) { this.show(target, this.el("p", { className: "msg err" }, e.message)); },

  indices(list) {
    const box = document.getElementById("indices");
    box.replaceChildren(...list.map(i => this.el("div", { className: "card" },
      this.el("div", { className: "k" }, i.name),
      i.error ? this.el("div", { className: "k" }, "Unavailable")
        : [this.el("div", { className: "v" }, this.num(i.price)),
           this.el("div", { className: i.change >= 0 ? "up" : "down" },
             (i.change >= 0 ? "+" : "") + this.num(i.change) + " (" + (i.change_pct >= 0 ? "+" : "") + i.change_pct + "%)")])));
  },
  trend(d) {
    this.show("out-market", this.chartBox("c-market"));
    Charts.line("c-market", d.candles.map(c => c.index.slice(0, 10)), [
      { label: d.symbol + " close", data: d.candles.map(c => c.close) },
      { label: "50-day average", data: d.candles.map(c => c.sma50), dash: [5, 4] },
      { label: "200-day average", data: d.candles.map(c => c.sma200), dash: [2, 3] }]);
  },
  intraday(r) {
    const m = r.metrics, p = r.plan, parts = [this.verdict(r)];
    const left = [["Price", this.num(m.price)], ["VWAP", this.num(m.vwap)], ["RSI", m.rsi], ["ATR", this.num(m.atr)], ["Signal score", m.score]];
    const rows = [this.table("Signals", left), this.table("What drove it", m.reasons.map(x => [x, ""]))];
    if (p) rows.push(this.table("Trade plan (" + p.side + ")", [["Entry", this.num(p.entry)], ["Stop", this.num(p.stop)],
      ["Target 1", this.num(p.target1)], ["Target 2", this.num(p.target2)], ["Quantity", p.quantity], ["Maximum loss", this.inr(p.max_loss)]]));
    if (r.levels) rows.push(this.table("Yesterday's levels", Object.entries(r.levels).map(([k, v]) => [k.toUpperCase(), this.num(v)])));
    if (r.as_of) parts.push(this.el("p", { className: "msg" }, "Latest bar: " + r.as_of.replace("T", " ").slice(0, 16)));
    parts.push(this.chartBox("c-intraday"), this.el("div", { className: "two" }, rows));
    this.show("out-intraday", ...parts);
    const fmt = t => { const d = t.replace("T", " "); return d.slice(8, 10) + "/" + d.slice(5, 7) + " " + d.slice(11, 16); };
    Charts.line("c-intraday", r.chart.map(c => fmt(c.index)), [
      { label: "Price", data: r.chart.map(c => c.close) }, { label: "VWAP", data: r.chart.map(c => c.vwap), dash: [5, 4] },
      { label: "EMA 9", data: r.chart.map(c => c.ema9) }, { label: "EMA 21", data: r.chart.map(c => c.ema21) }]);
  },
  sip(proj, goal, bt) {
    const parts = [this.verdict(proj), this.chartBox("c-sip")];
    const rows = [this.table("Projection", [["Invested", this.inr(proj.metrics.invested)], ["Expected value", this.inr(proj.metrics.value)],
      ["Gain", this.inr(proj.metrics.gain)], ["Value in today's money", this.inr(proj.metrics.real_value)], ["Multiple", proj.metrics.multiple + "x"]])];
    if (goal) rows.push(this.table("Goal", [["Needed each month", this.inr(goal.metrics.required_monthly)], ["Target", this.inr(goal.metrics.target)]]));
    if (bt) rows.push(this.table("Back-test: " + bt.scheme, [["Installments", bt.metrics.installments], ["Invested", this.inr(bt.metrics.invested)],
      ["Value now", this.inr(bt.metrics.value)], ["XIRR", this.pct(bt.metrics.xirr)], ["Same money as lump sum", this.inr(bt.metrics.lumpsum_value)]]));
    parts.push(this.el("div", { className: "two" }, rows));
    if (bt) parts.push(this.verdict(bt));
    this.show("out-sip", ...parts);
    Charts.line("c-sip", proj.series.map(s => "Year " + s.year), [
      { label: "Expected value", data: proj.series.map(s => s.value) }, { label: "Invested", data: proj.series.map(s => s.invested), dash: [5, 4] }]);
  },
  fundList(results, onPick) {
    document.getElementById("fund-results").replaceChildren(...results.map(f => this.el("li", {},
      this.el("button", { type: "button", onclick: () => onPick(f) }, f.schemeName, this.el("small", {}, "Code " + f.schemeCode)))));
  },
  fund(r) {
    const m = r.metrics, c = k => this.pct(m[k]);
    this.show("out-funds", this.el("h2", {}, r.scheme), this.verdict(r), this.chartBox("c-fund"), this.table("Numbers", [
      ["Score", m.score + " / 100"], ["1-year return", c("cagr_1y")], ["3-year CAGR", c("cagr_3y")], ["5-year CAGR", c("cagr_5y")],
      ["Volatility (3y)", c("volatility")], ["Sharpe ratio", m.sharpe], ["Worst fall (3y)", c("max_drawdown")], ["Latest NAV", this.num(m.latest_nav, 4)]]));
    Charts.line("c-fund", r.chart.map(x => x.date), [{ label: "NAV", data: r.chart.map(x => x.nav) }]);
  },
  ipoList(ipos, onPick) {
    document.getElementById("ipo-list").replaceChildren(...ipos.map(i => this.el("li", {},
      this.el("button", { type: "button", onclick: () => onPick(i) }, i.name,
        this.el("small", {}, "Band up to " + this.inr(i.price_high) + ", lot of " + i.lot_size + ". Tap to load into the form.")))));
  },
  ipo(r) {
    const m = r.metrics;
    this.show("out-ipo", this.verdict(r), this.table("Valuation", [["Peer-based value", this.inr(m.fair_value)],
      ["Upside to issue price", m.upside_pct == null ? "n/a" : m.upside_pct + "%"], ["Issue P/E", m.issue_pe ?? "n/a"],
      ["Grey market premium", m.gmp_pct + "%"], ["Estimated listing price", this.inr(m.est_listing_price)],
      ["Money needed for one lot", this.inr(m.application_amount)], ["Score", m.score]]));
  },
};
