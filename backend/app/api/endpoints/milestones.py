from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Milestone
from app.schemas.schemas import MilestoneResponse

router = APIRouter()

@router.get("", response_model=List[MilestoneResponse])
def get_milestones(db: Session = Depends(get_db)):
    # Retrieve all milestones, loading their linked evidence sources
    return db.query(Milestone).all()
