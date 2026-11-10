# Architecture

```
Browser (GitHub Pages)  --fetch-->  FastAPI (api/)  -->  agents/  -->  analytics/   (pure maths, tested)
                                                           |
                                                           +-->  integrations/market_data  -->  data/collectors -> processors -> validators
                                                           +-->  LLM narration (optional, falls back to templates)
                                    database/ (SQLite audit log)      integrations/google_* (optional)
```

**Layers**
- `api/`: thin routers. Validate input (Pydantic), call one agent, log, return JSON.
- `agents/`: orchestration. Fetch, compute, decide a verdict, write the summary. `BaseAgent.finish` is the one place the LLM is used.
- `analytics/`: no I/O. Everything here is unit-tested.
- `data/`: collectors hit the network; processors clean and make JSON-safe; validators reject bad input or corrupt bars before analysis.
- `integrations/market_data.py`: the only module agents use for data; adds a TTL cache.

**Design rules**
1. Numbers come from code, never from the LLM.
2. A failing optional service (LLM, Sheets, DB) must not break a response.
3. Frontend renders API text with `textContent` only.

**Extending:** add `agents/x_agent.py` (subclass `BaseAgent`), a router in `api/`, and register it in `main.py`.
