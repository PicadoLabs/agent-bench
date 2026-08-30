import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.config.settings import get_settings
from app.storage.database import init_db, SessionLocal
from app.benchmarks.loader import BenchmarkLoader
from app.api.benchmarks import router as benchmarks_router
from app.api.runs import router as runs_router
from app.api.leaderboard import router as leaderboard_router
from app.api.system import router as system_router

settings = get_settings()

app = FastAPI(
    title="AgentBench API",
    description="Provider-agnostic AI coding-agent evaluation & benchmarking platform",
    version="1.0.0"
)

# Enable CORS for local React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(benchmarks_router)
app.include_router(runs_router)
app.include_router(leaderboard_router)
app.include_router(system_router)


@app.on_event("startup")
def on_startup():
    """Initialize SQLite database and sync default benchmarks."""
    init_db()
    db = SessionLocal()
    try:
        tasks_dir = os.path.abspath(os.path.join(settings.benchmarks_dir, "tasks"))
        if os.path.exists(tasks_dir):
            BenchmarkLoader.sync_benchmarks_to_db(db, tasks_dir)
    finally:
        db.close()


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "AgentBench", "version": "1.0.0"}


# Serve compiled React frontend if frontend/dist exists
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    if (frontend_dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="static_assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't hijack API routes
        if full_path.startswith("api/") or full_path.startswith("ws/"):
            return None
        
        # Check if direct file exists (e.g. logo.png, favicon.png, etc.)
        target_file = frontend_dist / full_path
        if full_path and target_file.is_file():
            return FileResponse(str(target_file))

        index_file = frontend_dist / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"error": "Frontend build index.html not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)
