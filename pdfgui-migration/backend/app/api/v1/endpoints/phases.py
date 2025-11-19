"""Phase/structure endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....api.deps import get_current_user
from ....core.database import get_db
from ....models.project import Atom, Fitting, Phase, Project
from ....models.user import User
from ....schemas.phase import (
    AtomCreate,
    AtomResponse,
    LatticeParams,
    PairSelectionRequest,
    PDFParameters,
    PhaseCreate,
    PhaseResponse,
)

router = APIRouter()


@router.get("/fitting/{fitting_id}", response_model=List[PhaseResponse])
def list_phases(fitting_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all phases in a fitting."""
    fitting = (
        db.query(Fitting)
        .join(Project)
        .filter(Fitting.id == fitting_id, Project.user_id == current_user.id)
        .first()
    )

    if not fitting:
        raise HTTPException(status_code=404, detail="Fitting not found")

    return [
        PhaseResponse(
            id=p.id,
            name=p.name,
            space_group=p.space_group,
            lattice=(
                LatticeParams(**p.lattice_params)
                if p.lattice_params
                else LatticeParams(a=1, b=1, c=1, alpha=90, beta=90, gamma=90)
            ),
            atom_count=p.atom_count,
            pdf_parameters=PDFParameters(
                scale=p.scale_factor, delta1=p.delta1, delta2=p.delta2, sratio=p.sratio, spdiameter=p.spdiameter
            ),
            constraints=p.constraints,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in fitting.phases
    ]


@router.post("/fitting/{fitting_id}", response_model=PhaseResponse, status_code=status.HTTP_201_CREATED)
def create_phase(
    fitting_id: UUID,
    phase_data: PhaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a phase to a fitting."""
    fitting = (
        db.query(Fitting)
        .join(Project)
        .filter(Fitting.id == fitting_id, Project.user_id == current_user.id)
        .first()
    )

    if not fitting:
        raise HTTPException(status_code=404, detail="Fitting not found")

    # Create phase
    lattice = phase_data.lattice or LatticeParams(a=1, b=1, c=1, alpha=90, beta=90, gamma=90)
    phase = Phase(
        fitting_id=fitting_id,
        name=phase_data.name,
        lattice_params={
            "a": lattice.a,
            "b": lattice.b,
            "c": lattice.c,
            "alpha": lattice.alpha,
            "beta": lattice.beta,
            "gamma": lattice.gamma,
        },
    )
    db.add(phase)
    db.flush()

    # Add atoms if provided
    if phase_data.atoms:
        for i, atom_data in enumerate(phase_data.atoms):
            atom = Atom(
                phase_id=phase.id,
                index=i + 1,
                element=atom_data.element,
                x=atom_data.x,
                y=atom_data.y,
                z=atom_data.z,
                occupancy=atom_data.occupancy,
                uiso=atom_data.uiso,
            )
            db.add(atom)
        phase.atom_count = len(phase_data.atoms)

    db.commit()
    db.refresh(phase)

    return PhaseResponse(
        id=phase.id,
        name=phase.name,
        space_group=phase.space_group,
        lattice=LatticeParams(**phase.lattice_params),
        atom_count=phase.atom_count,
        pdf_parameters=PDFParameters(
            scale=phase.scale_factor,
            delta1=phase.delta1,
            delta2=phase.delta2,
            sratio=phase.sratio,
            spdiameter=phase.spdiameter,
        ),
        constraints=phase.constraints,
        created_at=phase.created_at,
        updated_at=phase.updated_at,
    )


@router.get("/{phase_id}", response_model=PhaseResponse)
def get_phase(phase_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get phase details."""
    phase = (
        db.query(Phase)
        .join(Fitting)
        .join(Project)
        .filter(Phase.id == phase_id, Project.user_id == current_user.id)
        .first()
    )

    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")

    return PhaseResponse(
        id=phase.id,
        name=phase.name,
        space_group=phase.space_group,
        lattice=(
            LatticeParams(**phase.lattice_params)
            if phase.lattice_params
            else LatticeParams(a=1, b=1, c=1, alpha=90, beta=90, gamma=90)
        ),
        atom_count=phase.atom_count,
        pdf_parameters=PDFParameters(
            scale=phase.scale_factor,
            delta1=phase.delta1,
            delta2=phase.delta2,
            sratio=phase.sratio,
            spdiameter=phase.spdiameter,
        ),
        constraints=phase.constraints,
        created_at=phase.created_at,
        updated_at=phase.updated_at,
    )


@router.put("/{phase_id}/lattice", response_model=PhaseResponse)
def update_lattice(
    phase_id: UUID,
    lattice: LatticeParams,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update lattice parameters."""
    phase = (
        db.query(Phase)
        .join(Fitting)
        .join(Project)
        .filter(Phase.id == phase_id, Project.user_id == current_user.id)
        .first()
    )

    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")

    phase.lattice_params = {
        "a": lattice.a,
        "b": lattice.b,
        "c": lattice.c,
        "alpha": lattice.alpha,
        "beta": lattice.beta,
        "gamma": lattice.gamma,
    }
    db.commit()
    db.refresh(phase)

    return PhaseResponse(
        id=phase.id,
        name=phase.name,
        space_group=phase.space_group,
        lattice=lattice,
        atom_count=phase.atom_count,
        pdf_parameters=PDFParameters(
            scale=phase.scale_factor,
            delta1=phase.delta1,
            delta2=phase.delta2,
            sratio=phase.sratio,
            spdiameter=phase.spdiameter,
        ),
        constraints=phase.constraints,
        created_at=phase.created_at,
        updated_at=phase.updated_at,
    )


@router.get("/{phase_id}/atoms", response_model=List[AtomResponse])
def list_atoms(phase_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List atoms in a phase."""
    phase = (
        db.query(Phase)
        .join(Fitting)
        .join(Project)
        .filter(Phase.id == phase_id, Project.user_id == current_user.id)
        .first()
    )

    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")

    return [
        AtomResponse(
            id=a.id,
            index=a.index,
            element=a.element,
            x=a.x,
            y=a.y,
            z=a.z,
            occupancy=a.occupancy,
            uiso=a.uiso,
            u11=a.u11,
            u22=a.u22,
            u33=a.u33,
            u12=a.u12,
            u13=a.u13,
            u23=a.u23,
            constraints=a.constraints,
        )
        for a in sorted(phase.atoms, key=lambda x: x.index)
    ]


@router.post("/{phase_id}/atoms", response_model=AtomResponse, status_code=status.HTTP_201_CREATED)
def add_atom(
    phase_id: UUID,
    atom_data: AtomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add atom to phase."""
    phase = (
        db.query(Phase)
        .join(Fitting)
        .join(Project)
        .filter(Phase.id == phase_id, Project.user_id == current_user.id)
        .first()
    )

    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")

    # Get next index
    max_index = db.query(Atom).filter(Atom.phase_id == phase_id).count()

    atom = Atom(
        phase_id=phase_id,
        index=max_index + 1,
        element=atom_data.element,
        x=atom_data.x,
        y=atom_data.y,
        z=atom_data.z,
        occupancy=atom_data.occupancy,
        uiso=atom_data.uiso,
        u11=atom_data.u11 or 0,
        u22=atom_data.u22 or 0,
        u33=atom_data.u33 or 0,
        u12=atom_data.u12 or 0,
        u13=atom_data.u13 or 0,
        u23=atom_data.u23 or 0,
    )
    db.add(atom)

    phase.atom_count = max_index + 1
    db.commit()
    db.refresh(atom)

    return AtomResponse(
        id=atom.id,
        index=atom.index,
        element=atom.element,
        x=atom.x,
        y=atom.y,
        z=atom.z,
        occupancy=atom.occupancy,
        uiso=atom.uiso,
        u11=atom.u11,
        u22=atom.u22,
        u33=atom.u33,
        u12=atom.u12,
        u13=atom.u13,
        u23=atom.u23,
        constraints=atom.constraints,
    )


@router.delete("/{phase_id}")
def delete_phase(phase_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete phase from fitting."""
    phase = (
        db.query(Phase)
        .join(Fitting)
        .join(Project)
        .filter(Phase.id == phase_id, Project.user_id == current_user.id)
        .first()
    )

    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")

    db.delete(phase)
    db.commit()

    return {"success": True}
