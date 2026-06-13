from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database.session import get_db
from app.models.models import Parent
from app.core.security import verify_password, create_access_token

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    parent_id: str
    email: str

@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Validates user credentials and issues a JSON Web Token (JWT) on success.
    """
    # Case-insensitive query for email
    parent = db.query(Parent).filter(Parent.email == login_data.email.lower().strip()).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Assert password is set in DB
    if not parent.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    # Verify hash match
    if not verify_password(login_data.password, parent.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    # Create and return JWT access token
    access_token = create_access_token(subject=parent.email)
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        parent_id=str(parent.id),
        email=parent.email
    )
