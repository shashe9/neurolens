import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Child, Milestone, MilestoneStatus, Observation, ObservationMilestoneEvidence
from app.schemas.schemas import (
    MilestoneResponse,
    MilestoneEvidenceResponse,
    CoverageResponse,
    MilestoneStatusUpdate,
    EvidenceLinkRequest,
    ObservationResponse,
    QuestionnaireSubmit
)
from app.api.dependencies import get_current_parent
from app.models.models import Parent, parent_child_links
from app.services.evidence_service import (
    link_observation_to_milestone,
    unlink_observation_from_milestone,
    list_evidence_for_milestone,
    get_domain_coverage
)

router = APIRouter()

@router.get("/milestones", response_model=List[MilestoneResponse])
def get_milestones(
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    """
    Retrieve all global milestones in the system catalog.
    """
    return db.query(Milestone).all()

@router.get("/children/{child_id}/milestones", response_model=List[MilestoneEvidenceResponse])
def get_children_milestones(
    child_id: uuid.UUID, 
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    """
    Retrieves all milestones in the system catalog, populated with child-specific tracking status
    and supporting observations (evidence mapping).
    """
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

    milestones = db.query(Milestone).all()

    # Load child's milestone statuses
    child_statuses = db.query(MilestoneStatus).filter(MilestoneStatus.child_id == child_id).all()
    status_map = {s.milestone_id: s for s in child_statuses}

    # Load child's active evidence mapping
    evidence_links = db.query(ObservationMilestoneEvidence).join(Observation).filter(
        Observation.child_id == child_id,
        Observation.deleted_at.is_(None)
    ).all()

    # Group evidence observations by milestone_id
    evidence_map = {}
    for link in evidence_links:
        evidence_map.setdefault(link.milestone_id, []).append(link.observation)

    response = []
    for m in milestones:
        # Resolve status, fallback to not_observed
        m_status = status_map.get(m.id)
        status_val = m_status.status if m_status else "not_observed"

        # Resolve active supporting observations
        m_evidence = evidence_map.get(m.id, [])
        evidence_ids = [e.id for e in m_evidence]

        response.append({
            "id": m.id,
            "domain_id": m.domain_id,
            "title": m.title,
            "description": m.description,
            "age_range_low": m.age_range_low,
            "age_range_high": m.age_range_high,
            "status": status_val,
            "observed_date": m_status.observed_date if m_status else None,
            "evidence_count": len(m_evidence),
            "evidence_ids": evidence_ids,
            "evidence": m_evidence,
            "sources": m.sources
        })

    return response

@router.put("/children/{child_id}/milestones/{milestone_id}/status")
def update_child_milestone_status(
    child_id: uuid.UUID,
    milestone_id: uuid.UUID,
    status_in: MilestoneStatusUpdate,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    """
    Updates or inserts a child's milestone status record.
    Blocks update if the child context is archived.
    """
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

    # Block updates on archived children (Major Issue 7)
    if child.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Archived children cannot update milestone status."
        )

    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found."
        )

    allowed_statuses = ["not_observed", "emerging", "observed", "consistently_demonstrated"]
    if status_in.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status value. Must be one of {allowed_statuses}."
        )

    db_status = db.query(MilestoneStatus).filter(
        MilestoneStatus.child_id == child_id,
        MilestoneStatus.milestone_id == milestone_id
    ).first()

    if not db_status:
        db_status = MilestoneStatus(
            child_id=child_id,
            milestone_id=milestone_id,
            status=status_in.status,
            notes=status_in.notes,
            observed_date=datetime.utcnow().date() if status_in.status in ["observed", "consistently_demonstrated"] else None
        )
        db.add(db_status)
    else:
        db_status.status = status_in.status
        db_status.notes = status_in.notes
        if status_in.status in ["observed", "consistently_demonstrated"]:
            if not db_status.observed_date:
                db_status.observed_date = datetime.utcnow().date()
        else:
            db_status.observed_date = None

    db.commit()
    db.refresh(db_status)
    return {
        "id": db_status.id,
        "child_id": db_status.child_id,
        "milestone_id": db_status.milestone_id,
        "status": db_status.status,
        "notes": db_status.notes,
        "observed_date": db_status.observed_date.isoformat() if db_status.observed_date else None
    }

