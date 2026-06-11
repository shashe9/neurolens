import uuid
from datetime import datetime
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from app.models.models import (
    Child,
    Milestone,
    MilestoneStatus,
    Observation,
    ObservationMilestoneEvidence,
    DevelopmentalDomain
)

def link_observation_to_milestone(
    db: Session,
    child_id: uuid.UUID,
    milestone_id: uuid.UUID,
    observation_id: uuid.UUID
) -> ObservationMilestoneEvidence:
    """
    Creates a many-to-many linkage between a parent observation and a developmental milestone.
    Validates that:
    1. The child profile is active (not archived).
    2. The observation belongs to the child context.
    3. The observation is active (not soft-deleted).
    4. Duplicate links are blocked.
    """
    # 1. Fetch child record and verify active status
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise ValueError(f"Child profile with ID {child_id} not found.")
    
    if child.deleted_at is not None:
        raise ValueError("Archived children cannot link new evidence.")

    # 2. Fetch milestone record
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise ValueError(f"Milestone with ID {milestone_id} not found.")

    # 3. Fetch observation record
    observation = db.query(Observation).filter(Observation.id == observation_id).first()
    if not observation:
        raise ValueError(f"Observation with ID {observation_id} not found.")

    # 4. Cross-child validation (Observation must belong to target child)
    if observation.child_id != child_id:
        raise ValueError("Observation child context does not match the target child.")

    # 5. Soft-deleted observation validation
    if observation.deleted_at is not None:
        raise ValueError("Soft-deleted observations cannot be linked as evidence.")

    # 6. Prevent duplicate links
    existing_link = db.query(ObservationMilestoneEvidence).filter(
        ObservationMilestoneEvidence.observation_id == observation_id,
        ObservationMilestoneEvidence.milestone_id == milestone_id
    ).first()
    if existing_link:
        raise ValueError("This observation is already linked to the milestone.")

    # Create and commit new evidence link
    new_link = ObservationMilestoneEvidence(
        observation_id=observation_id,
        milestone_id=milestone_id
    )
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return new_link

def unlink_observation_from_milestone(
    db: Session,
    child_id: uuid.UUID,
    milestone_id: uuid.UUID,
    observation_id: uuid.UUID
) -> None:
    """
    Removes a linkage between a parent observation and a milestone.
    Validates that:
    1. The child profile is active (not archived).
    2. The observation context belongs to the child.
    """
    # 1. Verify child active status (archived child data is fully read-only)
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise ValueError(f"Child profile with ID {child_id} not found.")
    
    if child.deleted_at is not None:
        raise ValueError("Archived children cannot unlink evidence.")

    # 2. Fetch link
    link = db.query(ObservationMilestoneEvidence).filter(
        ObservationMilestoneEvidence.observation_id == observation_id,
        ObservationMilestoneEvidence.milestone_id == milestone_id
    ).first()
    
    if not link:
        raise ValueError("Evidence linkage not found.")

    # 3. Verify ownership
    observation = db.query(Observation).filter(Observation.id == observation_id).first()
    if observation and observation.child_id != child_id:
        raise ValueError("Observation child context does not match the target child.")

    db.delete(link)
    db.commit()

def list_evidence_for_milestone(db: Session, child_id: uuid.UUID, milestone_id: uuid.UUID) -> List[Observation]:
    """
    Query active (non-soft-deleted) observations for child_id linked to milestone_id.
    """
    return db.query(Observation).join(ObservationMilestoneEvidence).filter(
        Observation.child_id == child_id,
        Observation.deleted_at.is_(None),
        ObservationMilestoneEvidence.milestone_id == milestone_id
    ).all()

def get_domain_coverage(db: Session, child_id: uuid.UUID) -> List[Dict[str, Any]]:
    """
    Calculates evidence coverage metrics per developmental domain.
    Returns:
    - Domain Name
    - Milestone Count (total milestones in the domain)
    - Milestones with evidence (milestones having >= 1 active supporting observation)
    - Milestones without evidence (milestones having 0 active supporting observations)
    - Observation Count (total active observations logged under this domain for this child)
    - Evidence Count (total junction linkages under this domain for this child)
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise ValueError(f"Child profile with ID {child_id} not found.")

    domains = db.query(DevelopmentalDomain).all()
    results = []

    for dom in domains:
        milestones = db.query(Milestone).filter(Milestone.domain_id == dom.id).all()
        milestone_count = len(milestones)
        
        milestones_with_evidence = 0
        mil_ids = [m.id for m in milestones]
        
        # Total active observations logged under this domain
        obs_count = db.query(Observation).filter(
            Observation.child_id == child_id,
            Observation.domain_id == dom.id,
            Observation.deleted_at.is_(None)
        ).count()

        # Count milestone evidence
        evidence_count = 0
        if mil_ids:
            # Query junction table linked to active observations for this child
            evidence_count = db.query(ObservationMilestoneEvidence).join(Observation).filter(
                Observation.child_id == child_id,
                Observation.deleted_at.is_(None),
                ObservationMilestoneEvidence.milestone_id.in_(mil_ids)
            ).count()

            for mil in milestones:
                has_active_evidence = db.query(ObservationMilestoneEvidence).join(Observation).filter(
                    Observation.child_id == child_id,
                    Observation.deleted_at.is_(None),
                    ObservationMilestoneEvidence.milestone_id == mil.id
                ).first() is not None
                
                if has_active_evidence:
                    milestones_with_evidence += 1

        results.append({
            "domain_name": dom.name,
            "milestone_count": milestone_count,
            "milestones_with_evidence": milestones_with_evidence,
            "milestones_without_evidence": milestone_count - milestones_with_evidence,
            "observation_count": obs_count,
            "evidence_count": evidence_count
        })

    return results

# TODO (Major Issue 2): Future derived status suggestions based on evidence count:
# 0 evidence -> not_observed
# 1 observation -> emerging
# 2+ observations -> observed
# Human/clinician option override -> consistently_demonstrated
