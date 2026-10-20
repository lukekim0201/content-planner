from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
import uuid

from app.database import get_session
from app.models import Project, User
from app.schemas import ProjectCreate, ProjectUpdate, ProjectRead, ProjectFullRead
from app.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])


def _get_owned_project(session: Session, project_id: uuid.UUID, user: User) -> Project:
    project = session.get(Project, project_id)
    if not project or project.user_id != user.id:
        # 404, not 403 — we don't want to confirm to another user that a
        # project id even exists.
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(
    data: ProjectCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    title = data.title.strip()
    if not title:
        raise HTTPException(status_code=422, detail="Title cannot be empty")
    project = Project(title=title, user_id=current_user.id)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.get("", response_model=list[ProjectRead])
def list_projects(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    statement = (
        select(Project)
        .where(Project.user_id == current_user.id)
        .order_by(Project.created_at.desc())
    )
    return session.exec(statement).all()


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return _get_owned_project(session, project_id, current_user)


@router.get("/{project_id}/full", response_model=ProjectFullRead)
def get_project_full(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    statement = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.script), selectinload(Project.assets))
    )
    project = session.exec(statement).first()
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    project = _get_owned_project(session, project_id, current_user)
    update_data = data.model_dump(exclude_unset=True)
    if "title" in update_data:
        title = (update_data["title"] or "").strip()
        if not title:
            raise HTTPException(status_code=422, detail="Title cannot be empty")
        update_data["title"] = title
    for key, value in update_data.items():
        setattr(project, key, value)
    project.updated_at = datetime.now(UTC)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    project = _get_owned_project(session, project_id, current_user)
    session.delete(project)  # cascades to script + assets (see models.py)
    session.commit()
