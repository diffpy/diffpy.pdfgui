"""Parameter and constraint database models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base


class Parameter(Base):
    """Refinable parameter model."""
    __tablename__ = "parameters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fitting_id = Column(UUID(as_uuid=True), ForeignKey("fittings.id"), nullable=False)
    param_index = Column(Integer, nullable=False)  # @1, @2, etc.
    name = Column(String(100))
    initial_value = Column(Float, default=0.0)
    refined_value = Column(Float)
    uncertainty = Column(Float)
    is_fixed = Column(Boolean, default=False)
    lower_bound = Column(Float)
    upper_bound = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    fitting = relationship("Fitting", back_populates="parameters_list")


class Constraint(Base):
    """Parameter constraint equation model."""
    __tablename__ = "constraints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fitting_id = Column(UUID(as_uuid=True), ForeignKey("fittings.id"), nullable=False)
    phase_id = Column(UUID(as_uuid=True), ForeignKey("phases.id"))
    target_variable = Column(String(100), nullable=False)  # e.g., 'lat(1)', 'x(2)'
    formula = Column(String(500), nullable=False)  # e.g., '@1 + 0.5'
    parsed_formula = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    fitting = relationship("Fitting", back_populates="constraints")
