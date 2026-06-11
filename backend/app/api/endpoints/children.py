import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Child, Parent, parent_child_links
from app.schemas.schemas import ChildCreate, ChildResponse

router = APIRouter()

@router.post("", response_model=ChildResponse, status_code=status.HTTP_201_CREATED)
def create_child(child_in: ChildCreate, db: Session = Depends(get_db)):
    # Create child object
    db_child = Child(
        first_name=child_in.first_name,
        last_name=child_in.last_name,
        date_of_birth=child_in.date_of_birth,
        gender=child_in.gender
    )
    db.add(db_child)
    db.commit()
    db.refresh(db_child)

    # Link to parent if parent_id is provided
    if child_in.parent_id:
        parent = db.query(Parent).filter(Parent.id == child_in.parent_id).first()
        if parent:
            db.execute(
                parent_child_links.insert().values(
                    parent_id=parent.id,
                    child_id=db_child.id,
                    relationship_type="parent"
                )
            )
            db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent with ID {child_in.parent_id} not found."
            )

    return db_child

from typing import List

@router.get("", response_model=List[ChildResponse])
def list_children(db: Session = Depends(get_db)):
    return db.query(Child).all()

@router.get("/{child_id}", response_model=ChildResponse)
def get_child(child_id: uuid.UUID, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
        )
    return child
