"""Project-related Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    """Schema for project creation."""

    name: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class ProjectUpdate(BaseModel):
    """Schema for project update."""

    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    is_archived: Optional[bool] = None


class ProjectResponse(BaseModel):
    """Schema for project response."""

    id: UUID
    name: str
    description: Optional[str]
    metadata: Dict[str, Any]
    fitting_count: int = 0
    created_at: datetime
    updated_at: datetime
    is_archived: bool

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Schema for paginated project list."""

    items: List[ProjectResponse]
    total: int
    page: int
    per_page: int
