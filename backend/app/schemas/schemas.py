import uuid
from datetime import datetime, date
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from app.models.models import ObservationType

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

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# Child Schemas
# ==========================================
class ChildBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    date_of_birth: date
    gender: Optional[str] = Field(None, max_length=50)

class ChildCreate(ChildBase):
    parent_id: Optional[uuid.UUID] = None  # To link child with a parent in seed/sandbox

class ChildUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=50)

class ChildResponse(ChildBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# Observation Schemas
# ==========================================
class ObservationCreate(BaseModel):
    parent_id: uuid.UUID
    body: str
    entry_type: ObservationType = Field(..., description="general, concern, or milestone")
    domain_id: Optional[int] = None
    milestone_id: Optional[uuid.UUID] = None
    observed_at: datetime = Field(default_factory=datetime.utcnow)
    context_note: Optional[str] = None
    location: Optional[str] = None
    observer_relation: Optional[str] = None
    is_regression: bool = False

    @field_validator("body")
    @classmethod
    def body_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Observation details/body cannot be empty or whitespace.")
        return v

class ObservationUpdate(BaseModel):
    body: Optional[str] = None
    entry_type: Optional[ObservationType] = None
    domain_id: Optional[int] = None
    milestone_id: Optional[uuid.UUID] = None
    observed_at: Optional[datetime] = None
    context_note: Optional[str] = None
    location: Optional[str] = None
    observer_relation: Optional[str] = None
    is_regression: Optional[bool] = None

    @field_validator("body")
    @classmethod
    def body_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Observation details/body cannot be empty or whitespace.")
        return v

class ObservationDelete(BaseModel):
    deleted_by: uuid.UUID

class ObservationResponse(BaseModel):
    id: uuid.UUID
    child_id: uuid.UUID
    parent_id: uuid.UUID
    body: str
    entry_type: ObservationType
    domain_id: Optional[int] = None
    milestone_id: Optional[uuid.UUID] = None
    observed_at: datetime
    context_note: Optional[str] = None
    location: Optional[str] = None
    observer_relation: Optional[str] = None
    is_regression: bool
    created_at: datetime
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)

class ObservationStatsResponse(BaseModel):
    total_count: int
    by_domain: Dict[str, int]
    by_type: Dict[str, int]
    active_concern_count: int

# ==========================================
# Milestone Schemas
# ==========================================
class EvidenceSourceResponse(BaseModel):
    id: uuid.UUID
    title: str
    organization: str
    year: int
    url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class MilestoneResponse(BaseModel):
    id: uuid.UUID
    domain_id: int
    title: str
    description: str
    age_range_low: int
    age_range_high: int
    sources: List[EvidenceSourceResponse] = []

    model_config = ConfigDict(from_attributes=True)

class EvidenceLinkRequest(BaseModel):
    observation_id: uuid.UUID

class MilestoneEvidenceResponse(BaseModel):
    id: uuid.UUID
    domain_id: int
    title: str
    description: str
    age_range_low: int
    age_range_high: int
    status: str  # not_observed, emerging, observed, consistently_demonstrated
    evidence_count: int
    evidence_ids: List[uuid.UUID]
    evidence: List[ObservationResponse]
    sources: List[EvidenceSourceResponse] = []

    model_config = ConfigDict(from_attributes=True)

class DomainCoverageItem(BaseModel):
    domain_name: str
    milestone_count: int
    milestones_with_evidence: int
    milestones_without_evidence: int
    observation_count: int
    evidence_count: int

class CoverageResponse(BaseModel):
    domains: List[DomainCoverageItem]

class MilestoneStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

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

    model_config = ConfigDict(from_attributes=True)

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

    model_config = ConfigDict(from_attributes=True)
