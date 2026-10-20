from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
import uuid

from app.database import get_session
from app.auth import get_current_user
from app.models import Project, Asset, User
from app.schemas import AssetCreate, AssetUpdate, AssetRead
from app import storage

router = APIRouter(prefix="/projects/{project_id}/assets", tags=["assets"])


def _get_owned_project(session: Session, project_id: uuid.UUID, user: User) -> Project:
    project = session.get(Project, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _get_owned_asset(session: Session, project: Project, asset_id: uuid.UUID) -> Asset:
    asset = session.get(Asset, asset_id)
    if not asset or asset.project_id != project.id:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.post("/upload", response_model=AssetRead, status_code=201)
async def upload_asset(
    project_id: uuid.UUID,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Upload a file directly. Stored in AWS S3 if configured, otherwise
    saved to local disk and served back from this API — either way the
    caller doesn't need to know which."""
    project = _get_owned_project(session, project_id, current_user)
    result = await storage.save_upload(file, project_id)
    asset = Asset(
        file_url=result.url,
        file_name=file.filename or "",
        asset_type=storage.infer_asset_type(file.content_type),
        size_bytes=result.size_bytes,
        project_id=project.id,
    )
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset


@router.post("", response_model=AssetRead, status_code=201)
def register_asset(
    project_id: uuid.UUID,
    data: AssetCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Register an asset that was already uploaded elsewhere (e.g. the
    frontend uploaded straight to a pre-signed S3 URL)."""
    project = _get_owned_project(session, project_id, current_user)
    asset = Asset(
        file_url=data.file_url,
        file_name=data.file_name,
        asset_type=data.asset_type,
        size_bytes=data.size_bytes,
        project_id=project.id,
    )
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset


@router.get("", response_model=list[AssetRead])
def list_assets(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    project = _get_owned_project(session, project_id, current_user)
    statement = (
        select(Asset)
        .where(Asset.project_id == project.id)
        .order_by(Asset.created_at.desc())
    )
    return session.exec(statement).all()


@router.get("/{asset_id}", response_model=AssetRead)
def get_asset(
    project_id: uuid.UUID,
    asset_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    project = _get_owned_project(session, project_id, current_user)
    return _get_owned_asset(session, project, asset_id)


@router.patch("/{asset_id}", response_model=AssetRead)
def update_asset(
    project_id: uuid.UUID,
    asset_id: uuid.UUID,
    data: AssetUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    project = _get_owned_project(session, project_id, current_user)
    asset = _get_owned_asset(session, project, asset_id)
    file_name = data.file_name.strip()
    if not file_name:
        raise HTTPException(status_code=422, detail="File name cannot be empty")
    asset.file_name = file_name
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(
    project_id: uuid.UUID,
    asset_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    project = _get_owned_project(session, project_id, current_user)
    asset = _get_owned_asset(session, project, asset_id)
    await storage.delete_stored_file(asset.file_url, project.id)
    session.delete(asset)
    session.commit()
