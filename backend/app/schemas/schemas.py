import uuid
from datetime import datetime, date
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, EmailStr

# ==========================================
# Parent Schemas
# ==========================================
class ParentBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr

class ParentCreate(ParentBase):
    pass

class ParentResponse(ParentBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# Child Schemas
# ==========================================
class ChildBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    date_of_birth: date
    gender: str = Field(..., max_length=50)

class ChildCreate(ChildBase):
    parent_id: Optional[uuid.UUID] = None  # To link child with a parent in seed/sandbox

class ChildResponse(ChildBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# Observation Schemas
# ==========================================
class ObservationCreate(BaseModel):
    child_id: uuid.UUID
    parent_id: uuid.UUID
    body: str
    entry_type: str = Field(..., description="general_observation, concern, or milestone_observation")
    domain_id: Optional[int] = None
    milestone_id: Optional[uuid.UUID] = None
    observed_at: datetime = Field(default_factory=datetime.utcnow)
    context_note: Optional[str] = None
    is_regression: bool = False

class ObservationResponse(BaseModel):
    id: uuid.UUID
    child_id: uuid.UUID
    parent_id: uuid.UUID
    body: str
    entry_type: str
    domain_id: Optional[int] = None
    milestone_id: Optional[uuid.UUID] = None
    observed_at: datetime
    context_note: Optional[str] = None
    is_regression: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# Milestone Schemas
# ==========================================
class EvidenceSourceResponse(BaseModel):
    id: uuid.UUID
    title: str
    organization: str
    year: int
    url: Optional[str] = None

    class Config:
        from_attributes = True

class MilestoneResponse(BaseModel):
    id: uuid.UUID
    domain_id: int
    title: str
    description: str
    age_range_low: int
    age_range_high: int
    sources: List[EvidenceSourceResponse] = []

    class Config:
        from_attributes = True

# ==========================================
# Visit Schemas
# ==========================================
class VisitCreate(BaseModel):
    child_id: uuid.UUID
    visit_date: date
    clinician_name: str
    visit_priority: str = Field(..., description="routine, urgent, consultation")
    concern_level: str = Field(..., description="low, medium, high")
    concern_note: str

class VisitResponse(BaseModel):
    id: uuid.UUID
    child_id: uuid.UUID
    visit_date: date
    clinician_name: str
    visit_priority: str
    concern_level: str
    concern_note: str
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# Report Schemas
# ==========================================
class ReportCreate(BaseModel):
    child_id: uuid.UUID
    visit_id: Optional[uuid.UUID] = None

class ReportResponse(BaseModel):
    id: uuid.UUID
    child_id: uuid.UUID
    visit_id: Optional[uuid.UUID] = None
    report_json: Dict[str, Any]
    generated_at: datetime
    status: str

    class Config:
        from_attributes = True
