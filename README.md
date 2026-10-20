# Content Planner

A mini production-management tool for video creators: take a video from
"I have an idea" to "I have a finished video with all its assets organized,"
tracking where each project sits in that pipeline on a kanban board.

## What it does

- **Projects** — one video idea each (e.g. "My Trip to Osaka Vlog"), moving
  through **IDEA → SCRIPTING → PRODUCTION → COMPLETED** on a drag-and-drop
  kanban board.
- **Scripts** — each project has exactly one script, written in a rich-text
  editor (Tiptap). Creating a script auto-advances a project out of `IDEA`.
- **Assets** — each project can hold any number of photos/videos/audio
  clips, uploaded by drag-and-drop, previewed in a gallery.
- **Auth** — email/password signup and login (JWT), so users only ever see
  their own projects.
- **Stretch goal** — an optional "suggest the next scene" button that asks
  OpenAI for a scene idea based on the script so far. Fully optional: with
  no API key configured it just explains that it's off, instead of
  breaking anything.

## Tech stack

| Layer    | Choice                                                        |
| -------- | -------------------------------------------------------------- |
| Backend  | FastAPI + SQLModel (SQLAlchemy) + JWT auth (python-jose/passlib) |
| Database | PostgreSQL in production, SQLite with zero setup for local dev  |
| Frontend | React (Vite) + Tailwind CSS + Tiptap editor + React Router      |
| Storage  | AWS S3 when configured, local disk otherwise (via boto3)        |
| AI       | OpenAI Chat Completions API (optional scene suggestions)        |
| Deploy   | Render or Railway (backend) + Vercel (frontend)                 |

## Project layout

```
backend/    FastAPI app, models, routers, Alembic migrations, tests
frontend/   React (Vite) SPA
```

## 1. Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
```

The default `.env` works out of the box with **zero setup** — it points at
a local SQLite file and stores uploaded assets on disk. Just run:

```bash
uvicorn app.main:app --reload
```

The API is now at `http://localhost:8000` (interactive docs at `/docs`).
Tables are created automatically on startup when using SQLite.

Optionally seed a demo account with sample projects across every column:

```bash
python seed.py
```

This creates `demo@example.com` / `demopass123` with four projects, one per
kanban column.

### Switching to Postgres

Set `DATABASE_URL` in `.env` to a Postgres connection string, then run
migrations instead of relying on auto-create:

```bash
alembic upgrade head
```

### Switching to AWS S3

Set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_S3_BUCKET` (and
optionally `AWS_REGION`, default `us-east-1`) in `.env` — uploads
automatically switch from local disk to S3 via `boto3`, no code changes
needed. The bucket needs public-read access on its objects for the
returned `file_url` to be directly viewable (or adapt `app/storage.py` to
return presigned GET URLs if you'd rather keep it private).

### Turning on the AI stretch goal

Set `OPENAI_API_KEY` in `.env` (defaults to the `gpt-4o-mini` model, change
via `OPENAI_MODEL`). Leave it blank and the feature just explains it's
off — nothing else in the app depends on it.

### Running backend tests

```bash
cd backend
pytest
```

The suite runs against an in-memory SQLite database, so it needs no
external services and leaves nothing behind.

## 2. Frontend setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The app is now at `http://localhost:5173`. `VITE_API_BASE_URL` in `.env`
points it at the backend (defaults to `http://localhost:8000`).

## Core features

1. **Auth** — sign up / log in, JWT stored in `localStorage`, attached to
   every request by `src/api/client.js`; `get_current_user` protects every
   write endpoint. Ownership is checked on every project/script/asset
   route — another user's project 404s rather than 403s, so its existence
   isn't leaked either.
2. **Kanban board** (`DashboardPage` + `KanbanBoard`) — drag a project card
   between the four status columns; the move is optimistic in the UI and
   persisted with a `PATCH /projects/{id}`, rolling back on failure. The
   status can also be changed from a dropdown on the project detail page.
3. **Script editor** (`ScriptEditPage` + `ScriptEditor`) — a Tiptap rich
   text editor with a small toolbar (bold, italic, heading, quote, lists).
   Creating the first script for a project bumps its status from `IDEA` to
   `SCRIPTING` automatically.
4. **Assets** (`AssetUploader` + `AssetGallery`) — drag-and-drop or click
   to upload; per-file progress bars; a responsive gallery that renders
   images inline, gives video/audio native players, and a generic icon for
   anything else.
