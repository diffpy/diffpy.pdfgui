"""File upload database model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base


class UploadedFile(Base):
    """Uploaded file metadata model."""
    __tablename__ = "uploaded_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # stru, pdb, cif, xyz, gr, dat, chi
    storage_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    checksum = Column(String(64))  # SHA-256
    parsed_content = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="uploaded_files")
    project = relationship("Project", back_populates="uploaded_files")
