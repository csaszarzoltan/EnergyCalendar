"""FastAPI main application entry point."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes import router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app_instance = FastAPI(
        title="EnergyCalendar API",
        description="Circadian energy rhythm choreography and cognitive load scheduling backend",
        version="0.1.0",
    )

    # Configure CORS for frontend web client
    app_instance.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API v1 routes
    app_instance.include_router(router, prefix="/api/v1")

    # Direct /health endpoint fallback
    @app_instance.get("/health", status_code=status.HTTP_200_OK)
    async def root_health() -> dict:
        return {"status": "ok", "service": "energy-calendar"}

    # Global exception handler for ValueError -> 400 Bad Request
    @app_instance.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(exc), "detail": str(exc)},
        )

    # Mount frontend static assets
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
    if not frontend_dir.exists():
        frontend_dir.mkdir(parents=True, exist_ok=True)

    app_instance.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
    app_instance.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

    return app_instance


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

