"""Unit tests for frontend static file mounting and SPA delivery."""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
def client_fixture():
    """AsyncClient fixture for verifying frontend static endpoints and API routing."""
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.mark.asyncio
async def test_frontend_root_serves_html(client_fixture: AsyncClient):
    """Verify that GET / returns the modern interactive SPA with HTML content."""
    async with client_fixture as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        content = response.text
        assert "Energia-Ritmus" in content
        assert "Koreogr" in content
        assert 'id="energy-wave-canvas"' in content
        assert 'id="quick-task-input"' in content
        assert 'id="cognitive-debt-meter"' in content
        assert 'id="btn-auto-schedule"' in content
        assert 'id="btn-add-task"' in content
        assert 'id="tasks-timeline"' in content
        assert 'id="task-backlog"' in content


@pytest.mark.asyncio
async def test_static_assets_available(client_fixture: AsyncClient):
    """Verify that GET /app.js and GET /style.css are served correctly at root."""
    async with client_fixture as client:
        res_js = await client.get("/app.js")
        assert res_js.status_code == 200
        assert "javascript" in res_js.headers.get("content-type", "").lower()
        assert "fetchEnergyCurve" in res_js.text

        res_css = await client.get("/style.css")
        assert res_css.status_code == 200
        assert "css" in res_css.headers.get("content-type", "").lower()
        assert "--cyan-neon" in res_css.text


@pytest.mark.asyncio
async def test_static_prefix_assets(client_fixture: AsyncClient):
    """Verify that static assets mounted under /static prefix are also accessible."""
    async with client_fixture as client:
        res_js = await client.get("/static/app.js")
        assert res_js.status_code == 200
        assert "javascript" in res_js.headers.get("content-type", "").lower()

        res_css = await client.get("/static/style.css")
        assert res_css.status_code == 200
        assert "css" in res_css.headers.get("content-type", "").lower()


@pytest.mark.asyncio
async def test_api_endpoints_precedence_over_static(client_fixture: AsyncClient):
    """Verify that /api/v1/* and /health routes take precedence over root static mount."""
    async with client_fixture as client:
        res_health = await client.get("/health")
        assert res_health.status_code == 200
        assert res_health.json() == {"status": "ok", "service": "energy-calendar"}

        res_api_health = await client.get("/api/v1/health")
        assert res_api_health.status_code == 200
        assert res_api_health.json() == {"status": "ok", "service": "energy-calendar"}

        parse_res = await client.post("/api/v1/energy/parse-task", json={"raw_text": "Kódolás 90 perc"})
        assert parse_res.status_code == 200
        assert parse_res.json()["load_type"] == "deep_work"