@router.get("/children/{child_id}/milestones/coverage", response_model=CoverageResponse)
def get_children_milestones_coverage(
    child_id: uuid.UUID, 
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    """
    Returns domain evidence coverage details for the child.
    """
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

    try:
        coverage = get_domain_coverage(db, child_id)
        return {"domains": coverage}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/children/{child_id}/milestones/{milestone_id}/evidence")
def link_evidence_to_milestone_api(
    child_id: uuid.UUID,
    milestone_id: uuid.UUID,
    req: EvidenceLinkRequest,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    """
    Links an observation to a milestone as supporting evidence.
    Validates child active context and child-observation ownership boundary.
    """
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

    try:
        new_link = link_observation_to_milestone(
            db=db,
            child_id=child_id,
            milestone_id=milestone_id,
            observation_id=req.observation_id
        )
        return {
            "id": str(new_link.id),
            "observation_id": str(new_link.observation_id),
            "milestone_id": str(new_link.milestone_id),
            "created_at": new_link.created_at.isoformat()
        }
    except ValueError as e:
        # Handle validation rejections with 400 Bad Request
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/children/{child_id}/milestones/{milestone_id}/evidence/{observation_id}")
def unlink_evidence_from_milestone_api(
    child_id: uuid.UUID,
    milestone_id: uuid.UUID,
    observation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    """
    Removes evidence mapping link.
    Validates archived child data is fully read-only and child ownership boundaries.
    """
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

    try:
        unlink_observation_from_milestone(
            db=db,
            child_id=child_id,
            milestone_id=milestone_id,
            observation_id=observation_id
        )
        return {"status": "success", "message": "Evidence linkage successfully removed."}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/children/{child_id}/milestones/{milestone_id}/evidence", response_model=List[ObservationResponse])
def get_milestone_evidence(
    child_id: uuid.UUID,
    milestone_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    """
    Lists supporting active observations linked to a milestone.
    """
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

    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found."
        )

    return list_evidence_for_milestone(db=db, child_id=child_id, milestone_id=milestone_id)

@router.get("/milestones/{id}", response_model=MilestoneResponse)
def get_milestone(
    id: uuid.UUID, 
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    """
    Retrieve specific milestone detail.
    """
    m = db.query(Milestone).filter(Milestone.id == id).first()
    if not m:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found."
        )
    return m


@router.post("/onboarding/questionnaire", status_code=status.HTTP_200_OK)
def submit_questionnaire(
    req: QuestionnaireSubmit,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    """
    Submits answers to the baseline developmental questionnaire.
    Saves the snapshot to the child's record and seeds MilestoneStatus records.
    """
    child = db.query(Child).filter(Child.id == req.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
        )

    # Check parent-child link ownership
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == req.child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have access to this child profile."
        )

    # 1. Update Child initial_snapshot
    child.initial_snapshot = req.snapshot

    # 2. Seed Milestone statuses based on seeds
    seeded_count = 0
    for m_id_str, status_str in req.milestone_seeds.items():
        try:
            m_uuid = uuid.UUID(m_id_str)
        except ValueError:
            continue
        
        # Check if milestone exists
        milestone = db.query(Milestone).filter(Milestone.id == m_uuid).first()
        if not milestone:
            continue

        # Upsert status
        db_status = db.query(MilestoneStatus).filter(
            MilestoneStatus.child_id == child.id,
            MilestoneStatus.milestone_id == m_uuid
        ).first()

        if not db_status:
            db_status = MilestoneStatus(
                child_id=child.id,
                milestone_id=m_uuid,
                status=status_str,
                observed_date=datetime.utcnow().date() if status_str in ["observed", "consistently_demonstrated"] else None
            )
            db.add(db_status)
        else:
            db_status.status = status_str
            if status_str in ["observed", "consistently_demonstrated"]:
                if not db_status.observed_date:
                    db_status.observed_date = datetime.utcnow().date()
            else:
                db_status.observed_date = None
        seeded_count += 1

    db.commit()
    db.refresh(child)
    return {"status": "success", "seeded_milestones_count": seeded_count}
