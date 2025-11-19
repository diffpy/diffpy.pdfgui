"""Dataset endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ....core.database import get_db
from ....models.project import Project, Fitting, Dataset
from ....schemas.dataset import (
    DatasetCreate, DatasetResponse, InstrumentParams, FitRange, DatasetDataResponse, DataArrays
)
from ....api.deps import get_current_user
from ....models.user import User

router = APIRouter()


@router.get("/fitting/{fitting_id}", response_model=List[DatasetResponse])
def list_datasets(
    fitting_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all datasets in a fitting."""
    fitting = db.query(Fitting).join(Project).filter(
        Fitting.id == fitting_id,
        Project.user_id == current_user.id
    ).first()

    if not fitting:
        raise HTTPException(status_code=404, detail="Fitting not found")

    return [
        DatasetResponse(
            id=d.id,
            name=d.name,
            source_type=d.source_type,
            qmax=d.qmax,
            qdamp=d.qdamp,
            qbroad=d.qbroad,
            dscale=d.dscale,
            fit_rmin=d.fit_rmin,
            fit_rmax=d.fit_rmax,
            fit_rstep=d.fit_rstep,
            point_count=d.point_count,
            metadata=d.metadata,
            created_at=d.created_at,
            updated_at=d.updated_at
        )
        for d in fitting.datasets
    ]


@router.post("/fitting/{fitting_id}", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
def create_dataset(
    fitting_id: UUID,
    dataset_data: DatasetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a dataset to a fitting."""
    fitting = db.query(Fitting).join(Project).filter(
        Fitting.id == fitting_id,
        Project.user_id == current_user.id
    ).first()

    if not fitting:
        raise HTTPException(status_code=404, detail="Fitting not found")

    dataset = Dataset(
        fitting_id=fitting_id,
        name=dataset_data.name
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return DatasetResponse(
        id=dataset.id,
        name=dataset.name,
        source_type=dataset.source_type,
        qmax=dataset.qmax,
        qdamp=dataset.qdamp,
        qbroad=dataset.qbroad,
        dscale=dataset.dscale,
        fit_rmin=dataset.fit_rmin,
        fit_rmax=dataset.fit_rmax,
        fit_rstep=dataset.fit_rstep,
        point_count=dataset.point_count,
        metadata=dataset.metadata,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at
    )


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dataset details."""
    dataset = db.query(Dataset).join(Fitting).join(Project).filter(
        Dataset.id == dataset_id,
        Project.user_id == current_user.id
    ).first()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return DatasetResponse(
        id=dataset.id,
        name=dataset.name,
        source_type=dataset.source_type,
        qmax=dataset.qmax,
        qdamp=dataset.qdamp,
        qbroad=dataset.qbroad,
        dscale=dataset.dscale,
        fit_rmin=dataset.fit_rmin,
        fit_rmax=dataset.fit_rmax,
        fit_rstep=dataset.fit_rstep,
        point_count=dataset.point_count,
        metadata=dataset.metadata,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at
    )


@router.get("/{dataset_id}/data", response_model=DatasetDataResponse)
def get_dataset_data(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get raw data arrays."""
    dataset = db.query(Dataset).join(Fitting).join(Project).filter(
        Dataset.id == dataset_id,
        Project.user_id == current_user.id
    ).first()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    observed = DataArrays(
        r=dataset.observed_data.get("robs", []),
        G=dataset.observed_data.get("Gobs", []),
        dG=dataset.observed_data.get("dGobs", [])
    )

    calculated = None
    if dataset.calculated_data:
        calculated = DataArrays(
            r=dataset.calculated_data.get("rcalc", []),
            G=dataset.calculated_data.get("Gcalc", [])
        )

    difference = None
    if dataset.difference_data:
        difference = DataArrays(
            r=dataset.difference_data.get("r", []),
            G=dataset.difference_data.get("G", [])
        )

    return DatasetDataResponse(
        observed=observed,
        calculated=calculated,
        difference=difference
    )


@router.put("/{dataset_id}/instrument", response_model=DatasetResponse)
def update_instrument_params(
    dataset_id: UUID,
    params: InstrumentParams,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update instrument parameters."""
    dataset = db.query(Dataset).join(Fitting).join(Project).filter(
        Dataset.id == dataset_id,
        Project.user_id == current_user.id
    ).first()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    dataset.source_type = params.stype
    dataset.qmax = params.qmax
    dataset.qdamp = params.qdamp
    dataset.qbroad = params.qbroad
    dataset.dscale = params.dscale

    db.commit()
    db.refresh(dataset)

    return DatasetResponse(
        id=dataset.id,
        name=dataset.name,
        source_type=dataset.source_type,
        qmax=dataset.qmax,
        qdamp=dataset.qdamp,
        qbroad=dataset.qbroad,
        dscale=dataset.dscale,
        fit_rmin=dataset.fit_rmin,
        fit_rmax=dataset.fit_rmax,
        fit_rstep=dataset.fit_rstep,
        point_count=dataset.point_count,
        metadata=dataset.metadata,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at
    )


@router.put("/{dataset_id}/fit-range", response_model=DatasetResponse)
def update_fit_range(
    dataset_id: UUID,
    fit_range: FitRange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update fitting range."""
    dataset = db.query(Dataset).join(Fitting).join(Project).filter(
        Dataset.id == dataset_id,
        Project.user_id == current_user.id
    ).first()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    dataset.fit_rmin = fit_range.rmin
    dataset.fit_rmax = fit_range.rmax
    dataset.fit_rstep = fit_range.rstep

    db.commit()
    db.refresh(dataset)

    return DatasetResponse(
        id=dataset.id,
        name=dataset.name,
        source_type=dataset.source_type,
        qmax=dataset.qmax,
        qdamp=dataset.qdamp,
        qbroad=dataset.qbroad,
        dscale=dataset.dscale,
        fit_rmin=dataset.fit_rmin,
        fit_rmax=dataset.fit_rmax,
        fit_rstep=dataset.fit_rstep,
        point_count=dataset.point_count,
        metadata=dataset.metadata,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at
    )


@router.delete("/{dataset_id}")
def delete_dataset(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete dataset from fitting."""
    dataset = db.query(Dataset).join(Fitting).join(Project).filter(
        Dataset.id == dataset_id,
        Project.user_id == current_user.id
    ).first()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    db.delete(dataset)
    db.commit()

    return {"success": True}
