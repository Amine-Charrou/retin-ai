"""
RetinAI Backend — FastAPI Entrypoint
Run with: uvicorn backend.app.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import STATIC_DIR
from backend.app.database import init_db
from backend.app.api.routes import router

# ── Create the FastAPI app ────────────────────────────────────────────────────
app = FastAPI(
    title="RetinAI API",
    description="Backend API for AI-powered Diabetic Retinopathy Screening",
    version="1.0.0"
)

# ── CORS — allow Next.js frontend ────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount static files (uploads, heatmaps) ───────────────────────────────────
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ── Include API routes ───────────────────────────────────────────────────────
app.include_router(router)

# ── Initialize database on startup ───────────────────────────────────────────
@app.on_event("startup")
async def startup():
    init_db()
    print("[OK] Database initialized")
    print("[OK] RetinAI Backend is ready — http://127.0.0.1:8000")
