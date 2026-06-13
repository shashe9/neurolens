import uuid
from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.models import Parent, HumanValidationSession
from app.api.dependencies import get_current_parent
from app.schemas.schemas import HumanValidationSessionCreate, HumanValidationSessionResponse

router = APIRouter()

@router.post("", response_model=HumanValidationSessionResponse, status_code=status.HTTP_201_CREATED)
def create_validation_session(
    request: HumanValidationSessionCreate,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    try:
        session = HumanValidationSession(
            participant_id=request.participant_id,
            role=request.role,
            usability_score=request.usability_score,
            trust_score=request.trust_score,
            report_usefulness_score=request.report_usefulness_score,
            comments=request.comments,
            created_at=datetime.utcnow()
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save human validation study session: {str(e)}"
        )


@router.get("", response_model=List[HumanValidationSessionResponse])
def list_validation_sessions(
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    sessions = db.query(HumanValidationSession).order_by(HumanValidationSession.created_at.desc()).all()
    return sessions


@router.get("/stats", response_model=Dict[str, Any])
def get_validation_stats(
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    total_sessions = db.query(HumanValidationSession).count()
    if total_sessions == 0:
        return {
            "total_sessions": 0,
            "avg_usability": 0.0,
            "avg_trust": 0.0,
            "avg_usefulness": 0.0,
            "by_role": {},
            "role_metrics": {}
        }

    stats = db.query(
        func.avg(HumanValidationSession.usability_score),
        func.avg(HumanValidationSession.trust_score),
        func.avg(HumanValidationSession.report_usefulness_score)
    ).first()

    role_counts_raw = db.query(
        HumanValidationSession.role,
        func.count(HumanValidationSession.id)
    ).group_by(HumanValidationSession.role).all()

    by_role = {role: count for role, count in role_counts_raw}

    # Calculate average scores specifically for each role persona (Phase 6C F-05 recommendation)
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
        "total_sessions": total_sessions,
        "avg_usability": round(float(stats[0] or 0.0), 2),
        "avg_trust": round(float(stats[1] or 0.0), 2),
        "avg_usefulness": round(float(stats[2] or 0.0), 2),
        "by_role": by_role,
        "role_metrics": role_metrics
    }
