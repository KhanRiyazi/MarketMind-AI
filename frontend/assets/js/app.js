/* Wiring: tabs, forms, backend connection check. */
const $ = s => document.querySelector(s);
const formData = f => Object.fromEntries(new FormData(f));

function bindForm(id, outId, handler) {
  $(id).addEventListener("submit", async e => {
    e.preventDefault();
    const btn = e.target.querySelector("button[type=submit], button:not([type])");
    btn.disabled = true; UI.loading(outId);
    try { await handler(formData(e.target)); } catch (err) { UI.error(outId, err); } finally { btn.disabled = false; }
  });
}

function openTab(name) {
  document.querySelectorAll(".tab").forEach(t => t.classList.toggle("on", t.id === "tab-" + name));
  document.querySelectorAll("#nav button").forEach(b => b.classList.toggle("on", b.dataset.tab === name));
  if (location.hash !== "#" + name) history.replaceState(null, "", "#" + name);
}

async function checkBackend() {
  const s = $("#apiStatus");
  try { const h = await API.get("/health"); s.textContent = "Connected" + (h.llm ? ", AI narration on" : ""); s.className = "ok"; return true; }
  catch { s.textContent = "Not reachable"; s.className = "bad"; return false; }
}

async function loadMarket() {
  try { UI.indices((await API.get("/api/market/overview")).indices); }
  catch (e) { UI.error("out-market", e); }
}

async function loadIpos() {
  try {
    UI.ipoList((await API.get("/api/ipo/upcoming")).ipos, i => {
      const f = $("#form-ipo");
      ["name", "price_high", "lot_size", "eps", "peer_pe", "gmp", "subscription_x"].forEach(k => { f.elements[k].value = i[k] ?? ""; });
      f.scrollIntoView({ behavior: "smooth" });
    });
  } catch (e) { UI.error("out-ipo", e); }
}

bindForm("#form-quote", "out-market", async d =>
  UI.trend(await API.get("/api/market/history/" + encodeURIComponent(d.symbol) + "?period=2y")));

bindForm("#form-intraday", "out-intraday", async d =>
  UI.intraday(await API.get("/api/intraday/" + encodeURIComponent(d.symbol) + "?" + new URLSearchParams({
    interval: d.interval, capital: d.capital, risk_pct: d.risk_pct }))));

bindForm("#form-sip", "out-sip", async d => {
  const base = { years: +d.years, annual_return: d.annual_return / 100, step_up: (d.step_up || 0) / 100 };
  const proj = await API.post("/api/sip/projection", { ...base, monthly: +d.monthly });
  const goal = d.target ? await API.post("/api/sip/goal", { ...base, target: +d.target }) : null;
  const bt = d.scheme_code ? await API.post("/api/sip/backtest", { scheme_code: +d.scheme_code, monthly: +d.monthly, years: Math.min(+d.years, 20) }) : null;
  UI.sip(proj, goal, bt);
});

bindForm("#form-funds", "fund-results", async d => {
  const { results } = await API.get("/api/mutual-funds/search?q=" + encodeURIComponent(d.q));
  UI.fundList(results, async f => {
    UI.loading("out-funds");
    try { UI.fund(await API.get("/api/mutual-funds/" + f.schemeCode + "/analysis")); } catch (e) { UI.error("out-funds", e); }
  });
  if (!results.length) UI.error("fund-results", new Error("No funds matched. Try fewer words."));
});

bindForm("#form-ipo", "out-ipo", async d => UI.ipo(await API.post("/api/ipo/analyze", {
  name: d.name, price_high: +d.price_high, lot_size: +d.lot_size, eps: +d.eps, peer_pe: +d.peer_pe,
  gmp: +d.gmp || 0, subscription_x: +d.subscription_x || 0 })));

$("#nav").addEventListener("click", e => e.target.dataset.tab && openTab(e.target.dataset.tab));
$("#apiBase").value = API.base();
$("#apiBase").addEventListener("change", async e => { API.setBase(e.target.value); if (await checkBackend()) { loadMarket(); loadIpos(); } });
window.addEventListener("hashchange", () => openTab(location.hash.slice(1) || "market"));

openTab(location.hash.slice(1) || "market");
checkBackend().then(ok => { if (ok) { loadMarket(); loadIpos(); } });
