"""File upload endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ....core.database import get_db
from ....models.file import UploadedFile
from ....services.file_service import FileService
from ....api.deps import get_current_user
from ....models.user import User
from ....core.config import settings

router = APIRouter()
file_service = FileService()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload structure or data file."""
    # Validate file
    if not file_service.validate_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )

    # Check file size
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB"
        )

    # Save file
    file_info = await file_service.save_upload(
        content,
        file.filename,
        str(current_user.id)
    )

    # Parse file content
    try:
        parsed = file_service.parse_file(
            file_info["storage_path"],
            file_info["file_type"]
        )
        file_info["parsed_content"] = parsed
    except Exception as e:
        file_info["parsed_content"] = {"error": str(e)}

    # Store in database
    uploaded_file = UploadedFile(
        user_id=current_user.id,
        filename=file_info["filename"],
        file_type=file_info["file_type"],
        storage_path=file_info["storage_path"],
        file_size=file_info["file_size"],
        checksum=file_info["checksum"],
        parsed_content=file_info.get("parsed_content", {})
    )
    db.add(uploaded_file)
    db.commit()
    db.refresh(uploaded_file)

    return {
        "id": uploaded_file.id,
        "filename": uploaded_file.filename,
        "file_type": uploaded_file.file_type,
        "file_size": uploaded_file.file_size,
        "checksum": uploaded_file.checksum,
        "preview": uploaded_file.parsed_content,
        "created_at": uploaded_file.created_at
    }


@router.get("", response_model=List[dict])
def list_files(
    file_type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List user's uploaded files."""
    query = db.query(UploadedFile).filter(
        UploadedFile.user_id == current_user.id
    )

    if file_type:
        query = query.filter(UploadedFile.file_type == file_type)

    files = query.order_by(UploadedFile.created_at.desc()).all()

    return [
        {
            "id": f.id,
            "filename": f.filename,
            "file_type": f.file_type,
            "file_size": f.file_size,
            "created_at": f.created_at
        }
        for f in files
    ]


@router.get("/{file_id}")
def get_file(
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get file metadata."""
    uploaded_file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id,
        UploadedFile.user_id == current_user.id
    ).first()

    if not uploaded_file:
        raise HTTPException(status_code=404, detail="File not found")

    return {
        "id": uploaded_file.id,
        "filename": uploaded_file.filename,
        "file_type": uploaded_file.file_type,
        "file_size": uploaded_file.file_size,
        "checksum": uploaded_file.checksum,
        "parsed_content": uploaded_file.parsed_content,
        "created_at": uploaded_file.created_at
    }


@router.get("/{file_id}/preview")
def get_file_preview(
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get parsed file preview."""
    uploaded_file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id,
        UploadedFile.user_id == current_user.id
    ).first()

    if not uploaded_file:
        raise HTTPException(status_code=404, detail="File not found")

    preview = file_service.get_file_preview(
        uploaded_file.storage_path,
        uploaded_file.file_type
    )

    return preview


@router.delete("/{file_id}")
async def delete_file(
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete uploaded file."""
    uploaded_file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id,
        UploadedFile.user_id == current_user.id
    ).first()

    if not uploaded_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete from storage
    await file_service.delete_file(uploaded_file.storage_path)

    # Delete from database
    db.delete(uploaded_file)
    db.commit()

    return {"success": True}
