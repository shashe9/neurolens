import uuid
from datetime import datetime, date
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Child, Parent, Observation, ObservationType
from app.schemas.schemas import (
    ObservationCreate,
    ObservationUpdate,
    ObservationResponse,
    ObservationStatsResponse
)

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
def list_observations(
    child_id: uuid.UUID,
    domain_id: Optional[int] = None,
    entry_type: Optional[ObservationType] = None,
    date_start: Optional[date] = None,
    date_end: Optional[date] = None,
    db: Session = Depends(get_db)
):
    # Verify child profile exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
        )

    # Query active observations for the child
    query = db.query(Observation).filter(
        Observation.child_id == child_id,
        Observation.deleted_at.is_(None)
    )

    # Apply filters dynamically
    if domain_id is not None:
        query = query.filter(Observation.domain_id == domain_id)
    if entry_type is not None:
        query = query.filter(Observation.entry_type == entry_type)
    if date_start is not None:
        query = query.filter(Observation.observed_at >= datetime.combine(date_start, datetime.min.time()))
    if date_end is not None:
        query = query.filter(Observation.observed_at <= datetime.combine(date_end, datetime.max.time()))

    # Sort by observed_at descending (newest first)
    return query.order_by(Observation.observed_at.desc()).all()

@router.get("/children/{child_id}/observations/stats", response_model=ObservationStatsResponse)
def get_observation_stats(child_id: uuid.UUID, db: Session = Depends(get_db)):
    # Verify child profile exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
        )

    # Query active observations
    active_obs = db.query(Observation).filter(
        Observation.child_id == child_id,
        Observation.deleted_at.is_(None)
    ).all()

    total_count = len(active_obs)

    # Calculate domain distribution
    by_domain = {}
    for obs in active_obs:
        if obs.domain:
            by_domain[obs.domain.name] = by_domain.get(obs.domain.name, 0) + 1

    # Calculate type distribution
    by_type = {}
    for obs in active_obs:
        # Resolve enum to string if needed
        val = obs.entry_type.value if hasattr(obs.entry_type, "value") else str(obs.entry_type)
        by_type[val] = by_type.get(val, 0) + 1

    active_concern_count = by_type.get("concern", 0)

    return ObservationStatsResponse(
        total_count=total_count,
        by_domain=by_domain,
        by_type=by_type,
        active_concern_count=active_concern_count
    )

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
