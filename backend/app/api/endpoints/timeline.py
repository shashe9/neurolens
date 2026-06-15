import uuid
from datetime import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Parent, Child, Observation, parent_child_links
from app.api.dependencies import get_current_parent
from app.services.clustering_service import cluster_observations

router = APIRouter()

@router.get("/{child_id}", status_code=status.HTTP_200_OK)
def get_timeline(
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

    # 1. Retrieve child's active observations sorted descending
    observations = db.query(Observation).filter(
        Observation.child_id == child_id,
        Observation.deleted_at.is_(None)
    ).order_by(Observation.observed_at.desc()).all()

    # 2. Group observations by Month Year
    grouped_observations = {}
    for obs in observations:
        month_year = obs.observed_at.strftime("%B %Y")
        grouped_observations.setdefault(month_year, []).append({
            "id": str(obs.id),
            "child_id": str(obs.child_id),
            "parent_id": str(obs.parent_id),
            "body": obs.body,
            "entry_type": obs.entry_type,
            "domain_id": obs.domain_id,
            "domain_name": obs.domain.name if obs.domain else "General",
            "milestone_id": str(obs.milestone_evidences[0].milestone_id) if obs.milestone_evidences else None,
            "observed_at": obs.observed_at.isoformat(),
            "context_note": obs.context_note,
            "location": obs.location,
            "observer_relation": obs.observer_relation,
            "is_regression": obs.is_regression,
            "structured_body": obs.structured_body,
            "structuring_status": obs.structuring_status,
            "created_at": obs.created_at.isoformat()
        })

    # 3. Compute semantic clusters
    clusters = cluster_observations(observations)

    return {
        "grouped_observations": grouped_observations,
        "clusters": clusters
    }
