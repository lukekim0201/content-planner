from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.database import get_session
from app.models import Project
from app.schemas import ProjectCreate, ProjectUpdate, ProjectRead, ProjectFullRead
import uuid
#temp
from app.constants import PLACEHOLDER_USER_ID

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ProjectRead, status_code=201)
def create_project(data: ProjectCreate, session: Session = Depends(get_session)):
    project = Project(title=data.title, user_id=PLACEHOLDER_USER_ID)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@router.get("/", response_model=list[ProjectRead])
def list_projects(session: Session = Depends(get_session)):
    return session.exec(select(Project)).all()

@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: uuid.UUID, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/{project_id}/full", response_model=ProjectFullRead)
def get_project_full(project_id: uuid.UUID, session: Session = Depends(get_session)):
    statement = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.script), selectinload(Project.assets))
    )
    project = session.exec(statement).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: uuid.UUID, data: ProjectUpdate, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: uuid.UUID, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    session.delete(project)
    session.commit()