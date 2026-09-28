"""Increment-1 checks: health shape, CORS defaults, rate-limit envelope."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok_and_does_not_leak_secret():
    res = client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert "dashscope_configured" in body
    assert "api_key" not in body
    assert "DASHSCOPE" not in res.text


def test_cors_preflight_allows_configured_origin():
    res = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res.status_code in (200, 204)
    assert res.headers.get("access-control-allow-origin") == "http://localhost:5173"
