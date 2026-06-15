import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.models import RecommendationFeedback, ActivityOutcome

def calculate_parent_preference_metrics(db: Session, child_id: uuid.UUID) -> Dict[str, float]:
    """Calculates continuous parent behavioral interaction metrics from feedback logs."""
    feedback_entries = db.query(RecommendationFeedback).filter(
        RecommendationFeedback.child_id == child_id
    ).all()

    outcomes = db.query(ActivityOutcome).filter(
        ActivityOutcome.child_id == child_id
    ).all()

    # Guides counts
    guides_shown = sum(1 for f in feedback_entries if f.recommendation_type == "guide")
    guides_opened = sum(1 for f in feedback_entries if f.recommendation_type == "guide" and f.opened_at is not None)
    guides_completed = sum(1 for f in feedback_entries if f.recommendation_type == "guide" and f.completed)

    # Activities counts
    activities_shown = sum(1 for f in feedback_entries if f.recommendation_type == "activity")
    activities_opened = sum(1 for f in feedback_entries if f.recommendation_type == "activity" and f.opened_at is not None)
    
    # Completed can be tracked in feedback or outcomes table
    completed_activity_ids = {o.activity_id for o in outcomes if o.completed}
    activities_completed = sum(
        1 for f in feedback_entries 
        if f.recommendation_type == "activity" and (f.completed or f.recommendation_id in completed_activity_ids)
    )

    # Compute rates (default to 0.5 to keep a neutral midpoint if no observations)
    guide_open_rate = (guides_opened / guides_shown) if guides_shown > 0 else 0.5
    guide_completion_rate = (guides_completed / guides_opened) if guides_opened > 0 else 0.5
    activity_open_rate = (activities_opened / activities_shown) if activities_shown > 0 else 0.5
    activity_completion_rate = (activities_completed / activities_opened) if activities_opened > 0 else 0.5

    # Engagement consistency (active days out of total logs)
    total_interactions = len(feedback_entries) + len(outcomes)
    engagement_consistency = min(1.0, total_interactions / 10.0) if total_interactions > 0 else 0.1

    return {
        "guide_open_rate": round(guide_open_rate, 2),
        "guide_completion_rate": round(guide_completion_rate, 2),
        "activity_open_rate": round(activity_open_rate, 2),
        "activity_completion_rate": round(activity_completion_rate, 2),
        "engagement_consistency": round(engagement_consistency, 2)
    }

def rank_recommendations(
    db: Session,
    child_id: uuid.UUID,
    scored_activities: List[Dict[str, Any]],
    scored_guides: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Applies continuous behavioral preference weights to re-rank scored recommendations."""
    metrics = calculate_parent_preference_metrics(db, child_id)

    # Extract rates
    act_completion = metrics["activity_completion_rate"]
    act_open = metrics["activity_open_rate"]
    guide_completion = metrics["guide_completion_rate"]
    guide_open = metrics["guide_open_rate"]

    # Re-score activities
    ranked_activities = []
    for item in scored_activities:
        base_score = item["score"]
        # Boost based on activity completion preference
        boost = (act_completion * 0.4) + (act_open * 0.1)
        adjusted_score = base_score * (1.0 + boost)
        ranked_activities.append({
            **item,
            "adjusted_score": round(adjusted_score, 2)
        })

    # Re-score guides
    ranked_guides = []
    for item in scored_guides:
        base_score = item["score"]
        # Boost based on guide reading preference
        boost = (guide_completion * 0.4) + (guide_open * 0.1)
        adjusted_score = base_score * (1.0 + boost)
        ranked_guides.append({
            **item,
            "adjusted_score": round(adjusted_score, 2)
        })

    # Sort descending by adjusted score
    ranked_activities.sort(key=lambda x: x["adjusted_score"], reverse=True)
    ranked_guides.sort(key=lambda x: x["adjusted_score"], reverse=True)

    return {
        "metrics": metrics,
        "activities": ranked_activities,
        "guides": ranked_guides
    }
