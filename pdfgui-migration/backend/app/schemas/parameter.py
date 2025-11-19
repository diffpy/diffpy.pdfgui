"""Parameter and constraint Pydantic schemas."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class ParameterBounds(BaseModel):
    """Schema for parameter bounds."""

    lower: Optional[float] = None
    upper: Optional[float] = None


class ParameterUpdate(BaseModel):
    """Schema for parameter update."""

    index: int
    initial_value: Optional[float] = None
    is_fixed: Optional[bool] = None
    bounds: Optional[ParameterBounds] = None


class ParameterResponse(BaseModel):
    """Schema for parameter response."""

    index: int
    name: Optional[str]
    initial_value: float
    refined_value: Optional[float]
    uncertainty: Optional[float]
    is_fixed: bool
    bounds: ParameterBounds


class ParametersUpdateRequest(BaseModel):
    """Schema for updating multiple parameters."""

    parameters: List[ParameterUpdate]


class ConstraintCreate(BaseModel):
    """Schema for constraint creation."""

    target: str
    formula: str
    phase_id: Optional[UUID] = None


class ConstraintResponse(BaseModel):
    """Schema for constraint response."""

    id: UUID
    target: str
    formula: str
    phase_id: Optional[UUID]
    parameters_used: List[int]


class ConstraintValidation(BaseModel):
    """Schema for constraint validation result."""

    valid: bool
    parameters_used: List[int]
    error: Optional[str] = None
