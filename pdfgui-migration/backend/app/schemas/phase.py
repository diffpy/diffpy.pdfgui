"""Phase/structure-related Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class LatticeParams(BaseModel):
    """Schema for lattice parameters."""

    a: float
    b: float
    c: float
    alpha: float = 90.0
    beta: float = 90.0
    gamma: float = 90.0


class AtomCreate(BaseModel):
    """Schema for atom creation."""

    element: str
    x: float
    y: float
    z: float
    occupancy: float = 1.0
    uiso: float = 0.0
    u11: Optional[float] = None
    u22: Optional[float] = None
    u33: Optional[float] = None
    u12: Optional[float] = None
    u13: Optional[float] = None
    u23: Optional[float] = None


class AtomResponse(BaseModel):
    """Schema for atom response."""

    id: UUID
    index: int
    element: str
    x: float
    y: float
    z: float
    occupancy: float
    uiso: float
    u11: float
    u22: float
    u33: float
    u12: float
    u13: float
    u23: float
    constraints: Dict[str, Any]


class PhaseCreate(BaseModel):
    """Schema for phase creation."""

    name: str
    file_id: Optional[UUID] = None
    lattice: Optional[LatticeParams] = None
    atoms: Optional[List[AtomCreate]] = None


class PDFParameters(BaseModel):
    """Schema for PDF-specific parameters."""

    scale: float = 1.0
    delta1: float = 0.0
    delta2: float = 0.0
    sratio: float = 1.0
    spdiameter: float = 0.0


class PhaseResponse(BaseModel):
    """Schema for phase response."""

    id: UUID
    name: str
    space_group: Optional[str]
    lattice: LatticeParams
    atom_count: int
    pdf_parameters: PDFParameters
    constraints: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PairSelectionRequest(BaseModel):
    """Schema for pair selection."""

    selections: List[str]  # e.g., ["all-all", "!La-La"]
