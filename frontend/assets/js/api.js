/* Thin fetch wrapper. The backend address is editable in the sidebar and remembered per browser. */
const API = {
  base() {
    try { return localStorage.getItem("mm_api") || "http://localhost:8000"; } catch { return "http://localhost:8000"; }
  },
  setBase(v) { try { localStorage.setItem("mm_api", v.replace(/\/$/, "")); } catch {} },
  async request(path, opts = {}) {
    let res;
    try { res = await fetch(this.base() + path, opts); }
    catch { throw new Error("Cannot reach the backend. Start it with: uvicorn app.main:app --reload"); }
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Request failed (" + res.status + ")");
    return data;
  },
  get(path) { return this.request(path); },
  post(path, body) {
    return this.request(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  },
};
