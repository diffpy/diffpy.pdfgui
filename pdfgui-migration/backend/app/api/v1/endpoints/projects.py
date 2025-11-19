"""Project management endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ....api.deps import get_current_user
from ....core.database import get_db
from ....models.project import Fitting, Project
from ....models.user import User
from ....schemas.project import ProjectCreate, ProjectListResponse, ProjectResponse, ProjectUpdate

router = APIRouter()


@router.get("", response_model=ProjectListResponse)
def list_projects(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    archived: bool = False,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all projects for current user."""
    query = db.query(Project).filter(Project.user_id == current_user.id, Project.is_archived == archived)

    if search:
        query = query.filter(Project.name.ilike(f"%{search}%"))

    total = query.count()
    projects = query.offset((page - 1) * per_page).limit(per_page).all()

    # Add fitting count
    items = []
    for project in projects:
        project_dict = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "metadata": project.metadata,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "is_archived": project.is_archived,
            "fitting_count": len(project.fittings),
        }
        items.append(ProjectResponse(**project_dict))

    return ProjectListResponse(items=items, total=total, page=page, per_page=per_page)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Create a new project."""
    project = Project(
        user_id=current_user.id,
        name=project_data.name,
        description=project_data.description,
        metadata=project_data.metadata or {},
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        metadata=project.metadata,
        created_at=project.created_at,
        updated_at=project.updated_at,
        is_archived=project.is_archived,
        fitting_count=0,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get project details."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        metadata=project.metadata,
        created_at=project.created_at,
        updated_at=project.updated_at,
        is_archived=project.is_archived,
        fitting_count=len(project.fittings),
    )


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update project metadata."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description
    if project_data.metadata is not None:
        project.metadata = project_data.metadata
    if project_data.is_archived is not None:
        project.is_archived = project_data.is_archived

    db.commit()
    db.refresh(project)

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        metadata=project.metadata,
        created_at=project.created_at,
        updated_at=project.updated_at,
        is_archived=project.is_archived,
        fitting_count=len(project.fittings),
    )


@router.delete("/{project_id}")
def delete_project(
    project_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Delete (archive) project."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.is_archived = True
    db.commit()

    return {"success": True}
