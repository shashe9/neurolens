import jwt
import uuid
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Parent
from app.core.config import settings

def get_current_parent(request: Request, db: Session = Depends(get_db)) -> Parent:
    """
    Dependency that extracts the JWT token from the Authorization header,
    validates the signature, and retrieves the authenticated Parent profile.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    parent = db.query(Parent).filter(Parent.email == email).first()
    if parent is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return parent
