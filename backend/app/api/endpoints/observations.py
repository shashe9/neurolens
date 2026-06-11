import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Child, Parent, Observation
from app.schemas.schemas import ObservationCreate, ObservationResponse

router = APIRouter()

@router.post("", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED)
def create_observation(obs_in: ObservationCreate, db: Session = Depends(get_db)):
    # Verify child and parent exist
    child = db.query(Child).filter(Child.id == obs_in.child_id).first()
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child profile not found.")
        
    parent = db.query(Parent).filter(Parent.id == obs_in.parent_id).first()
    if not parent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent profile not found.")

    # Create observation
    db_obs = Observation(
        child_id=obs_in.child_id,
        parent_id=obs_in.parent_id,
        body=obs_in.body,
        entry_type=obs_in.entry_type,
        domain_id=obs_in.domain_id,
        milestone_id=obs_in.milestone_id,
        observed_at=obs_in.observed_at,
        context_note=obs_in.context_note,
        is_regression=obs_in.is_regression
    )
    db.add(db_obs)
    db.commit()
    db.refresh(db_obs)
    return db_obs

@router.get("", response_model=List[ObservationResponse])
def get_observations(child_id: Optional[uuid.UUID] = None, db: Session = Depends(get_db)):
    query = db.query(Observation)
    if child_id:
        query = query.filter(Observation.child_id == child_id)
    return query.order_by(Observation.observed_at.desc()).all()
