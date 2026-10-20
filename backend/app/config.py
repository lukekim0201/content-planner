"""Centralized environment configuration.

Everything the app reads from the environment goes through here so there is
exactly one place that knows the variable names and their defaults.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Database -----------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./content_planner.db")
# Some hosts hand out "postgres://" URLs, which SQLAlchemy 2.x rejects.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://"):]

# --- Auth -----------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# --- CORS -------------------------------------------------------------
# Comma-separated list of extra allowed origins (e.g. your deployed Vercel
# URL). localhost:5173 (Vite dev server) is always allowed.
_extra_origins = os.getenv("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"] + [
    origin.strip() for origin in _extra_origins.split(",") if origin.strip()
]

# --- Public URL of this API (used to build local-storage file URLs) ----
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")

# --- Asset storage: AWS S3, falling back to local disk -------------------
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
LOCAL_UPLOAD_DIR = os.getenv("LOCAL_UPLOAD_DIR", "uploads")
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(50 * 1024 * 1024)))  # 50MB

def storage_is_s3() -> bool:
    return bool(AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_S3_BUCKET)

# --- AI stretch goal: scene brainstorming via OpenAI ----------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def ai_is_configured() -> bool:
    return bool(OPENAI_API_KEY)
