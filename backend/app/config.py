"""
RetinAI Backend — Configuration
Loads environment variables and defines paths.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # retin-ai-1/
load_dotenv(PROJECT_ROOT / ".env")

# ── Directories ───────────────────────────────────────────────────────────────
BACKEND_DIR = PROJECT_ROOT / "backend"
MODEL_DIR = BACKEND_DIR / "model"
STATIC_DIR = BACKEND_DIR / "static"
UPLOADS_DIR = STATIC_DIR / "uploads"
HEATMAPS_DIR = STATIC_DIR / "heatmaps"

# Ensure directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
HEATMAPS_DIR.mkdir(parents=True, exist_ok=True)

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_PATH = BACKEND_DIR / "retinai.db"
