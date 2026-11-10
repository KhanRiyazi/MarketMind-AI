from fastapi.testclient import TestClient
from app.main import app


def test_health():
    with TestClient(app) as c:
        r = c.get("/health")
        assert r.status_code == 200 and r.json()["status"] == "ok"


def test_sip_projection_endpoint():
    with TestClient(app) as c:
        r = c.post("/api/sip/projection", json={"monthly": 5000, "years": 10, "annual_return": 0.12})
        assert r.status_code == 200
        body = r.json()
        assert body["metrics"]["value"] > body["metrics"]["invested"] and len(body["series"]) == 10


def test_sip_validation_error():
    with TestClient(app) as c:
        assert c.post("/api/sip/projection", json={"monthly": -1, "years": 10}).status_code == 422


def test_ipo_endpoint_verdicts():
    with TestClient(app) as c:
        good = c.post("/api/ipo/analyze", json={"name": "A", "price_high": 400, "lot_size": 30, "eps": 20,
                                                "peer_pe": 30, "gmp": 80, "subscription_x": 30}).json()
        bad = c.post("/api/ipo/analyze", json={"name": "B", "price_high": 400, "lot_size": 30, "eps": -2,
                                               "peer_pe": 30, "gmp": -10, "subscription_x": 0.5}).json()
        assert good["verdict"] == "Apply" and bad["verdict"] == "Avoid"


def test_bad_symbol_is_400():
    with TestClient(app) as c:
        assert c.get("/api/market/quote/bad;symbol").status_code in (400, 404)
