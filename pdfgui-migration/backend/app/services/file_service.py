"""File service - handles file uploads and parsing."""

import hashlib
import os
from pathlib import Path
from typing import Any, Dict, Optional

import aiofiles

from ..core.config import settings
from .dataset_service import DatasetService
from .structure_service import StructureService


class FileService:
    """Service for file upload and parsing operations."""

    def __init__(self):
        self.structure_service = StructureService()
        self.dataset_service = DatasetService()
        self._ensure_upload_dir()

    def _ensure_upload_dir(self):
        """Ensure upload directory exists."""
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    async def save_upload(self, content: bytes, filename: str, user_id: str) -> Dict[str, Any]:
        """Save uploaded file and return metadata."""
        # Generate unique filename
        checksum = hashlib.sha256(content).hexdigest()
        ext = Path(filename).suffix.lower()
        storage_name = f"{user_id}_{checksum}{ext}"
        storage_path = os.path.join(settings.UPLOAD_DIR, storage_name)

        # Save file
        async with aiofiles.open(storage_path, "wb") as f:
            await f.write(content)

        # Determine file type
        file_type = self._get_file_type(ext)

        return {
            "filename": filename,
            "file_type": file_type,
            "storage_path": storage_path,
            "file_size": len(content),
            "checksum": checksum,
        }

    def _get_file_type(self, ext: str) -> str:
        """Determine file type from extension."""
        type_map = {
            ".stru": "stru",
            ".pdb": "pdb",
            ".cif": "cif",
            ".xyz": "xyz",
            ".gr": "gr",
            ".dat": "dat",
            ".chi": "chi",
            ".ddp": "ddp",
        }
        return type_map.get(ext, "unknown")

    def parse_file(self, filepath: str, file_type: str) -> Dict[str, Any]:
        """Parse file content based on type."""
        if file_type in ["stru", "pdb", "cif", "xyz"]:
            return self.structure_service.read_structure_file(filepath, file_type)
        elif file_type in ["gr", "dat", "chi"]:
            return self.dataset_service.read_data_file(filepath)
        elif file_type == "ddp":
            return {"type": "project", "needs_special_handling": True}
        else:
            raise ValueError(f"Unknown file type: {file_type}")

    def validate_file(self, filename: str) -> bool:
        """Validate file extension is allowed."""
        ext = Path(filename).suffix.lower()
        return ext in settings.ALLOWED_EXTENSIONS

    async def delete_file(self, storage_path: str) -> bool:
        """Delete uploaded file."""
        try:
            if os.path.exists(storage_path):
                os.remove(storage_path)
            return True
        except Exception:
            return False

    def get_file_preview(self, filepath: str, file_type: str, max_lines: int = 50) -> Dict[str, Any]:
        """Get file preview with basic info."""
        preview = {"type": file_type, "lines": []}

        # Read first N lines
        with open(filepath, "r") as f:
            for i, line in enumerate(f):
                if i >= max_lines:
                    preview["truncated"] = True
                    break
                preview["lines"].append(line.rstrip())

        # Add parsed info
        try:
            parsed = self.parse_file(filepath, file_type)
            preview["parsed"] = {
                "atom_count": parsed.get("atom_count", 0),
                "point_count": parsed.get("point_count", 0),
                "lattice": parsed.get("lattice", {}),
            }
        except Exception as e:
            preview["parse_error"] = str(e)

        return preview
