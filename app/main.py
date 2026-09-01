from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routers import projects, scripts, assets, auth

app = FastAPI()
app.include_router(projects.router)
app.include_router(scripts.router)
app.include_router(assets.router)
app.include_router(auth.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "null",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API is alive"}

@app.get("/health")
def health_check():
    return {"status": "ok"}