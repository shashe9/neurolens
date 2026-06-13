import uuid
from datetime import datetime, date
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Child, Parent, Observation, ObservationType, ObservationMilestoneEvidence
from app.services.evidence_service import link_observation_to_milestone
from app.schemas.schemas import (
    ObservationCreate,
    ObservationUpdate,
    ObservationResponse,
    ObservationStatsResponse
)
from app.api.dependencies import get_current_parent
from app.models.models import parent_child_links

router = APIRouter()

@router.post("/children/{child_id}/observations", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED)
def create_observation(
    child_id: uuid.UUID, 
    obs_in: ObservationCreate, 
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    # Verify child profile exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
        )

    # Check parent-child link ownership
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have access to this child profile."
        )
        
    parent = db.query(Parent).filter(Parent.id == obs_in.parent_id).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent profile not found."
        )

    # Verify obs_in.parent_id matches authenticated parent
    if obs_in.parent_id != current_parent.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot log observation using another parent's identifier."
        )

    # Create observation record (milestone_id is omitted from database model)
    db_obs = Observation(
        child_id=child_id,
        parent_id=obs_in.parent_id,
        body=obs_in.body,
        entry_type=obs_in.entry_type,
        domain_id=obs_in.domain_id,
        observed_at=obs_in.observed_at,
        context_note=obs_in.context_note,
        location=obs_in.location,
        observer_relation=obs_in.observer_relation,
        is_regression=obs_in.is_regression
    )
    db.add(db_obs)
    db.commit()
    db.refresh(db_obs)

    # Link milestone in junction table if provided
    if obs_in.milestone_id:
        try:
            link_observation_to_milestone(
                db=db,
                child_id=child_id,
                milestone_id=obs_in.milestone_id,
                observation_id=db_obs.id
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to link milestone: {str(e)}"
            )

    return db_obs

@router.get("/children/{child_id}/observations", response_model=List[ObservationResponse])
def list_observations(
    child_id: uuid.UUID,
    domain_id: Optional[int] = None,
    entry_type: Optional[ObservationType] = None,
    date_start: Optional[date] = None,
    date_end: Optional[date] = None,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    # Verify child profile exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
        )

    # Check parent-child link ownership
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have access to this child profile."
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
def get_observation_stats(
    child_id: uuid.UUID, 
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    # Verify child profile exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
        )

    # Check parent-child link ownership
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have access to this child profile."
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
def get_observation(
    id: uuid.UUID, 
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    obs = db.query(Observation).filter(
        Observation.id == id,
        Observation.deleted_at.is_(None)
    ).first()
    if not obs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Observation not found."
        )

    # Verify parent-child ownership of this observation's target child
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == obs.child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have access to the target child profile."
        )

    return obs

@router.put("/observations/{id}", response_model=ObservationResponse)
def update_observation(
    id: uuid.UUID, 
    obs_in: ObservationUpdate, 
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    obs = db.query(Observation).filter(
        Observation.id == id,
        Observation.deleted_at.is_(None)
    ).first()
    if not obs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Observation not found."
        )

    # Verify parent-child ownership
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == obs.child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have access to the target child profile."
        )

    # Apply updates dynamically
    update_data = obs_in.model_dump(exclude_unset=True)
    milestone_id_update = update_data.pop("milestone_id", None) if "milestone_id" in update_data else None

    for field, value in update_data.items():
        setattr(obs, field, value)

    # If milestone_id is updated, handle mapping inside junction table
    if milestone_id_update is not None or "milestone_id" in obs_in.model_dump(exclude_unset=True):
        # Drop previous linkages
        db.query(ObservationMilestoneEvidence).filter(
            ObservationMilestoneEvidence.observation_id == obs.id
        ).delete()
        db.commit()

        # Link new one if it is not null
        if milestone_id_update:
            try:
                link_observation_to_milestone(
                    db=db,
                    child_id=obs.child_id,
                    milestone_id=milestone_id_update,
                    observation_id=obs.id
                )
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to update milestone linkage: {str(e)}"
                )

    db.commit()
    db.refresh(obs)
    return obs

@router.delete("/observations/{id}", response_model=ObservationResponse)
def delete_observation(
    id: uuid.UUID, 
    deleted_by: uuid.UUID, 
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    # Verify parameter matches credentials
    if deleted_by != current_parent.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Authorization context does not match."
        )

    obs = db.query(Observation).filter(
        Observation.id == id,
        Observation.deleted_at.is_(None)
    ).first()
    if not obs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Observation not found."
        )

    # Verify parent-child ownership
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == obs.child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have access to the target child profile."
        )

    # Soft delete: update metadata and commit
    obs.deleted_at = datetime.utcnow()
    obs.deleted_by = deleted_by

    db.commit()
    db.refresh(obs)
    return obs
