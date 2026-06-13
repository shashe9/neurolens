import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Child, ClinicalVisit, Parent, parent_child_links
from app.schemas.schemas import VisitCreate, VisitResponse
from app.api.dependencies import get_current_parent

router = APIRouter()

@router.post("", response_model=VisitResponse, status_code=status.HTTP_201_CREATED)
def create_visit(
    visit_in: VisitCreate, 
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    # Verify child profile exists
    child = db.query(Child).filter(Child.id == visit_in.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
        )

    # Check parent-child link ownership
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == visit_in.child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have access to this child profile."
        )

    # Save visit preparation context
    db_visit = ClinicalVisit(
        child_id=visit_in.child_id,
        visit_date=visit_in.visit_date,
        clinician_name=visit_in.clinician_name,
        visit_priority=visit_in.visit_priority,
        concern_level=visit_in.concern_level,
        concern_note=visit_in.concern_note
    )
    db.add(db_visit)
    db.commit()
    db.refresh(db_visit)
    return db_visit

@router.get("/children/{child_id}", response_model=List[VisitResponse])
def list_child_visits(
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

    visits = db.query(ClinicalVisit).filter(ClinicalVisit.child_id == child_id).order_by(ClinicalVisit.visit_date.desc()).all()
    return visits
