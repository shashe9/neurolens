import uuid
from datetime import datetime, date
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import (
    Observation, ObservationType, MilestoneStatus,
    ActivityOutcome, ClinicalVisit, First, RecommendationFeedback
)

def get_companion_timeline(db: Session, child_id: uuid.UUID) -> List[Dict[str, Any]]:
    """
    Compiles all child and parent events (observations, milestone achievements,
    firsts, activity outcomes, clinical visits, recommendation engagements)
    into a single narrative chronological stream.
    """
    timeline_events = []

    # 1. Fetch Observations
    observations = db.query(Observation).filter(
        Observation.child_id == child_id,
        Observation.deleted_at.is_(None)
    ).all()

    for obs in observations:
        event_type = "observation"
        title = "Logged Journal Entry"
        if obs.entry_type == ObservationType.CONCERN:
            event_type = "concern"
            title = "Logged Concern / Watch Item"
        elif obs.entry_type == ObservationType.MILESTONE:
            event_type = "milestone"
            title = "Logged Milestone Observation"

        timeline_events.append({
            "id": f"obs-{obs.id}",
            "type": event_type,
            "date": obs.observed_at.isoformat(),
            "title": title,
            "description": obs.body,
            "metadata": {
                "domain": obs.domain.name if obs.domain else "General",
                "location": obs.location,
                "observer_relation": obs.observer_relation,
                "quality_score": getattr(obs, "quality_score", 1.0)
            }
        })

    # 2. Fetch Milestone Achievements
    milestones = db.query(MilestoneStatus).filter(
        MilestoneStatus.child_id == child_id,
        MilestoneStatus.status.in_(["achieved", "observed", "consistently_demonstrated"])
    ).all()

    for ms in milestones:
        evt_date = ms.observed_date if ms.observed_date else ms.updated_at.date()
        dt_str = datetime.combine(evt_date, datetime.min.time()).isoformat()
        timeline_events.append({
            "id": f"ms-{ms.id}",
            "type": "milestone",
            "date": dt_str,
            "title": f"Milestone Achieved: {ms.milestone.title}",
            "description": ms.milestone.description,
            "metadata": {
                "domain": ms.milestone.domain.name,
                "age_range": f"{ms.milestone.age_range_low}-{ms.milestone.age_range_high} mo",
                "notes": ms.notes
            }
        })

    # 3. Fetch Firsts
    firsts = db.query(First).filter(First.child_id == child_id).all()
    for f in firsts:
        dt_str = datetime.combine(f.first_date, datetime.min.time()).isoformat()
        timeline_events.append({
            "id": f"first-{f.id}",
            "type": "achievement",
            "date": dt_str,
            "title": f"Celebrated First: {f.first_title} 🎉",
            "description": f"Successfully recorded and confirmed {f.first_title}.",
            "metadata": {
                "is_first": f.is_first
            }
        })

    # 4. Fetch Activity Outcomes
    outcomes = db.query(ActivityOutcome).filter(ActivityOutcome.child_id == child_id).all()
    for out in outcomes:
        timeline_events.append({
            "id": f"outcome-{out.id}",
            "type": "activity_attempt",
            "date": out.logged_at.isoformat(),
            "title": f"Activity Outcome: {'Completed' if out.completed else 'Attempted'}",
            "description": out.parent_notes or "Logged play session outcome.",
            "metadata": {
                "activity_id": out.activity_id,
                "attempted": out.attempted,
                "completed": out.completed,
                "observed_change": out.observed_change
            }
        })

    # 5. Fetch Clinical Visits
    visits = db.query(ClinicalVisit).filter(ClinicalVisit.child_id == child_id).all()
    for v in visits:
        dt_str = datetime.combine(v.visit_date, datetime.min.time()).isoformat()
        timeline_events.append({
            "id": f"visit-{v.id}",
            "type": "visit",
            "date": dt_str,
            "title": f"Clinical Visit with {v.clinician_name}",
            "description": f"Priority: {v.visit_priority.capitalize()}. Concern Level: {v.concern_level.capitalize()}.\nNote: {v.concern_note}",
            "metadata": {
                "clinician_name": v.clinician_name,
                "priority": v.visit_priority,
                "concern_level": v.concern_level
            }
        })

    # 6. Fetch Recommendation Engagements
    feedback = db.query(RecommendationFeedback).filter(
        RecommendationFeedback.child_id == child_id,
        RecommendationFeedback.opened_at.is_not(None)
    ).all()
    for fb in feedback:
        timeline_events.append({
            "id": f"feedback-{fb.id}",
            "type": "recommendation_accepted",
            "date": fb.opened_at.isoformat(),
            "title": f"Read Guide/Activity: {fb.recommendation_id}",
            "description": fb.feedback_text or f"Caregiver opened recommendation {fb.recommendation_id}.",
            "metadata": {
                "recommendation_id": fb.recommendation_id,
                "type": fb.recommendation_type,
                "completed": fb.completed,
                "helpful": fb.helpful
            }
        })

    # Sort events by date descending
    timeline_events.sort(key=lambda x: x["date"], reverse=True)
    return timeline_events
