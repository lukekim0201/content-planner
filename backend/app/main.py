from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import ALLOWED_ORIGINS, LOCAL_UPLOAD_DIR, DATABASE_URL, storage_is_s3
from app.routers import projects, scripts, assets, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Zero-setup local dev: SQLite gets its tables created automatically on
    # startup. Postgres (prod) is expected to be migrated explicitly via
    # `alembic upgrade head` (see Procfile / render.yaml / railway.json),
    # so we deliberately don't auto-create tables there.
    if DATABASE_URL.startswith("sqlite"):
        from app.database import create_db_and_tables

        create_db_and_tables()
    yield


app = FastAPI(
    title="Content Planner API",
    description=(
        "Plan, script, and produce video content: projects move through "
        "IDEA -> SCRIPTING -> PRODUCTION -> COMPLETED on a kanban board, "
        "each project has one script and any number of media assets."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(scripts.router)
app.include_router(assets.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Only needed when AWS S3 isn't configured: serve locally-stored assets
# back out from the same API (see app/storage.py).
if not storage_is_s3():
    Path(LOCAL_UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=LOCAL_UPLOAD_DIR), name="uploads")


@app.get("/")
def read_root():
    return {"message": "Content Planner API is alive"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "storage_backend": "s3" if storage_is_s3() else "local-disk",
    }
