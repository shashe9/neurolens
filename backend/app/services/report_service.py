import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.models import Child, ClinicalVisit, MilestoneStatus, Observation, Report, ObservationType

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
        "first_name": child.first_name,
        "last_name": child.last_name,
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
            "milestone": obs.milestone.title if obs.milestone else None,
            "observed_at": obs.observed_at.isoformat(),
            "context_note": obs.context_note,
            "location": obs.location,
            "observer_relation": obs.observer_relation,
            "is_regression": obs.is_regression
        })

    # 5. Gather milestone statuses
    milestones_data = []
    for status in child.milestone_statuses:
        sources_list = []
        for src in status.milestone.sources:
            sources_list.append({
                "title": src.title,
                "organization": src.organization,
                "year": src.year
            })
            
        milestones_data.append({
            "id": str(status.milestone.id),
            "domain": status.milestone.domain.name,
            "title": status.milestone.title,
            "description": status.milestone.description,
            "age_range": f"{status.milestone.age_range_low}-{status.milestone.age_range_high} Months",
            "status": status.status,
            "observed_date": status.observed_date.isoformat() if status.observed_date else None,
            "notes": status.notes,
            "sources": sources_list
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
        visit_data = {
            "id": str(visit_record.id),
            "date": visit_record.visit_date.isoformat(),
            "clinician": visit_record.clinician_name,
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

    # 8. Package the full report payload
    report_payload = {
        "metadata": {
            "platform": "Neurolens V1",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0"
        },
        "child": child_data,
        "parents": parents_data,
        "visit_context": visit_data,
        "report_sections": report_sections,
        "evidence": observations_data,
        "milestones": milestones_data
    }

    # 8. Create Report in Database
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
