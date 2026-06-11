from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Child, ClinicalVisit
from app.schemas.schemas import VisitCreate, VisitResponse

router = APIRouter()

@router.post("", response_model=VisitResponse, status_code=status.HTTP_201_CREATED)
def create_visit(visit_in: VisitCreate, db: Session = Depends(get_db)):
    # Verify child profile exists
    child = db.query(Child).filter(Child.id == visit_in.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
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
