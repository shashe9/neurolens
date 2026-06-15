import uuid
from datetime import datetime, date, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.models import Child, Observation, MilestoneStatus, First, DevelopmentalDomain
from app.services.report_service import get_persistent_concerns, calculate_observation_quality
from app.services.focus_detection_service import analyze_developmental_focus, detect_blind_spots, generate_visit_prep

def build_child_profile(db: Session, child_id: uuid.UUID) -> Dict[str, Any]:
    """
    Constructs a dynamic child developmental profile based on real database records.
    No hardcoded values are returned.
    """
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise ValueError("Child profile not found.")

    # Calculate exact age in months
    age_months = (datetime.utcnow().date() - child.date_of_birth).days // 30

    # Retrieve all observations
    observations = db.query(Observation).filter(
        Observation.child_id == child_id,
        Observation.deleted_at.is_(None)
    ).all()

    # Retrieve domains
    domains = db.query(DevelopmentalDomain).all()
    domain_map = {d.id: d.name for d in domains}

    # Count observations per domain
    domain_counts = {d.name.lower().replace(" ", "_"): 0 for d in domains}
    for obs in observations:
        if obs.domain_id and obs.domain_id in domain_map:
            d_name = domain_map[obs.domain_id].lower().replace(" ", "_")
            domain_counts[d_name] = domain_counts.get(d_name, 0) + 1

    # Sorting domains by active counts
    active_domains_sorted = sorted(
        [d for d in domain_counts],
        key=lambda d: domain_counts[d],
        reverse=True
    )
    
    most_active = [d for d in active_domains_sorted if domain_counts[d] > 0]
    least_active = [d for d in active_domains_sorted if domain_counts[d] == 0]

    # Strong vs underrepresented domains
    strong_domains = [d for d in domain_counts if domain_counts[d] >= 3]
    # Underrepresented domains (coverage < 2 in last 30 days)
    blind_spots = detect_blind_spots(db, child_id, observations)
    underrepresented_domains = [bs["domain_name"].lower().replace(" ", "_") for bs in blind_spots]

    # Focus themes from focus detection service
    focus_themes_raw = analyze_developmental_focus(observations)
    recent_focus_themes = [f["theme"] for f in focus_themes_raw]

    # Confirmed Firsts
    firsts = db.query(First).filter(First.child_id == child_id).all()
    recent_firsts = [f.first_title for f in firsts]

    # Concerns
    persistent_raw = get_persistent_concerns(db, child_id)
    persistent_concerns = [p["first_occurrence"]["body"] for p in persistent_raw]

    # Quality check
    quality_data = calculate_observation_quality(observations)
    observation_quality = quality_data.get("quality_level", "Sparse")

    # Visit details
    visit_prep = generate_visit_prep(db, child_id, observations)
    visit_discussion_topics = visit_prep.get("suggested_topics", [])

    # Growth signals (verbal/motor/play indicators in text)
    growth_signals = []
    text_corpus = " ".join([o.body.lower() for o in observations])
    if "point" in text_corpus or "pointed" in text_corpus:
        growth_signals.append("pointing_gesture")
    if "speak" in text_corpus or "word" in text_corpus or "say" in text_corpus:
        growth_signals.append("verbal_expression")
    if "stack" in text_corpus or "block" in text_corpus:
        growth_signals.append("block_play")

    # Recommended skills/targets based on age range not yet achieved
    achieved_milestone_ids = {
        ms.milestone_id for ms in db.query(MilestoneStatus).filter(
            MilestoneStatus.child_id == child_id,
            MilestoneStatus.status.in_(["observed", "consistently_demonstrated", "achieved"])
        ).all()
    }
    
    # We suggest targets that match the child's age band and are not yet achieved
    from app.models.models import Milestone
    unachieved_age_milestones = db.query(Milestone).filter(
        Milestone.age_range_low <= age_months,
        Milestone.age_range_high >= age_months,
        ~Milestone.id.in_(achieved_milestone_ids) if achieved_milestone_ids else True
    ).limit(5).all()
    
    recommended_targets = [m.title for m in unachieved_age_milestones]

    return {
        "age_months": age_months,
        "strong_domains": strong_domains,
        "underrepresented_domains": underrepresented_domains,
        "recent_focus_themes": recent_focus_themes,
        "recent_firsts": recent_firsts,
        "persistent_concerns": persistent_concerns,
        "observation_quality": observation_quality,
        "most_active_domains": most_active,
        "least_active_domains": least_active,
        "visit_discussion_topics": visit_discussion_topics,
        "growth_signals": growth_signals,
        "recommended_targets": recommended_targets,
        "domain_counts": domain_counts
    }
