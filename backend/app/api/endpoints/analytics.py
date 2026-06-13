import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.models import (
    Parent,
    Child,
    AISuggestionEvent,
    SuggestionFeedback,
    Milestone,
    Observation,
    HumanValidationSession,
    InteractionType,
    parent_child_links
)
from app.api.dependencies import get_current_parent

router = APIRouter()

@router.get("/caregiver/{child_id}", status_code=status.HTTP_200_OK)
def get_caregiver_analytics(
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

    suggestions_reviewed = db.query(AISuggestionEvent).filter(
        AISuggestionEvent.child_id == child_id
    ).count()

    helpful_votes = db.query(SuggestionFeedback).filter(
        SuggestionFeedback.child_id == child_id,
        SuggestionFeedback.feedback_type == "helpful"
    ).count()

    total_feedback = db.query(SuggestionFeedback).filter(
        SuggestionFeedback.child_id == child_id
    ).count()

    return {
        "suggestions_reviewed": suggestions_reviewed,
        "helpful_votes": helpful_votes,
        "total_feedback": total_feedback
    }


@router.get("/judge", status_code=status.HTTP_200_OK)
def get_judge_analytics(
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    # Global Suggestion Statistics
    total_suggestions = db.query(AISuggestionEvent).count()
    accepted_suggestions = db.query(AISuggestionEvent).filter(
        AISuggestionEvent.interaction_type == InteractionType.ACCEPTED
    ).count()
    overridden_suggestions = db.query(AISuggestionEvent).filter(
        AISuggestionEvent.interaction_type == InteractionType.OVERRIDDEN
    ).count()
    ignored_suggestions = db.query(AISuggestionEvent).filter(
        AISuggestionEvent.interaction_type == InteractionType.IGNORED
    ).count()
    manual_only_suggestions = db.query(AISuggestionEvent).filter(
        AISuggestionEvent.interaction_type == InteractionType.MANUAL_ONLY
    ).count()

    # Global Feedback Statistics
    helpful_votes = db.query(SuggestionFeedback).filter(
        SuggestionFeedback.feedback_type == "helpful"
    ).count()
    not_helpful_votes = db.query(SuggestionFeedback).filter(
        SuggestionFeedback.feedback_type == "not_helpful"
    ).count()

    # Rates
    acceptance_rate = float(accepted_suggestions) / total_suggestions if total_suggestions > 0 else 0.0
    total_feedback_votes = helpful_votes + not_helpful_votes
    helpfulness_rate = float(helpful_votes) / total_feedback_votes if total_feedback_votes > 0 else 0.0

    # Dataset Sizes
    total_milestones = db.query(Milestone).count()
    total_observations = db.query(Observation).filter(
        Observation.deleted_at.is_(None)
    ).count()

    # Human Validation Study Summary
    validation_count = db.query(HumanValidationSession).count()
    validation_stats = db.query(
        func.avg(HumanValidationSession.usability_score),
        func.avg(HumanValidationSession.trust_score),
        func.avg(HumanValidationSession.report_usefulness_score)
    ).first()

    role_stats_raw = db.query(
        HumanValidationSession.role,
        func.count(HumanValidationSession.id),
        func.avg(HumanValidationSession.usability_score),
        func.avg(HumanValidationSession.trust_score),
        func.avg(HumanValidationSession.report_usefulness_score)
    ).group_by(HumanValidationSession.role).all()

    role_metrics = {}
    for role, count, usability, trust, usefulness in role_stats_raw:
        role_metrics[role] = {
            "count": count,
            "avg_usability": round(float(usability or 0.0), 2),
            "avg_trust": round(float(trust or 0.0), 2),
            "avg_usefulness": round(float(usefulness or 0.0), 2)
        }

    return {
        "total_suggestions": total_suggestions,
        "accepted_suggestions": accepted_suggestions,
        "overridden_suggestions": overridden_suggestions,
        "ignored_suggestions": ignored_suggestions,
        "manual_only_suggestions": manual_only_suggestions,
        "acceptance_rate": round(acceptance_rate, 4),
        
        "helpful_votes": helpful_votes,
        "not_helpful_votes": not_helpful_votes,
        "helpfulness_rate": round(helpfulness_rate, 4),
        
        "total_milestones": total_milestones,
        "total_observations": total_observations,
        
        "validation_sessions_count": validation_count,
        "avg_usability": round(float(validation_stats[0] or 0.0), 2) if validation_stats else 0.0,
        "avg_trust": round(float(validation_stats[1] or 0.0), 2) if validation_stats else 0.0,
        "avg_usefulness": round(float(validation_stats[2] or 0.0), 2) if validation_stats else 0.0,
        "role_metrics": role_metrics,
        
        # Hardcoded baseline benchmark stats from repository evidence
        "benchmark_metrics": {
            "top_1_accuracy": 0.8062,
            "top_3_accuracy": 0.9625,
            "domain_accuracy": 0.8688
        }
    }
