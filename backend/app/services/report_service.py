import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.models import (
    Child,
    ClinicalVisit,
    Milestone,
    MilestoneStatus,
    Observation,
    ObservationMilestoneEvidence,
    Report,
    ObservationType,
    ActivityOutcome,
    RecommendationFeedback
)
from app.services.evidence_service import get_domain_coverage

def generate_report(db: Session, child_id: uuid.UUID, visit_id: Optional[uuid.UUID] = None) -> Report:
    """
    Compiles child demographics, historian details, qualitative observations,
    milestone matrices, and clinical visit context into a single immutable
    JSON snapshot representing the Clinician Report.
    """
    # 1. Fetch child record
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise ValueError(f"Child profile with ID {child_id} not found.")

    # Calculate approximate chronological age
    # (Since this is a sandbox v1, we can use simple math or months)
    days_old = (datetime.utcnow().date() - child.date_of_birth).days
    approx_months = int(days_old / 30.4)

    # 2. Assemble Child Demographics
    child_data = {
        "id": str(child.id),
        "first_name": child.display_first_name,
        "last_name": child.display_last_name,
        "date_of_birth": child.date_of_birth.isoformat(),
        "gender": child.gender,
        "chronological_age": f"{approx_months} months"
    }

    # 3. Assemble Parent details
    parents_data = []
    for parent in child.parents:
        # Resolve relationship type from link table if available
        # Simple default relationship for V1
        parents_data.append({
            "id": str(parent.id),
            "first_name": parent.first_name,
            "last_name": parent.last_name,
            "email": parent.email,
            "relationship": "Parent"
        })

    # 4. Gather qualitative observations (excluding soft-deleted ones, ordered by observed_at DESC)
    active_observations = db.query(Observation).filter(
        Observation.child_id == child_id,
        Observation.deleted_at.is_(None)
    ).order_by(Observation.observed_at.desc()).all()

    observations_data = []
    for obs in active_observations:
        observations_data.append({
            "id": str(obs.id),
            "entry_type": obs.entry_type.value if hasattr(obs.entry_type, "value") else str(obs.entry_type),
            "body": obs.body,
            "domain": obs.domain.name if obs.domain else None,
            "milestone": obs.milestone_evidences[0].milestone.title if obs.milestone_evidences else None,
            "observed_at": obs.observed_at.isoformat(),
            "context_note": obs.context_note,
            "location": obs.location,
            "observer_relation": obs.observer_relation,
            "is_regression": obs.is_regression,
            "recurrence_group_id": str(obs.recurrence_group_id) if obs.recurrence_group_id else None
        })

    # 5. Gather milestone statuses and evidence mapping
    milestones = db.query(Milestone).all()
    status_map = {s.milestone_id: s for s in child.milestone_statuses}
    
    # Query active evidence links for the child
    evidence_links = db.query(ObservationMilestoneEvidence).join(Observation).filter(
        Observation.child_id == child_id,
        Observation.deleted_at.is_(None)
    ).all()
    
    evidence_map = {}
    for link in evidence_links:
        evidence_map.setdefault(link.milestone_id, []).append(link.observation)

    milestones_data = []
    for m in milestones:
        m_status = status_map.get(m.id)
        status_val = m_status.status if m_status else "not_observed"
        notes_val = m_status.notes if m_status else None
        observed_date_val = m_status.observed_date.isoformat() if (m_status and m_status.observed_date) else None

        sources_list = []
        for src in m.sources:
            sources_list.append({
                "title": src.title,
                "organization": src.organization,
                "year": src.year
            })

        m_evidence = evidence_map.get(m.id, [])
        evidence_ids = [str(obs.id) for obs in m_evidence]

        # Calculate structured evidence date ranges
        first_evidence_date = None
        last_evidence_date = None
        if m_evidence:
            sorted_m_evidence = sorted(m_evidence, key=lambda o: o.observed_at)
            first_evidence_date = sorted_m_evidence[0].observed_at.date().isoformat()
            last_evidence_date = sorted_m_evidence[-1].observed_at.date().isoformat()

        milestones_data.append({
            "id": str(m.id),
            "domain": m.domain.name,
            "title": m.title,
            "description": m.description,
            "age_range": f"{m.age_range_low}-{m.age_range_high} Months",
            "status": status_val,
            "observed_date": observed_date_val,
            "notes": notes_val,
            "sources": sources_list,
            "evidence_count": len(m_evidence),
            "evidence_observation_ids": evidence_ids,
            "first_evidence_date": first_evidence_date,
            "last_evidence_date": last_evidence_date
        })

    # 6. Gather Clinical Visit details
    visit_data = {}
    visit_record = None
    if visit_id:
        visit_record = db.query(ClinicalVisit).filter(ClinicalVisit.id == visit_id).first()
    
    # Fallback to the latest visit if no ID is specified
    if not visit_record:
        visit_record = db.query(ClinicalVisit).filter(ClinicalVisit.child_id == child_id).order_by(ClinicalVisit.visit_date.desc()).first()

    if visit_record:
        if visit_record.child_id != child_id:
            raise ValueError("Clinical visit context does not match the specified child record.")
        clinician_name = visit_record.doctor.name if getattr(visit_record, 'doctor', None) else visit_record.clinician_name
        visit_data = {
            "id": str(visit_record.id),
            "date": visit_record.visit_date.isoformat(),
            "clinician": clinician_name,
            "priority": visit_record.visit_priority,
            "concern_level": visit_record.concern_level,
            "primary_concern_note": visit_record.concern_note
        }

    # 7. Calculate provenance details for observations
    concern_obs = [o for o in active_observations if o.entry_type == ObservationType.CONCERN]
    milestone_obs = [o for o in active_observations if o.entry_type == ObservationType.MILESTONE]
    general_obs = [o for o in active_observations if o.entry_type == ObservationType.GENERAL]

    def build_section(key, title, obs_list, contribution):
        count = len(obs_list)
        if count > 0:
            # Sort chronologically to get boundaries
            sorted_obs = sorted(obs_list, key=lambda o: o.observed_at)
            start = sorted_obs[0].observed_at.date().isoformat()
            end = sorted_obs[-1].observed_at.date().isoformat()
        else:
            start = None
            end = None
            
        return {
            "section_key": key,
            "title": title,
            "observation_count": count,
            "period_start": start,
            "period_end": end,
            "source_observations": [{"id": str(o.id), "contribution": contribution} for o in obs_list]
        }

    report_sections = [
        build_section("primary_concerns", "Primary Developmental Concerns", concern_obs, "primary_evidence"),
        build_section("milestone_evidence", "Milestone-Specific Evidence", milestone_obs, "milestone_verification"),
        build_section("general_logs", "General Developmental Logs", general_obs, "general_timeline")
    ]

    # 8. Calculate Evidence Coverage Summary per domain (Major Issue 3 & report recommendation)
    domain_coverage_list = get_domain_coverage(db, child_id)
    coverage_summary = {}
    for item in domain_coverage_list:
        coverage_summary[item["domain_name"]] = {
            "total_milestones": item["milestone_count"],
            "supported_milestones": item["milestones_with_evidence"],
            "total_evidence_observations": item["evidence_count"]
        }

    # Compile parent summary narrative text
    active_domains = [item["domain_name"] for item in domain_coverage_list if item["evidence_count"] > 0]
    domain_list_str = ", ".join(active_domains) if active_domains else "developmental areas"
    achieved_titles = [m["title"] for m in milestones_data if m["status"] in ["observed", "consistently_demonstrated"]]
    
    from app.services.focus_detection_service import generate_parent_narrative
    narrative_text = generate_parent_narrative(db, child_id, active_observations)
    obs_count = len(active_observations)

    # Compute parent effort summary
    if obs_count > 0:
        sorted_obs = sorted(active_observations, key=lambda o: o.observed_at)
        days_diff = (sorted_obs[-1].observed_at - sorted_obs[0].observed_at).days
        weeks_count = max(1, round(days_diff / 7.0))
        active_domains = {o.domain.name for o in active_observations if o.domain}
        domain_names = ", ".join(list(active_domains)[:3]) if active_domains else "developmental domains"
        effort_text = f"Over the past {weeks_count} weeks, {obs_count} observations were recorded across {domain_names}."
    else:
        effort_text = "No observations recorded yet. We encourage logging a few moments each week to build a complete growth timeline."

    parent_effort_summary = {
        "text": effort_text,
        "total_observations": obs_count,
        "completed_activities_count": db.query(ActivityOutcome).filter(ActivityOutcome.child_id == child_id, ActivityOutcome.completed == True).count(),
        "attempted_activities_count": db.query(ActivityOutcome).filter(ActivityOutcome.child_id == child_id, ActivityOutcome.attempted == True).count(),
        "guides_read_count": db.query(RecommendationFeedback).filter(RecommendationFeedback.child_id == child_id, RecommendationFeedback.recommendation_type == "guide", RecommendationFeedback.opened_at.is_not(None)).count()
    }

    # Compute clusters for clinician brief
    from app.services.clustering_service import cluster_observations
    clusters = cluster_observations(active_observations)

    # 9. Calculate longitudinal intelligence metrics
    persistent_concerns = get_persistent_concerns(db, child_id)
    quality_data = calculate_observation_quality(active_observations)

    prior_report = db.query(Report).filter(
        Report.child_id == child_id
    ).order_by(Report.generated_at.desc()).first()

    visit_delta = None
    if prior_report:
        visit_delta = compute_visit_delta(
            prior_report.report_json,
            child_data,
            parents_data,
            visit_data,
            coverage_summary,
            active_observations,
            milestones_data
        )

    # 9.5 Get recommendations for reports
    from app.services.recommendation_service import get_personalized_recommendations
    try:
        recs = get_personalized_recommendations(db, child_id)
    except Exception as e:
        recs = {
            "activities": [],
            "guides": [],
            "child_profile": {
                "visit_discussion_topics": [],
                "underrepresented_domains": [],
                "growth_signals": []
            },
            "next_observations": []
        }

    # 10. Package the dual V2 report payload
    report_payload = {
        "metadata": {
            "platform": "Neurolens V2",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "version": "2.0.0",
            "observation_count": len(active_observations),
            "milestone_count": len([m for m in milestones_data if m["status"] in ["observed", "consistently_demonstrated"]]),
            "concern_count": len([o for o in active_observations if o.entry_type == ObservationType.CONCERN]),
            "visit_count": len(child.visits),
            "observation_ids_used": [str(o.id) for o in active_observations],
            "milestone_ids_used": [str(m["id"]) for m in milestones_data if m["status"] in ["observed", "consistently_demonstrated"]],
            "concern_ids_used": [str(o.id) for o in active_observations if o.entry_type == ObservationType.CONCERN],
            "top_observations": [o.body for o in active_observations[:3]]
        },
        "parent_summary": {
            "narrative": narrative_text,
            "key_achievements": achieved_titles[:5],
            "logged_moments_count": obs_count,
            "recommended_activities": recs["activities"],
            "recommended_guides": recs["guides"],
            "suggested_discussion_topics": recs["child_profile"]["visit_discussion_topics"],
            "observation_blind_spots": recs["child_profile"]["underrepresented_domains"],
            "learning_opportunities": recs["next_observations"],
            "growth_highlights": recs["child_profile"]["growth_signals"],
            "parent_effort": parent_effort_summary
        },
        "clinician_brief": {
            "demographics": child_data,
            "parents": parents_data,
            "visit_context": visit_data,
            "domain_summaries": coverage_summary,
            "excerpts": observations_data,
            "milestone_matrix": milestones_data,
            "clusters": clusters,
            "persistent_concerns": persistent_concerns,
            "visit_delta": visit_delta,
            "quality_data": quality_data
        },
        # V1 Backward Compatibility keys
        "child": child_data,
        "parents": parents_data,
        "visit_context": visit_data,
        "report_sections": report_sections,
        "evidence": observations_data,
        "milestones": milestones_data,
        "coverage_summary": coverage_summary,
        
        # Longitudinal keys at root
        "persistent_concerns": persistent_concerns,
        "visit_delta": visit_delta,
        "quality_data": quality_data
    }

    # 11. Create Report in Database
    new_report = Report(
        child_id=child.id,
        visit_id=visit_record.id if visit_record else None,
        report_json=report_payload,
        status="final"
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    return new_report


def get_persistent_concerns(db: Session, child_id: uuid.UUID) -> list:
    """Queries child concern observations and groups them by recurrence_group_id if they span 2+ weeks."""
    concerns = db.query(Observation).filter(
        Observation.child_id == child_id,
        Observation.entry_type == ObservationType.CONCERN,
        Observation.recurrence_group_id.isnot(None),
        Observation.deleted_at.is_(None)
    ).order_by(Observation.observed_at.asc()).all()

    groups = {}
    for c in concerns:
        groups.setdefault(c.recurrence_group_id, []).append(c)

    persistent = []
    for group_id, obs_list in groups.items():
        if len(obs_list) < 2:
            continue
        earliest = obs_list[0]
        latest = obs_list[-1]
        span_days = (latest.observed_at - earliest.observed_at).days
        if span_days < 14:
            continue

        persistent.append({
            "recurrence_group_id": str(group_id),
            "first_occurrence": {
                "observed_at": earliest.observed_at.isoformat(),
                "body": earliest.body
            },
            "latest_occurrence": {
                "observed_at": latest.observed_at.isoformat(),
                "body": latest.body
            },
            "total_mentions": len(obs_list),
            "supporting_excerpts": [
                {
                    "id": str(o.id),
                    "body": o.body,
                    "observed_at": o.observed_at.isoformat(),
                    "observer_relation": o.observer_relation,
                    "location": o.location
                } for o in obs_list
            ]
        })
    return persistent


def compute_visit_delta(prior_json: dict, current_demographics: dict, current_parents: list, current_visit_context: dict, current_coverage: dict, current_observations: list, current_milestones: list) -> dict:
    """Compares the current snapshot data with the prior visit report snapshot to generate a structured delta."""
    prior_brief = prior_json.get("clinician_brief", {})
    if not prior_brief:
        prior_brief = prior_json
        
    prior_excerpts = prior_brief.get("excerpts", [])
    if not prior_excerpts:
        prior_excerpts = prior_json.get("evidence", [])
        
    prior_concerns = [o for o in prior_excerpts if o.get("entry_type") == "concern"]
    current_concerns = [o for o in current_observations if o.entry_type == ObservationType.CONCERN]
    
    prior_group_ids = {c.get("recurrence_group_id") for c in prior_concerns if c.get("recurrence_group_id")}
    current_group_ids = {str(c.recurrence_group_id) for c in current_concerns if c.recurrence_group_id}
    
    # Resolved concerns: prior concerns whose group_id is not in current_group_ids
    resolved_concerns = []
    for c in prior_concerns:
        g_id = c.get("recurrence_group_id")
        if g_id is None or g_id not in current_group_ids:
            resolved_concerns.append({
                "id": c.get("id"),
                "body": c.get("body"),
                "observed_at": c.get("observed_at")
            })
            
    # New concerns: current concerns whose group_id is not in prior_group_ids
    new_concerns = []
    for c in current_concerns:
        g_id = str(c.recurrence_group_id) if c.recurrence_group_id else None
        if g_id is None or g_id not in prior_group_ids:
            new_concerns.append({
                "id": str(c.id),
                "body": c.body,
                "observed_at": c.observed_at.isoformat()
            })
            
    # Persistent concerns: current concerns whose group_id is in both
    persistent_concerns = []
    for c in current_concerns:
        g_id = str(c.recurrence_group_id) if c.recurrence_group_id else None
        if g_id is not None and g_id in prior_group_ids:
            persistent_concerns.append({
                "id": str(c.id),
                "body": c.body,
                "observed_at": c.observed_at.isoformat()
            })
            
    # New Milestones Observed
    prior_milestones = prior_brief.get("milestone_matrix", [])
    if not prior_milestones:
        prior_milestones = prior_json.get("milestones", [])
    prior_status_map = {m.get("id"): m.get("status") for m in prior_milestones}
    
    new_milestones_observed = []
    for m in current_milestones:
        curr_status = m["status"]
        prior_status = prior_status_map.get(m["id"], "not_observed")
        if curr_status in ["observed", "consistently_demonstrated"] and prior_status not in ["observed", "consistently_demonstrated"]:
            new_milestones_observed.append({
                "id": m["id"],
                "title": m["title"],
                "domain": m["domain"],
                "status": curr_status
            })
            
    # New Regressions
    prior_regression_ids = {o.get("id") for o in prior_excerpts if o.get("is_regression")}
    new_regressions = []
    for o in current_observations:
        if o.is_regression and str(o.id) not in prior_regression_ids:
            new_regressions.append({
                "id": str(o.id),
                "body": o.body,
                "observed_at": o.observed_at.isoformat()
            })
            
    # Domain coverage change
    prior_coverage = prior_brief.get("domain_summaries", {})
    if not prior_coverage:
        prior_coverage = prior_json.get("coverage_summary", {})
        
    domain_coverage_change = {}
    for d_name, curr_cov in current_coverage.items():
        p_cov = prior_coverage.get(d_name, {})
        p_count = p_cov.get("total_evidence_observations", 0)
        c_count = curr_cov.get("total_evidence_observations", 0)
        domain_coverage_change[d_name] = {
            "prior": p_count,
            "current": c_count,
            "delta": c_count - p_count
        }
        
    return {
        "prior_visit_date": prior_brief.get("visit_context", {}).get("date") or prior_json.get("metadata", {}).get("generated_at"),
        "new_concerns": new_concerns,
        "persistent_concerns": persistent_concerns,
        "resolved_concerns": resolved_concerns,
        "new_milestones_observed": new_milestones_observed,
        "new_regressions": new_regressions,
        "domain_coverage_change": domain_coverage_change
    }


def calculate_observation_quality(active_observations: list) -> dict:
    """Deterministically rates observation quality (Regular/Intermittent/Sparse) and calculates metadata."""
    total_count = len(active_observations)
    if total_count == 0:
        return {
            "quality_level": "Sparse",
            "observation_period": "No observations logged",
            "total_observations": 0,
            "domains_represented": "0 of 6"
        }
    
    dates = sorted([o.observed_at.date() for o in active_observations])
    unique_dates = sorted(list(set(dates)))
    domains = {o.domain_id for o in active_observations if o.domain_id is not None}
    domains_represented_count = len(domains)
    
    period_start = dates[0].strftime("%b %Y")
    period_end = dates[-1].strftime("%b %Y")
    if period_start == period_end:
        period_str = period_start
    else:
        period_str = f"{period_start} - {period_end}"
        
    if total_count < 5 or len(unique_dates) < 3 or domains_represented_count < 2:
        level = "Sparse"
    elif total_count >= 15 and len(unique_dates) >= 8 and domains_represented_count >= 4:
        level = "Regular"
    else:
        level = "Intermittent"
        
    return {
        "quality_level": level,
        "observation_period": period_str,
        "total_observations": total_count,
        "domains_represented": f"{domains_represented_count} of 6"
    }
