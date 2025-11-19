"""Project and fitting-related database models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Float, Text, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class FittingStatus(str, enum.Enum):
    """Fitting job status."""
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class SourceType(str, enum.Enum):
    """PDF data source type."""
    NEUTRON = "N"
    XRAY = "X"


class Project(Base):
    """Project container model."""
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_archived = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="projects")
    fittings = relationship("Fitting", back_populates="project", cascade="all, delete-orphan")
    uploaded_files = relationship("UploadedFile", back_populates="project")
    series_data = relationship("SeriesData", back_populates="project", cascade="all, delete-orphan")


class Fitting(Base):
    """Fitting/refinement job model."""
    __tablename__ = "fittings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(String(20), default=FittingStatus.PENDING.value)
    queue_position = Column(Integer)
    parameters = Column(JSON, default=dict)
    results = Column(JSON, default=dict)
    rw_value = Column(Float)
    chi_squared = Column(Float)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="fittings")
    phases = relationship("Phase", back_populates="fitting", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="fitting", cascade="all, delete-orphan")
    calculations = relationship("Calculation", back_populates="fitting", cascade="all, delete-orphan")
    parameters_list = relationship("Parameter", back_populates="fitting", cascade="all, delete-orphan")
    constraints = relationship("Constraint", back_populates="fitting", cascade="all, delete-orphan")
    run_history = relationship("RunHistory", back_populates="fitting")
    plot_configs = relationship("PlotConfig", back_populates="fitting", cascade="all, delete-orphan")


class Phase(Base):
    """Crystal structure phase model."""
    __tablename__ = "phases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fitting_id = Column(UUID(as_uuid=True), ForeignKey("fittings.id"), nullable=False)
    name = Column(String(255), nullable=False)
    space_group = Column(String(50))
    lattice_params = Column(JSON, default=dict)  # {a, b, c, alpha, beta, gamma}
    initial_structure = Column(JSON, default=dict)
    refined_structure = Column(JSON, default=dict)
    constraints = Column(JSON, default=dict)
    selected_pairs = Column(JSON, default=list)
    scale_factor = Column(Float, default=1.0)
    delta1 = Column(Float, default=0.0)
    delta2 = Column(Float, default=0.0)
    sratio = Column(Float, default=1.0)
    spdiameter = Column(Float, default=0.0)
    atom_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    fitting = relationship("Fitting", back_populates="phases")
    atoms = relationship("Atom", back_populates="phase", cascade="all, delete-orphan")


class Atom(Base):
    """Atom within a phase structure."""
    __tablename__ = "atoms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phase_id = Column(UUID(as_uuid=True), ForeignKey("phases.id"), nullable=False)
    index = Column(Integer, nullable=False)
    element = Column(String(10), nullable=False)
    x = Column(Float, default=0.0)
    y = Column(Float, default=0.0)
    z = Column(Float, default=0.0)
    occupancy = Column(Float, default=1.0)
    u11 = Column(Float, default=0.0)
    u22 = Column(Float, default=0.0)
    u33 = Column(Float, default=0.0)
    u12 = Column(Float, default=0.0)
    u13 = Column(Float, default=0.0)
    u23 = Column(Float, default=0.0)
    uiso = Column(Float, default=0.0)
    constraints = Column(JSON, default=dict)

    # Relationships
    phase = relationship("Phase", back_populates="atoms")


class Dataset(Base):
    """Experimental PDF dataset model."""
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fitting_id = Column(UUID(as_uuid=True), ForeignKey("fittings.id"), nullable=False)
    name = Column(String(255), nullable=False)
    source_type = Column(String(1), default=SourceType.NEUTRON.value)  # 'N' or 'X'
    qmax = Column(Float, default=32.0)
    qdamp = Column(Float, default=0.01)
    qbroad = Column(Float, default=0.0)
    dscale = Column(Float, default=1.0)
    fit_rmin = Column(Float, default=1.0)
    fit_rmax = Column(Float, default=30.0)
    fit_rstep = Column(Float, default=0.01)
    point_count = Column(Integer, default=0)
    observed_data = Column(JSON, default=dict)  # {robs: [], Gobs: [], dGobs: []}
    calculated_data = Column(JSON, default=dict)  # {rcalc: [], Gcalc: []}
    difference_data = Column(JSON, default=dict)  # {r: [], G: []}
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    fitting = relationship("Fitting", back_populates="datasets")


class Calculation(Base):
    """Theoretical PDF calculation model."""
    __tablename__ = "calculations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fitting_id = Column(UUID(as_uuid=True), ForeignKey("fittings.id"), nullable=False)
    name = Column(String(255), nullable=False)
    rmin = Column(Float, default=0.01)
    rmax = Column(Float, default=50.0)
    rstep = Column(Float, default=0.01)
    rlen = Column(Integer, default=0)
    calculated_pdf = Column(JSON, default=dict)  # {r: [], G: []}
    parameters = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    fitting = relationship("Fitting", back_populates="calculations")
