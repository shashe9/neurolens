import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Child, Parent, Observation
from app.schemas.schemas import ObservationCreate, ObservationUpdate, ObservationDelete, ObservationResponse

router = APIRouter()

@router.post("/children/{child_id}/observations", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED)
def create_observation(child_id: uuid.UUID, obs_in: ObservationCreate, db: Session = Depends(get_db)):
    # Verify child profile exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
        )
        
    parent = db.query(Parent).filter(Parent.id == obs_in.parent_id).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent profile not found."
        )

    # Create observation record
    db_obs = Observation(
        child_id=child_id,
        parent_id=obs_in.parent_id,
        body=obs_in.body,
        entry_type=obs_in.entry_type,
        domain_id=obs_in.domain_id,
        milestone_id=obs_in.milestone_id,
        observed_at=obs_in.observed_at,
        context_note=obs_in.context_note,
        location=obs_in.location,
        observer_relation=obs_in.observer_relation,
        is_regression=obs_in.is_regression
    )
    db.add(db_obs)
    db.commit()
    db.refresh(db_obs)
    return db_obs

@router.get("/children/{child_id}/observations", response_model=List[ObservationResponse])
def list_observations(child_id: uuid.UUID, db: Session = Depends(get_db)):
    # Verify child profile exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
        )

    # List all non-deleted observations for the child, sorted by observed_at DESC
    return db.query(Observation).filter(
        Observation.child_id == child_id,
        Observation.deleted_at.is_(None)
    ).order_by(Observation.observed_at.desc()).all()

@router.get("/observations/{id}", response_model=ObservationResponse)
def get_observation(id: uuid.UUID, db: Session = Depends(get_db)):
    obs = db.query(Observation).filter(
        Observation.id == id,
        Observation.deleted_at.is_(None)
    ).first()
    if not obs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Observation not found."
        )
    return obs

@router.put("/observations/{id}", response_model=ObservationResponse)
def update_observation(id: uuid.UUID, obs_in: ObservationUpdate, db: Session = Depends(get_db)):
    obs = db.query(Observation).filter(
        Observation.id == id,
        Observation.deleted_at.is_(None)
    ).first()
    if not obs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Observation not found."
        )

    # Apply updates dynamically
    update_data = obs_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obs, field, value)

    db.commit()
    db.refresh(obs)
    return obs

@router.delete("/observations/{id}", response_model=ObservationResponse)
def delete_observation(id: uuid.UUID, deleted_by: uuid.UUID, db: Session = Depends(get_db)):
    obs = db.query(Observation).filter(
        Observation.id == id,
        Observation.deleted_at.is_(None)
    ).first()
    if not obs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Observation not found."
        )

    # Verify parent authorization exists
    parent = db.query(Parent).filter(Parent.id == deleted_by).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent authorization profile not found."
        )

    # Soft delete: update metadata and commit
    obs.deleted_at = datetime.utcnow()
    obs.deleted_by = deleted_by

    db.commit()
    db.refresh(obs)
    return obs
