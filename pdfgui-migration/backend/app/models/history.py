"""Run history and plot configuration models."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..core.database import Base


class RunHistory(Base):
    """Run history/audit trail model."""

    __tablename__ = "run_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    fitting_id = Column(UUID(as_uuid=True), ForeignKey("fittings.id"))
    action_type = Column(String(50), nullable=False)
    input_params = Column(JSON, default=dict)
    output_results = Column(JSON, default=dict)
    wizard_state = Column(JSON, default=dict)
    execution_time = Column(Float)
    status = Column(String(20))
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="run_history")
    fitting = relationship("Fitting", back_populates="run_history")


class PlotConfig(Base):
    """Saved plot configuration model."""

    __tablename__ = "plot_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fitting_id = Column(UUID(as_uuid=True), ForeignKey("fittings.id"), nullable=False)
    plot_type = Column(String(50), nullable=False)  # pdf, structure, parameters, series
    config = Column(JSON, default=dict)
    data_series = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    fitting = relationship("Fitting", back_populates="plot_configs")


class SeriesData(Base):
    """Temperature/doping series data model."""

    __tablename__ = "series_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    series_type = Column(String(20), nullable=False)  # temperature, doping
    series_values = Column(JSON, default=list)
    fitting_ids = Column(JSON, default=list)
    extracted_params = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="series_data")
