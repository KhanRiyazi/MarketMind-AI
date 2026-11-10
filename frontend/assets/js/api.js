/* Thin fetch wrapper. The backend address is editable in the sidebar and remembered per browser. */
/* Thin fetch wrapper. Uses localhost when you run the site locally, Render when it is hosted.
   The address can still be overridden from the sidebar field. */
const DEFAULT_API = ["localhost", "127.0.0.1"].includes(location.hostname)
  ? "http://localhost:8000"
  : "https://marketmind-api-qm38.onrender.com";

const API = {
  base() {
    try { return localStorage.getItem("mm_api") || DEFAULT_API; } catch { return DEFAULT_API; }
  },
  setBase(v) { try { localStorage.setItem("mm_api", v.replace(/\/$/, "")); } catch { } },
  async request(path, opts = {}) {
    let res;
    try { res = await fetch(this.base() + path, opts); }
    catch { throw new Error("Cannot reach the backend. If it was idle, wait about 30 seconds and try again."); }
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Request failed (" + res.status + ")");
    return data;
  },
  get(path) { return this.request(path); },
  post(path, body) {
    return this.request(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  },
};