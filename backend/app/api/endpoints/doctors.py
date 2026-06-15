import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import Doctor
from app.schemas.schemas import DoctorCreate, DoctorResponse

router = APIRouter()

@router.post("", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def create_doctor(doctor_in: DoctorCreate, db: Session = Depends(get_db)):
    if doctor_in.email:
        existing = db.query(Doctor).filter(Doctor.email == doctor_in.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctor with this email already exists."
            )
    
    db_doctor = Doctor(
        name=doctor_in.name,
        specialization=doctor_in.specialization,
        clinic_name=doctor_in.clinic_name,
        email=doctor_in.email,
        phone=doctor_in.phone,
        city=doctor_in.city,
        state=doctor_in.state,
        country=doctor_in.country
    )
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

@router.get("", response_model=List[DoctorResponse])
def list_doctors(db: Session = Depends(get_db)):
    return db.query(Doctor).order_by(Doctor.name.asc()).all()

@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: uuid.UUID, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found."
        )
    return doctor

@router.put("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(doctor_id: uuid.UUID, doctor_in: DoctorCreate, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found."
        )
    
    if doctor_in.email and doctor_in.email != doctor.email:
        existing = db.query(Doctor).filter(Doctor.email == doctor_in.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctor with this email already exists."
            )
            
    doctor.name = doctor_in.name
    doctor.specialization = doctor_in.specialization
    doctor.clinic_name = doctor_in.clinic_name
    doctor.email = doctor_in.email
    doctor.phone = doctor_in.phone
    doctor.city = doctor_in.city
    doctor.state = doctor_in.state
    doctor.country = doctor_in.country
    
    db.commit()
    db.refresh(doctor)
    return doctor

@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(doctor_id: uuid.UUID, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found."
        )
    db.delete(doctor)
    db.commit()
    return None
