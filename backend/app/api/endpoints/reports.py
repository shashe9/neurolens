import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.schemas import ReportCreate, ReportResponse
from app.services.report_service import generate_report
from app.models.models import Report, Parent, parent_child_links
from app.api.dependencies import get_current_parent

router = APIRouter()

@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    report_in: ReportCreate, 
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    # Check parent-child link ownership
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == report_in.child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have access to this child profile."
        )

    try:
        db_report = generate_report(db, child_id=report_in.child_id, visit_id=report_in.visit_id)
        return db_report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report snapshot: {str(e)}"
        )

@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: uuid.UUID, 
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinician report snapshot not found."
        )

    # Check parent-child link ownership for the child this report belongs to
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == report.child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have access to this report profile."
        )

    return report
