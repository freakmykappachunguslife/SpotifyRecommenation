"""
Gago Glazers FastAPI backend entry point.
"""
import os
from pathlib import Path

# Load .env from project root, then backend/ (backend overrides)
from dotenv import load_dotenv
_backend_dir = Path(__file__).resolve().parent
_project_root = _backend_dir.parent
_env_root = _project_root / ".env"
_env_backend = _backend_dir / ".env"
load_dotenv(_env_root)
load_dotenv(_env_backend)
# Startup check: warn if credentials might be missing
if not os.getenv("SPOTIFY_CLIENT_ID") or not os.getenv("SPOTIFY_CLIENT_SECRET"):
    print(f"WARNING: Spotify credentials not set. Loaded .env from: {_env_root} (exists={_env_root.exists()}), {_env_backend} (exists={_env_backend.exists()})")
    print("  Put SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env in the project root:", _project_root)
else:
    print("Spotify credentials loaded from .env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from api_routes import router as api_router

app = FastAPI(
    title="Gago Glazers API",
    description="Search + track + audio features via Spotify; similar tracks via cosine similarity on audio features.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api", tags=["api"])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def index():
    """Simple HTML UI for search and similar (optional)."""
    return FileResponse(Path(__file__).parent / "static" / "index.html")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8888"))
    uvicorn.run(app, host="0.0.0.0", port=port)
