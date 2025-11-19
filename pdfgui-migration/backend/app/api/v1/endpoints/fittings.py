"""Fitting/refinement endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ....core.database import get_db
from ....models.project import Project, Fitting, FittingStatus
from ....schemas.fitting import (
    FittingCreate, FittingResponse, FittingRun,
    FittingStatusResponse, FittingResultsResponse
)
from ....schemas.parameter import ParameterResponse, ConstraintCreate, ConstraintResponse
from ....services.fitting_service import FittingService
from ....api.deps import get_current_user
from ....models.user import User

router = APIRouter()
fitting_service = FittingService()


@router.get("/project/{project_id}", response_model=List[FittingResponse])
def list_fittings(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all fittings in a project."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return [
        FittingResponse(
            id=f.id,
            name=f.name,
            status=f.status,
            rw_value=f.rw_value,
            chi_squared=f.chi_squared,
            phase_count=len(f.phases),
            dataset_count=len(f.datasets),
            parameters=f.parameters,
            results=f.results,
            created_at=f.created_at,
            updated_at=f.updated_at,
            completed_at=f.completed_at
        )
        for f in project.fittings
    ]


@router.post("/project/{project_id}", response_model=FittingResponse, status_code=status.HTTP_201_CREATED)
def create_fitting(
    project_id: UUID,
    fitting_data: FittingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new fitting in a project."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    fitting = Fitting(
        project_id=project_id,
        name=fitting_data.name,
        status=FittingStatus.PENDING.value
    )
    db.add(fitting)
    db.commit()
    db.refresh(fitting)

    return FittingResponse(
        id=fitting.id,
        name=fitting.name,
        status=fitting.status,
        rw_value=fitting.rw_value,
        chi_squared=fitting.chi_squared,
        phase_count=0,
        dataset_count=0,
        parameters={},
        results={},
        created_at=fitting.created_at,
        updated_at=fitting.updated_at,
        completed_at=fitting.completed_at
    )


@router.get("/{fitting_id}", response_model=FittingResponse)
def get_fitting(
    fitting_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get fitting details."""
    fitting = db.query(Fitting).join(Project).filter(
        Fitting.id == fitting_id,
        Project.user_id == current_user.id
    ).first()

    if not fitting:
        raise HTTPException(status_code=404, detail="Fitting not found")

    return FittingResponse(
        id=fitting.id,
        name=fitting.name,
        status=fitting.status,
        rw_value=fitting.rw_value,
        chi_squared=fitting.chi_squared,
        phase_count=len(fitting.phases),
        dataset_count=len(fitting.datasets),
        parameters=fitting.parameters,
        results=fitting.results,
        created_at=fitting.created_at,
        updated_at=fitting.updated_at,
        completed_at=fitting.completed_at
    )


@router.post("/{fitting_id}/run", status_code=status.HTTP_202_ACCEPTED)
def run_fitting(
    fitting_id: UUID,
    run_params: FittingRun,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start refinement job."""
    fitting = db.query(Fitting).join(Project).filter(
        Fitting.id == fitting_id,
        Project.user_id == current_user.id
    ).first()

    if not fitting:
        raise HTTPException(status_code=404, detail="Fitting not found")

    if fitting.status == FittingStatus.RUNNING.value:
        raise HTTPException(status_code=400, detail="Fitting is already running")

    # Update status
    fitting.status = FittingStatus.QUEUED.value
    db.commit()

    # Queue refinement task
    # In production, this would use Celery
    # background_tasks.add_task(run_refinement_task, str(fitting_id))

    return {
        "job_id": str(fitting_id),
        "status": "QUEUED",
        "message": "Refinement job queued"
    }


@router.get("/{fitting_id}/status", response_model=FittingStatusResponse)
def get_fitting_status(
    fitting_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current refinement status."""
    fitting = db.query(Fitting).join(Project).filter(
        Fitting.id == fitting_id,
        Project.user_id == current_user.id
    ).first()

    if not fitting:
        raise HTTPException(status_code=404, detail="Fitting not found")

    return FittingStatusResponse(
        status=fitting.status,
        iteration=fitting.results.get("iteration", 0),
        current_rw=fitting.rw_value,
        elapsed_time=fitting.results.get("elapsed_time", 0)
    )


@router.post("/{fitting_id}/stop")
def stop_fitting(
    fitting_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Stop running refinement."""
    fitting = db.query(Fitting).join(Project).filter(
        Fitting.id == fitting_id,
        Project.user_id == current_user.id
    ).first()

    if not fitting:
        raise HTTPException(status_code=404, detail="Fitting not found")

    if fitting.status != FittingStatus.RUNNING.value:
        raise HTTPException(status_code=400, detail="Fitting is not running")

    fitting.status = FittingStatus.CANCELLED.value
    db.commit()

    return {"success": True, "status": "CANCELLED"}


@router.get("/{fitting_id}/parameters", response_model=List[ParameterResponse])
def get_parameters(
    fitting_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all parameters for fitting."""
    fitting = db.query(Fitting).join(Project).filter(
        Fitting.id == fitting_id,
        Project.user_id == current_user.id
    ).first()

    if not fitting:
        raise HTTPException(status_code=404, detail="Fitting not found")

    return [
        ParameterResponse(
            index=p.param_index,
            name=p.name,
            initial_value=p.initial_value,
            refined_value=p.refined_value,
            uncertainty=p.uncertainty,
            is_fixed=p.is_fixed,
            bounds={"lower": p.lower_bound, "upper": p.upper_bound}
        )
        for p in fitting.parameters_list
    ]


@router.post("/{fitting_id}/constraints", response_model=ConstraintResponse, status_code=status.HTTP_201_CREATED)
def add_constraint(
    fitting_id: UUID,
    constraint_data: ConstraintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add constraint to fitting."""
    from ....models.parameter import Constraint as ConstraintModel
    from ....services.constraint_service import ConstraintService

    fitting = db.query(Fitting).join(Project).filter(
        Fitting.id == fitting_id,
        Project.user_id == current_user.id
    ).first()

    if not fitting:
        raise HTTPException(status_code=404, detail="Fitting not found")

    # Validate formula
    constraint_service = ConstraintService()
    validation = constraint_service.validate_formula(constraint_data.formula)

    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["error"])

    # Create constraint
    constraint = ConstraintModel(
        fitting_id=fitting_id,
        phase_id=constraint_data.phase_id,
        target_variable=constraint_data.target,
        formula=constraint_data.formula
    )
    db.add(constraint)
    db.commit()
    db.refresh(constraint)

    return ConstraintResponse(
        id=constraint.id,
        target=constraint.target_variable,
        formula=constraint.formula,
        phase_id=constraint.phase_id,
        parameters_used=validation["parameters"]
    )
