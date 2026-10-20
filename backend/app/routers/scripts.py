from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
import uuid

from app.database import get_session
from app.auth import get_current_user
from app.models import Project, Script, User
from app.schemas import (
    ScriptCreate,
    ScriptUpdate,
    ScriptRead,
    SceneSuggestionRequest,
    SceneSuggestionRead,
)
from app import ai

router = APIRouter(prefix="/projects/{project_id}/script", tags=["scripts"])


def _get_owned_project(session: Session, project_id: uuid.UUID, user: User) -> Project:
    project = session.get(Project, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ScriptRead, status_code=201)
def create_script(
    project_id: uuid.UUID,
    data: ScriptCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    project = _get_owned_project(session, project_id, current_user)
    if project.script:
        raise HTTPException(status_code=400, detail="Script already exists for this project")

    script = Script(content=data.content, project_id=project_id)
    session.add(script)
    # A project with a script being written is no longer just an "idea".
    if project.status == project.status.IDEA:
        project.status = project.status.SCRIPTING
        session.add(project)
    session.commit()
    session.refresh(script)
    return script


@router.get("", response_model=ScriptRead)
def get_script(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    project = _get_owned_project(session, project_id, current_user)
    if not project.script:
        raise HTTPException(status_code=404, detail="Script not found")
    return project.script


@router.patch("", response_model=ScriptRead)
def update_script(
    project_id: uuid.UUID,
    data: ScriptUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    project = _get_owned_project(session, project_id, current_user)
    script = project.script
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    script.content = data.content
    script.updated_at = datetime.now(UTC)
    session.add(script)
    session.commit()
    session.refresh(script)
    return script


@router.delete("", status_code=204)
def delete_script(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    project = _get_owned_project(session, project_id, current_user)
    script = project.script
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    session.delete(script)
    session.commit()


@router.post("/suggest", response_model=SceneSuggestionRead)
async def suggest_next_scene(
    project_id: uuid.UUID,
    data: SceneSuggestionRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Stretch goal: ask an LLM what scene might come next.

    Optional by design — returns HTTP 501 with a clear message if no
    OPENAI_API_KEY is configured, rather than breaking the app.
    """
    project = _get_owned_project(session, project_id, current_user)
    script = project.script
    if not script:
        raise HTTPException(status_code=404, detail="Write a script first")
    suggestion = await ai.suggest_next_scene(script.content, direction=data.direction)
    return SceneSuggestionRead(suggestion=suggestion)
