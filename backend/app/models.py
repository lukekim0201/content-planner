from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, UTC
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
    OTHER = "OTHER"


def _utcnow() -> datetime:
    return datetime.now(UTC)


class User(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=_utcnow)

    projects: List["Project"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Project(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    status: ProjectStatus = Field(default=ProjectStatus.IDEA, index=True)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    owner: Optional[User] = Relationship(back_populates="projects")

    script: Optional["Script"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "uselist": False},
    )
    assets: List["Asset"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Script(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    content: str = Field(default="")
    updated_at: datetime = Field(default_factory=_utcnow)

    project_id: uuid.UUID = Field(foreign_key="project.id", unique=True)
    project: Optional[Project] = Relationship(back_populates="script")


class Asset(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    file_url: str
    file_name: str = Field(default="")
    asset_type: AssetType
    size_bytes: int = Field(default=0)
    created_at: datetime = Field(default_factory=_utcnow)

    project_id: uuid.UUID = Field(foreign_key="project.id", index=True)
    project: Optional[Project] = Relationship(back_populates="assets")
