from sqlmodel import SQLModel
from typing import Optional
import uuid
from app.models import ProjectStatus, AssetType

# User
class UserCreate(SQLModel):
    email: str
    password: str

class UserLogin(SQLModel):
    email: str
    password: str

class UserRead(SQLModel):
    id: uuid.UUID
    email: str

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

#Project
class ProjectCreate(SQLModel):
    title: str

class ProjectUpdate(SQLModel):
    title: Optional[str] = None
    status: Optional[ProjectStatus] = None

class ProjectRead(SQLModel):
    id: uuid.UUID
    title: str
    status: ProjectStatus

#Script
class ScriptCreate(SQLModel):
    content: str

class ScriptUpdate(SQLModel):
    content: Optional[str] = None

class ScriptRead(SQLModel):
    id: uuid.UUID
    content: str

#Asset
class AssetCreate(SQLModel):
    file_url: str
    asset_type: AssetType

class AssetRead(SQLModel):
    id: uuid.UUID
    file_url: str
    asset_type: AssetType

# Nested
class ProjectFullRead(SQLModel):
    id: uuid.UUID
    title: str
    status: ProjectStatus
    script: Optional[ScriptRead] = None
    assets: list[AssetRead] = []