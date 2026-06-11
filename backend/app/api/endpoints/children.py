import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Child, Parent, parent_child_links
from app.schemas.schemas import ChildCreate, ChildResponse, ChildUpdate, ParentResponse

router = APIRouter()

@router.get("/parent/sandbox", response_model=ParentResponse)
def get_sandbox_parent(db: Session = Depends(get_db)):
    # Retrieve or create Sandbox Parent (V1 sandbox explicit parent fallback)
    parent = db.query(Parent).filter(Parent.email == "sandbox.parent@example.com").first()
    if not parent:
        # Check if Jane Doe already exists and can be reused as the default sandbox parent
        jane = db.query(Parent).filter(Parent.email == "jane.doe@example.com").first()
        if jane:
            return jane
            
        parent = Parent(
            first_name="Sandbox",
            last_name="Parent",
            email="sandbox.parent@example.com"
        )
        db.add(parent)
        db.commit()
        db.refresh(parent)
    return parent

@router.post("", response_model=ChildResponse, status_code=status.HTTP_201_CREATED)
def create_child(child_in: ChildCreate, db: Session = Depends(get_db)):
    # Validate required fields
    if not child_in.first_name.strip() or not child_in.last_name.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="First name and last name are required and cannot be empty."
        )

    # Create child object
    db_child = Child(
        first_name=child_in.first_name.strip(),
        last_name=child_in.last_name.strip(),
        date_of_birth=child_in.date_of_birth,
        gender=child_in.gender.strip() if child_in.gender else None
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

@router.get("", response_model=List[ChildResponse])
def list_children(
    parent_id: Optional[uuid.UUID] = None,
    include_archived: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Child)
    
    # Filter by soft-delete status
    if not include_archived:
        query = query.filter(Child.deleted_at.is_(None))
        
    # Filter by parent link if provided
    if parent_id:
        query = query.join(Child.parents).filter(Parent.id == parent_id)
        
    return query.all()

@router.get("/{child_id}", response_model=ChildResponse)
def get_child(child_id: uuid.UUID, db: Session = Depends(get_db)):
    # Standard query fetches children even if archived for report history audit trails
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
        )
    return child

@router.put("/{child_id}", response_model=ChildResponse)
def update_child(child_id: uuid.UUID, child_in: ChildUpdate, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
        )

    # Validate inputs
    update_data = child_in.model_dump(exclude_unset=True)
    if "first_name" in update_data and not update_data["first_name"].strip():
        raise HTTPException(status_code=422, detail="First name cannot be empty.")
    if "last_name" in update_data and not update_data["last_name"].strip():
        raise HTTPException(status_code=422, detail="Last name cannot be empty.")

    # Apply updates
    for field, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(child, field, value)

    db.commit()
    db.refresh(child)
    return child

@router.delete("/{child_id}", response_model=ChildResponse)
def archive_child(child_id: uuid.UUID, deleted_by: uuid.UUID, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
        )

    parent = db.query(Parent).filter(Parent.id == deleted_by).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent authorization profile not found."
        )

    # Soft delete: mark child as archived (leaves observations/visits/reports untouched)
    child.deleted_at = datetime.utcnow()
    child.deleted_by = deleted_by

    db.commit()
    db.refresh(child)
    return child

@router.post("/{child_id}/restore", response_model=ChildResponse)
def restore_child(child_id: uuid.UUID, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
        )

    # Restore from archive
    child.deleted_at = None
    child.deleted_by = None

    db.commit()
    db.refresh(child)
    return child
