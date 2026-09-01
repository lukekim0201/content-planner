from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.auth import get_current_user
from app.models import Project, Script, User
from app.schemas import ScriptCreate, ScriptUpdate, ScriptRead
import uuid

router = APIRouter(prefix="/projects/{project_id}/script", tags=["scripts"])

@router.post("/", response_model=ScriptRead, status_code=201)
def create_script(
    project_id: uuid.UUID,data: ScriptCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    project = session.get(Project, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.script:
        raise HTTPException(status_code=400, detail="Script already exists for this project")
    
    script = Script(content=data.content, project_id=project_id)
    session.add(script)
    session.commit()
    session.refresh(script)
    return script

@router.get("/", response_model=ScriptRead)
def get_script(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    project = session.get(Project, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    
    script = project.script
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    return script

@router.patch("/", response_model=ScriptRead)
def update_script(
    project_id: uuid.UUID,
    data: ScriptUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    project = session.get(Project, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    
    script = project.script
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(script, key, value)
    session.add(script)
    session.commit()
    session.refresh(script)
    return script

@router.delete("/", status_code=204)
def delete_script(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    project = session.get(Project, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    
    script = project.script
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    session.delete(script)
    session.commit()