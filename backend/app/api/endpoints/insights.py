import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Parent, Child, parent_child_links, DevelopmentalDomain, Observation, MilestoneStatus, Milestone, ObservationType
from app.api.dependencies import get_current_parent
from app.services.change_detection_service import detect_and_save_changes
from app.services.focus_detection_service import (
    analyze_developmental_focus,
    detect_blind_spots,
    generate_visit_prep
)

router = APIRouter()

@router.get("/{child_id}/trends", status_code=status.HTTP_200_OK)
def get_insights_trends(
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

    domains = db.query(DevelopmentalDomain).all()
    now = datetime.utcnow()
    t90 = now - timedelta(days=90)
    t45 = now - timedelta(days=45)

    trends = []
    for d in domains:
        # 1. Activity count (last 90 days)
        activity_count = db.query(Observation).filter(
            Observation.child_id == child_id,
            Observation.domain_id == d.id,
            Observation.observed_at >= t90,
            Observation.deleted_at.is_(None)
        ).count()

        # Map activity count to 1-5 score
        if activity_count == 0:
            activity_score = 1
        elif activity_count <= 2:
            activity_score = 2
        elif activity_count <= 5:
            activity_score = 3
        elif activity_count <= 9:
            activity_score = 4
        else:
            activity_score = 5

        # 2. Variety direction (milestones achieved in current 45 days vs previous 45-90 days)
        current_milestones = db.query(MilestoneStatus).join(Milestone).filter(
            MilestoneStatus.child_id == child_id,
            Milestone.domain_id == d.id,
            MilestoneStatus.status == "observed",
            MilestoneStatus.updated_at >= t45
        ).count()

        previous_milestones = db.query(MilestoneStatus).join(Milestone).filter(
            MilestoneStatus.child_id == child_id,
            Milestone.domain_id == d.id,
            MilestoneStatus.status == "observed",
            MilestoneStatus.updated_at >= t90,
            MilestoneStatus.updated_at < t45
        ).count()

        if current_milestones > previous_milestones:
            variety_direction = "up"
        elif current_milestones < previous_milestones:
            variety_direction = "down"
        else:
            variety_direction = "stable"

        trends.append({
            "domain_name": d.name,
            "activity_score": activity_score,
            "variety_direction": variety_direction
        })

    return {"trends": trends}


@router.get("/{child_id}/changes", status_code=status.HTTP_200_OK)
def get_insights_changes(
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

    changes = detect_and_save_changes(db, child_id)
    return {"changes": changes}


@router.get("/{child_id}/developmental-focus", status_code=status.HTTP_200_OK)
def get_developmental_focus(
    child_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    # Verify parent-child link ownership
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

    observations = db.query(Observation).filter(
        Observation.child_id == child_id,
        Observation.deleted_at.is_(None)
    ).all()

    focus = analyze_developmental_focus(observations)
    return {"focus": focus}


@router.get("/{child_id}/blind-spots", status_code=status.HTTP_200_OK)
def get_blind_spots_api(
    child_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    # Verify parent-child link ownership
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

    observations = db.query(Observation).filter(
        Observation.child_id == child_id,
        Observation.deleted_at.is_(None)
    ).all()

    blind_spots = detect_blind_spots(db, child_id, observations)
    return {"blind_spots": blind_spots}


@router.get("/{child_id}/visit-prep", status_code=status.HTTP_200_OK)
def get_visit_prep_api(
    child_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    # Verify parent-child link ownership
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

    observations = db.query(Observation).filter(
        Observation.child_id == child_id,
        Observation.deleted_at.is_(None)
    ).all()

    prep = generate_visit_prep(db, child_id, observations)
    return prep


from app.schemas.schemas import (
    SnapshotResponse,
    GrowthStoryResponse,
    FirstCreate,
    FirstResponse,
    RecommendationsPayload
)
from app.services.developmental_intelligence_service import (
    generate_child_snapshot,
    generate_growth_story,
    generate_monthly_change_summary,
    generate_monthly_questions
)
from app.services.recommendation_service import get_personalized_recommendations
from app.models.models import First
from typing import List, Optional

@router.get("/{child_id}/snapshot", response_model=SnapshotResponse, status_code=status.HTTP_200_OK)
def get_child_snapshot_api(
    child_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    # Verify child profile exists and ownership
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child profile not found.")
    
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: You do not have access to this child profile.")
        
    return generate_child_snapshot(db, child_id)


@router.get("/{child_id}/growth-story", response_model=GrowthStoryResponse, status_code=status.HTTP_200_OK)
def get_growth_story_api(
    child_id: uuid.UUID,
    month: Optional[str] = None,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child profile not found.")
    
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: You do not have access to this child profile.")

    return generate_growth_story(db, child_id, month_str=month)


@router.get("/{child_id}/monthly-change", response_model=List[str], status_code=status.HTTP_200_OK)
def get_monthly_change_api(
    child_id: uuid.UUID,
    month: Optional[str] = None,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child profile not found.")
    
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: You do not have access to this child profile.")

    return generate_monthly_change_summary(db, child_id, month_str=month)


@router.get("/{child_id}/firsts", response_model=List[FirstResponse], status_code=status.HTTP_200_OK)
def get_firsts_api(
    child_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child profile not found.")
    
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: You do not have access to this child profile.")

    return db.query(First).filter(First.child_id == child_id).order_by(First.first_date.desc()).all()


@router.post("/{child_id}/firsts", response_model=FirstResponse, status_code=status.HTTP_201_CREATED)
def create_first_api(
    child_id: uuid.UUID,
    first_in: FirstCreate,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child profile not found.")
    
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: You do not have access to this child profile.")

    db_first = First(
        child_id=child_id,
        is_first=True,
        first_title=first_in.first_title,
        first_date=first_in.first_date,
        linked_observation_id=first_in.linked_observation_id
    )
    db.add(db_first)
    db.commit()
    db.refresh(db_first)
    return db_first


@router.get("/{child_id}/monthly-questions", response_model=List[str], status_code=status.HTTP_200_OK)
def get_monthly_questions_api(
    child_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child profile not found.")
    
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: You do not have access to this child profile.")

    return generate_monthly_questions(db, child_id)


@router.get("/{child_id}/recommendations", response_model=RecommendationsPayload, status_code=status.HTTP_200_OK)
def get_recommendations_api(
    child_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child profile not found.")
    
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: You do not have access to this child profile.")

    return get_personalized_recommendations(db, child_id)


from app.services.companion_timeline_service import get_companion_timeline
from app.services.learning_path_service import generate_personalized_learning_path

@router.get("/{child_id}/concern-evolution", status_code=status.HTTP_200_OK)
def get_concern_evolution_api(
    child_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child profile not found.")
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: You do not have access to this child profile.")

    domains = db.query(DevelopmentalDomain).all()
    now = datetime.utcnow()
    t30 = now - timedelta(days=30)
    t60 = now - timedelta(days=60)

    evolution_report = []
    for d in domains:
        obs_30d = db.query(Observation).filter(
            Observation.child_id == child_id,
            Observation.domain_id == d.id,
            Observation.entry_type == ObservationType.CONCERN,
            Observation.observed_at >= t30,
            Observation.deleted_at.is_(None)
        ).all()

        obs_60d = db.query(Observation).filter(
            Observation.child_id == child_id,
            Observation.domain_id == d.id,
            Observation.entry_type == ObservationType.CONCERN,
            Observation.observed_at >= t60,
            Observation.observed_at < t30,
            Observation.deleted_at.is_(None)
        ).all()

        logging_density = len(obs_30d)
        
        # Determine confidence
        if logging_density < 2:
            confidence = "Low"
            reason = "Insufficient recent observations"
        elif logging_density < 5:
            confidence = "Medium"
            reason = "Moderate recent log frequency"
        else:
            confidence = "High"
            reason = "Frequent caregiver entries"

        # Weighted scores
        weighted_30d = sum(getattr(o, "quality_score", 1.0) for o in obs_30d)
        weighted_60d = sum(getattr(o, "quality_score", 1.0) for o in obs_60d)

        # Trend check
        if len(obs_30d) == 0 and len(obs_60d) == 0:
            continue  # omit domains without any concerns in 60d
        
        if weighted_30d < weighted_60d:
            trend = "Improving"
        elif weighted_30d > weighted_60d:
            trend = "Increasing"
        else:
            trend = "Stable"

        evolution_report.append({
            "domain_name": d.name,
            "trend": trend,
            "confidence": confidence,
            "reason": reason,
            "logging_density": logging_density,
            "weighted_score_30d": round(weighted_30d, 2),
            "weighted_score_60d": round(weighted_60d, 2)
        })

    return {"evolution": evolution_report}


@router.get("/{child_id}/companion-timeline", status_code=status.HTTP_200_OK)
def get_companion_timeline_api(
    child_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child profile not found.")
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: You do not have access to this child profile.")

    return get_companion_timeline(db, child_id)


@router.get("/{child_id}/learning-path", status_code=status.HTTP_200_OK)
def get_learning_path_api(
    child_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child profile not found.")
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: You do not have access to this child profile.")

    return generate_personalized_learning_path(db, child_id)


