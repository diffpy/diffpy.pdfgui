"""Dataset-related Pydantic schemas."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class InstrumentParams(BaseModel):
    """Schema for instrument parameters."""
    stype: str = "N"  # 'N' for neutron, 'X' for X-ray
    qmax: float = 32.0
    qdamp: float = 0.01
    qbroad: float = 0.0
    dscale: float = 1.0


class FitRange(BaseModel):
    """Schema for fitting range."""
    rmin: float = 1.0
    rmax: float = 30.0
    rstep: float = 0.01


class DatasetCreate(BaseModel):
    """Schema for dataset creation."""
    name: str
    file_id: Optional[UUID] = None


class DatasetResponse(BaseModel):
    """Schema for dataset response."""
    id: UUID
    name: str
    source_type: str
    qmax: float
    qdamp: float
    qbroad: float
    dscale: float
    fit_rmin: float
    fit_rmax: float
    fit_rstep: float
    point_count: int
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DataArrays(BaseModel):
    """Schema for PDF data arrays."""
    r: List[float]
    G: List[float]
    dG: Optional[List[float]] = None


class DatasetDataResponse(BaseModel):
    """Schema for full dataset data."""
    observed: DataArrays
    calculated: Optional[DataArrays] = None
    difference: Optional[DataArrays] = None
