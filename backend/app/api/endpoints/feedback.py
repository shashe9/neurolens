import uuid
from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.models import Parent, Child, SuggestionFeedback, parent_child_links
from app.api.dependencies import get_current_parent
from app.schemas.schemas import FeedbackCreate, FeedbackResponse

router = APIRouter()

@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    request: FeedbackCreate,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    # 1. Validate child exists
    child = db.query(Child).filter(Child.id == request.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
        )

    # 2. Check parent-child link ownership
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == request.child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have access to this child profile."
        )

    try:
        feedback = SuggestionFeedback(
            parent_id=current_parent.id,
            child_id=request.child_id,
            ai_suggestion_event_id=request.ai_suggestion_event_id,
            milestone_id=request.milestone_id,
            feedback_type=request.feedback_type,
            comment=request.comment,
            created_at=datetime.utcnow()
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save suggestion feedback: {str(e)}"
        )


@router.get("", response_model=List[FeedbackResponse])
def list_feedback(
    child_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    # Validate parent-child ownership
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

    feedback_entries = db.query(SuggestionFeedback).filter(
        SuggestionFeedback.child_id == child_id
    ).order_by(SuggestionFeedback.created_at.desc()).all()
    return feedback_entries


@router.get("/stats/{child_id}", response_model=Dict[str, int])
def get_feedback_stats(
    child_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    # Validate parent-child ownership
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

    results = db.query(
        SuggestionFeedback.feedback_type,
        func.count(SuggestionFeedback.id)
    ).filter(
        SuggestionFeedback.child_id == child_id
    ).group_by(SuggestionFeedback.feedback_type).all()

    stats = {"helpful": 0, "not_helpful": 0}
    for feedback_type, count in results:
        if feedback_type in stats:
            stats[feedback_type] = count

    return stats
