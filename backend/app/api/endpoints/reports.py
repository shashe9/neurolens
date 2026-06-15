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


@router.get("/debug/{child_id}")
def get_report_debug(
    child_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
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

    # Fetch latest report for child
    report = db.query(Report).filter(Report.child_id == child_id).order_by(Report.generated_at.desc()).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No clinician report found for this child."
        )

    metadata = report.report_json.get("metadata", {})
    clinician_brief = report.report_json.get("clinician_brief", {})

    observations = clinician_brief.get("excerpts", [])
    milestones = clinician_brief.get("milestone_matrix", [])
    concerns = clinician_brief.get("persistent_concerns", [])

    return {
        "report_id": str(report.id),
        "child_id": str(child_id),
        "generated_at": metadata.get("generated_at"),
        "observations_used": {
            "count": metadata.get("observation_count", len(observations)),
            "details": [obs.get("body") for obs in observations]
        },
        "milestones_used": {
            "count": metadata.get("milestone_count", len([m for m in milestones if m.get("status") in ["observed", "consistently_demonstrated"]])),
            "details": [m.get("title") for m in milestones if m.get("status") in ["observed", "consistently_demonstrated"]]
        },
        "concerns_used": {
            "count": metadata.get("concern_count", len([obs for obs in observations if obs.get("entry_type") == "concern"])),
            "details": [obs.get("body") for obs in observations if obs.get("entry_type") == "concern"]
        },
        "top_observations": metadata.get("top_observations", [obs.get("body") for obs in observations[:3]]),
        "generated_from": {
            "observation_ids": metadata.get("observation_ids_used", [obs.get("id") for obs in observations]),
            "milestone_ids": metadata.get("milestone_ids_used", [m.get("id") for m in milestones if m.get("status") in ["observed", "consistently_demonstrated"]]),
            "concern_ids": metadata.get("concern_ids_used", [obs.get("id") for obs in observations if obs.get("entry_type") == "concern"])
        }
    }

