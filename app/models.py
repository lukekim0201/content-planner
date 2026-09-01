from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class ProjectStatus(str, Enum):
    IDEA = "IDEA"
    SCRIPTING = "SCRIPTING"
    PRODUCTION = "PRODUCTION"
    COMPLETED = "COMPLETED"


class AssetType(str, Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"


class User(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    projects: List["Project"] = Relationship(back_populates="owner")


class Project(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    status: ProjectStatus = Field(default=ProjectStatus.IDEA)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user_id: uuid.UUID = Field(foreign_key="user.id")
    owner: Optional[User] = Relationship(back_populates="projects")

    script: Optional["Script"] = Relationship(back_populates="project")
    assets: List["Asset"] = Relationship(back_populates="project")


class Script(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    content: str = Field(default="")
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    project_id: uuid.UUID = Field(foreign_key="project.id", unique=True)
    project: Optional[Project] = Relationship(back_populates="script")


class Asset(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    file_url: str
    asset_type: AssetType
    created_at: datetime = Field(default_factory=datetime.utcnow)

    project_id: uuid.UUID = Field(foreign_key="project.id")
    project: Optional[Project] = Relationship(back_populates="assets")