5. **AI scene suggestions** (stretch goal) — `POST
   /projects/{id}/script/suggest` calls OpenAI with the script so far (plus
   optional creative direction) and returns one concrete next scene.

## Deployment

- **Backend → Render**: `backend/render.yaml` is a ready-to-use Blueprint
  (New → Blueprint in the Render dashboard, point it at this repo and set
  the Blueprint path to `backend/render.yaml`). It provisions a free
  Postgres database, runs `alembic upgrade head` on every deploy, and
  generates a `SECRET_KEY` for you.
- **Backend → Railway**: set the service's root directory to `backend`;
  `railway.json` configures the start command (migrate then serve). Add a
  Postgres plugin and set the same env vars as in `.env.example`.
- **Frontend → Vercel**: import this repo with `frontend` as the project
  root, set `VITE_API_BASE_URL` to your deployed backend URL.
  `vercel.json` handles the SPA rewrite so client-side routes don't 404 on
  refresh.
- Whichever backend host you use, set `ALLOWED_ORIGINS` to your Vercel URL
  so the browser's CORS check passes, and `PUBLIC_BASE_URL` to the
  backend's own public URL (only matters if you're using local-disk
  storage instead of S3).

## API endpoints

22 endpoints total (20 domain endpoints + 2 trivial health-check routes).

| Method | Path                                | Auth | Description                          |
| ------ | ------------------------------------ | ---- | ------------------------------------- |
| GET    | `/`                                   | —    | Liveness check                        |
| GET    | `/health`                             | —    | Health check (reports storage backend)|
| POST   | `/signup`                            | —    | Create a user                         |
| POST   | `/login`                             | —    | Get a JWT access token                |
| GET    | `/auth/me`                           | ✓    | Current user                          |
| POST   | `/projects`                          | ✓    | Create a project (starts as `IDEA`)   |
| GET    | `/projects`                          | ✓    | List your projects                    |
| GET    | `/projects/{id}`                     | ✓    | Get one project                       |
| GET    | `/projects/{id}/full`                | ✓    | Project + script + assets, nested     |
| PATCH  | `/projects/{id}`                     | ✓    | Update title and/or status            |
| DELETE | `/projects/{id}`                     | ✓    | Delete a project (cascades)           |
| POST   | `/projects/{id}/script`              | ✓    | Create the project's script           |
| GET    | `/projects/{id}/script`              | ✓    | Get the script                        |
| PATCH  | `/projects/{id}/script`              | ✓    | Update script content                 |
| DELETE | `/projects/{id}/script`              | ✓    | Delete the script                     |
| POST   | `/projects/{id}/script/suggest`      | ✓    | AI: suggest the next scene (optional) |
| POST   | `/projects/{id}/assets/upload`       | ✓    | Upload a file (multipart)             |
| POST   | `/projects/{id}/assets`              | ✓    | Register an already-hosted asset      |
| GET    | `/projects/{id}/assets`              | ✓    | List assets                           |
| GET    | `/projects/{id}/assets/{asset_id}`   | ✓    | Get one asset                         |
| PATCH  | `/projects/{id}/assets/{asset_id}`   | ✓    | Rename an asset                       |
| DELETE | `/projects/{id}/assets/{asset_id}`   | ✓    | Delete an asset (and its S3 object)   |

## Measured performance

Real numbers, not a guess — [`backend/benchmark.py`](backend/benchmark.py)
hits the core CRUD endpoints 50x each and reports average/p95 latency. A
local run (SQLite, single `uvicorn` worker, loopback — no network hop)
measured:

```
GET /projects                    avg=  3.14ms  p95=  4.10ms  (n=50)
GET /projects/{id}               avg=  3.68ms  p95=  5.40ms  (n=50)
GET /projects/{id}/full          avg=  4.33ms  p95=  5.01ms  (n=50)
PATCH /projects/{id}             avg=  5.25ms  p95=  6.12ms  (n=50)
GET /projects/{id}/script        avg=  2.86ms  p95=  3.49ms  (n=50)
GET /auth/me                     avg=  1.98ms  p95=  2.53ms  (n=50)
------------------------------------------------------------
OVERALL                          avg=  3.54ms  p95=  5.49ms  (n=300)
```

Comfortably under 100ms — but this is local SQLite with no network hop, so
it's the best case, not a production number. Re-run
`python benchmark.py` (server must be running) against your actual
deployed backend before quoting a number publicly — a Postgres round trip
and a hosted free-tier instance (Render/Railway) will both add real
latency, and a cold start on a free-tier dyno can spike well past 100ms
for the very first request.
