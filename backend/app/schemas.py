from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime
import uuid
from app.models import ProjectStatus, AssetType


# --- User / auth ---------------------------------------------------------
class UserCreate(SQLModel):
    email: str
    password: str


class UserLogin(SQLModel):
    email: str
    password: str


class UserRead(SQLModel):
    id: uuid.UUID
    email: str
    created_at: datetime


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# --- Project ---------------------------------------------------------------
class ProjectCreate(SQLModel):
    title: str


class ProjectUpdate(SQLModel):
    title: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ProjectRead(SQLModel):
    id: uuid.UUID
    title: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime


# --- Script ---------------------------------------------------------------
class ScriptCreate(SQLModel):
    content: str = ""


class ScriptUpdate(SQLModel):
    content: str


class ScriptRead(SQLModel):
    id: uuid.UUID
    content: str
    updated_at: datetime


class SceneSuggestionRequest(SQLModel):
    # Optional extra creative direction from the user, e.g. "make it funnier"
    direction: Optional[str] = None


class SceneSuggestionRead(SQLModel):
    suggestion: str


# --- Asset ---------------------------------------------------------------
class AssetCreate(SQLModel):
    """Register an asset that was already uploaded elsewhere (e.g. directly
    to a pre-signed S3 URL from the browser)."""
    file_url: str
    file_name: str = ""
    asset_type: AssetType
    size_bytes: int = 0


class AssetUpdate(SQLModel):
    file_name: str


class AssetRead(SQLModel):
    id: uuid.UUID
    file_url: str
    file_name: str
    asset_type: AssetType
    size_bytes: int
    created_at: datetime


# --- Nested / combined reads ------------------------------------------
class ProjectFullRead(SQLModel):
    id: uuid.UUID
    title: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    script: Optional[ScriptRead] = None
    assets: list[AssetRead] = []
