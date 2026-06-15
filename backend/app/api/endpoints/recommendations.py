import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.session import get_db
from app.models.models import Parent, Child, parent_child_links, RecommendationFeedback, ActivityOutcome
from app.api.dependencies import get_current_parent
from app.services.recommendation_service import get_personalized_recommendations
from app.services.activity_outcome_service import create_activity_outcome

router = APIRouter()

class RecommendationFeedbackCreate(BaseModel):
    child_id: uuid.UUID
    recommendation_id: str
    recommendation_type: str  # activity, guide, question
    opened: Optional[bool] = False
    completed: Optional[bool] = False
    helpful: Optional[bool] = None
    dismissed: Optional[bool] = False
    feedback_text: Optional[str] = None

class ActivityOutcomeCreate(BaseModel):
    child_id: uuid.UUID
    activity_id: str
    attempted: bool
    completed: bool
    parent_notes: Optional[str] = None
    observed_change: Optional[str] = None


@router.get("/{child_id}", status_code=status.HTTP_200_OK)
def get_daily_recommendation(
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

    res = get_personalized_recommendations(db, child_id)
    res["recommendation_text"] = res["activities"][0]["why_recommended"] if res.get("activities") else "Try this activity."
    res["domain_name"] = "Communication"
    return res


@router.post("/feedback", status_code=status.HTTP_201_CREATED)
def post_recommendation_feedback(
    feedback_in: RecommendationFeedbackCreate,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    # Check parent-child link ownership
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == feedback_in.child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have access to this child profile."
        )

    # Check if a feedback record already exists for this recommendation to avoid duplicates
    existing = db.query(RecommendationFeedback).filter(
        RecommendationFeedback.child_id == feedback_in.child_id,
        RecommendationFeedback.recommendation_id == feedback_in.recommendation_id
    ).first()

    if existing:
        if feedback_in.opened:
            existing.opened_at = datetime.utcnow()
        if feedback_in.completed:
            existing.completed = True
        if feedback_in.helpful is not None:
            existing.helpful = feedback_in.helpful
        if feedback_in.dismissed:
            existing.dismissed = True
        if feedback_in.feedback_text:
            existing.feedback_text = feedback_in.feedback_text
        db.commit()
        db.refresh(existing)
        return existing

    db_fb = RecommendationFeedback(
        child_id=feedback_in.child_id,
        recommendation_id=feedback_in.recommendation_id,
        recommendation_type=feedback_in.recommendation_type,
        shown_at=datetime.utcnow(),
        opened_at=datetime.utcnow() if feedback_in.opened else None,
        completed=feedback_in.completed,
        helpful=feedback_in.helpful,
        dismissed=feedback_in.dismissed,
        feedback_text=feedback_in.feedback_text
    )
    db.add(db_fb)
    db.commit()
    db.refresh(db_fb)
    return db_fb


@router.post("/activity-outcomes", status_code=status.HTTP_201_CREATED)
def post_activity_outcome(
    outcome_in: ActivityOutcomeCreate,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    # Check parent-child link ownership
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == outcome_in.child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have access to this child profile."
        )

    res = create_activity_outcome(
        db=db,
        child_id=outcome_in.child_id,
        activity_id=outcome_in.activity_id,
        attempted=outcome_in.attempted,
        completed=outcome_in.completed,
        parent_notes=outcome_in.parent_notes,
        observed_change=outcome_in.observed_change
    )
    return res

