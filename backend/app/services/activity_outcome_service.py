import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.models import ActivityOutcome, Child

def create_activity_outcome(
    db: Session,
    child_id: uuid.UUID,
    activity_id: str,
    attempted: bool,
    completed: bool,
    parent_notes: Optional[str] = None,
    observed_change: Optional[str] = None
) -> ActivityOutcome:
    """Records parent feedback and outcomes for a play activity."""
    outcome = ActivityOutcome(
        child_id=child_id,
        activity_id=activity_id,
        attempted=attempted,
        completed=completed,
        parent_notes=parent_notes,
        observed_change=observed_change,
        logged_at=datetime.utcnow()
    )
    db.add(outcome)
    db.commit()
    db.refresh(outcome)
    return outcome

def get_child_activity_outcomes(db: Session, child_id: uuid.UUID) -> List[ActivityOutcome]:
    """Retrieves all activity outcome logs for a child."""
    return db.query(ActivityOutcome).filter(
        ActivityOutcome.child_id == child_id
    ).order_by(ActivityOutcome.logged_at.desc()).all()
