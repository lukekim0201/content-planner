from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Project, Asset
from app.schemas import AssetCreate, AssetRead
import uuid

router = APIRouter(prefix="/projects/{project_id}/assets", tags=["assets"])

@router.post("/", response_model=AssetRead, status_code=201)
def create_asset(project_id: uuid.UUID, data: AssetCreate, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    asset = Asset(file_url=data.file_url, asset_type=data.asset_type, project_id=project_id)
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset

@router.get("/", response_model=list[AssetRead])
def list_assets(project_id: uuid.UUID, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return session.exec(select(Asset).where(Asset.project_id == project_id)).all()

@router.delete("/{asset_id}", status_code=204)
def delete_asset(project_id: uuid.UUID, asset_id: uuid.UUID, session: Session = Depends(get_session)):
    asset = session.get(Asset, asset_id)
    if not asset or asset.project_id != project_id:
        raise HTTPException(status_code=404, detail="Asset not found")
    session.delete(asset)
    session.commit()