"""Fitting-related Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class FittingCreate(BaseModel):
    """Schema for fitting creation."""

    name: str
    copy_from: Optional[UUID] = None


class FittingRun(BaseModel):
    """Schema for running refinement."""

    max_iterations: int = 100
    tolerance: float = 1e-8


class FittingResponse(BaseModel):
    """Schema for fitting response."""

    id: UUID
    name: str
    status: str
    rw_value: Optional[float]
    chi_squared: Optional[float]
    phase_count: int = 0
    dataset_count: int = 0
    parameters: Dict[str, Any] = {}
    results: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class FittingStatusResponse(BaseModel):
    """Schema for fitting status during refinement."""

    status: str
    iteration: int
    current_rw: Optional[float]
    elapsed_time: float


class FittingResultsResponse(BaseModel):
    """Schema for fitting results."""

    rw: float
    chi_squared: float
    iterations: int
    elapsed_time: float
    parameters: List[Dict[str, Any]]
    residuals: Dict[str, Any]
