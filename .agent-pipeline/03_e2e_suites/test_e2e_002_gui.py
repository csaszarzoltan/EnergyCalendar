"""E2E Test Suite for SPEC-002: Frontend UI and Interactive App Mounting.

Black-box verification of web UI delivery, static assets, and DOM contracts.
"""
from __future__ import annotations
import pytest
from httpx import AsyncClient, ASGITransport

try:
    from src.main import app
except ImportError:
    app = None

BASE_API_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def test_e2e_gui_root_serves_html():
    """Verify that GET / returns the modern interactive SPA with HTML content."""
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_API_URL)
    async with client_ctx as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        content = response.text
        assert "Energia-Ritmus" in content
        assert "Koreogr" in content
        assert "energy-wave-canvas" in content
        assert "quick-task-input" in content
        assert "cognitive-debt-meter" in content


@pytest.mark.asyncio
async def test_e2e_gui_static_assets():
    """Verify that static assets (app.js, style.css) are served correctly."""
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_API_URL)
    async with client_ctx as client:
        res_js = await client.get("/app.js")
        assert res_js.status_code == 200
        assert "javascript" in res_js.headers.get("content-type", "").lower()
        
        res_css = await client.get("/style.css")
        assert res_css.status_code == 200
        assert "css" in res_css.headers.get("content-type", "").lower()


@pytest.mark.asyncio
async def test_e2e_gui_dom_contracts():
    """Verify critical interactive controls and UI element IDs in HTML."""
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_API_URL)
    async with client_ctx as client:
        response = await client.get("/")
        content = response.text
        # Essential interactive selectors from US-001 gui_flow
        assert 'id="energy-wave-canvas"' in content
        assert 'id="quick-task-input"' in content
        assert 'id="btn-auto-schedule"' in content
        assert 'id="btn-add-task"' in content
        assert 'id="cognitive-debt-meter"' in content
        assert 'id="tasks-timeline"' in content
        assert 'id="task-backlog"' in content
