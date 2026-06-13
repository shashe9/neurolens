import uuid
from datetime import datetime, date
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from app.models.models import ObservationType, InteractionType

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


# ==========================================
# Observation Intelligence Engine (OIE) Schemas
# ==========================================

class DomainSuggestion(BaseModel):
    domain_name: str
    relevance_score: float
    relevance_label: str

    @field_validator("relevance_label")
    @classmethod
    def validate_label(cls, v: str) -> str:
        valid_labels = {"Strong relevance", "Moderate relevance", "Possible relevance", "Weakly relevant"}
        if v not in valid_labels:
            raise ValueError(f"Relevance label must be one of: {valid_labels}")
        return v


class ObservationSuggestion(BaseModel):
    milestone_id: uuid.UUID
    title: str
    relevance_score: float
    relevance_label: str
    translated_terms: List[Dict[str, str]] = Field(default_factory=list)
    domain_name: str
    age_band_relevance: str
    explanation_text: str

    @field_validator("relevance_label")
    @classmethod
    def validate_label(cls, v: str) -> str:
        valid_labels = {"Strong relevance", "Moderate relevance", "Possible relevance", "Weakly relevant"}
        if v not in valid_labels:
            raise ValueError(f"Relevance label must be one of: {valid_labels}")
        return v



class AISuggestRequest(BaseModel):
    observation_text: str
    child_id: uuid.UUID
    child_age_months: int

    @field_validator("observation_text")
    @classmethod
    def validate_observation_text(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 10:
            raise ValueError("Observation details must be at least 10 non-whitespace characters long.")
        if len(cleaned) > 1000:
            raise ValueError("Observation details cannot exceed 1000 characters.")
        return cleaned

    @field_validator("child_age_months")
    @classmethod
    def validate_age(cls, v: int) -> int:
        if v < 0 or v > 120:
            raise ValueError("Child age must be between 0 and 120 months.")
        return v


class AISuggestResponse(BaseModel):
    domains: List[DomainSuggestion]
    milestones: List[ObservationSuggestion]
    observation_patterns: List[str]
    report_keywords: List[str]
    explanations: List[str]
    event_id: uuid.UUID
    model_version: str


class AIConfirmRequest(BaseModel):
    selected_domain: Optional[str] = None
    selected_milestone_id: Optional[uuid.UUID] = None
    interaction_type: InteractionType


# ==========================================
# Feedback Schemas
# ==========================================
class FeedbackCreate(BaseModel):
    parent_id: uuid.UUID
    child_id: uuid.UUID
    ai_suggestion_event_id: Optional[uuid.UUID] = None
    milestone_id: uuid.UUID
    feedback_type: str = Field(..., description="helpful or not_helpful")
    comment: Optional[str] = None

    @field_validator("feedback_type")
    @classmethod
    def validate_feedback_type(cls, v: str) -> str:
        valid_types = {"helpful", "not_helpful"}
        if v not in valid_types:
            raise ValueError(f"Feedback type must be one of: {valid_types}")
        return v

class FeedbackResponse(BaseModel):
    id: uuid.UUID
    parent_id: uuid.UUID
    child_id: uuid.UUID
    ai_suggestion_event_id: Optional[uuid.UUID] = None
    milestone_id: uuid.UUID
    feedback_type: str
    comment: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Human Validation Schemas
# ==========================================
class HumanValidationSessionCreate(BaseModel):
    participant_id: str = Field(..., max_length=100)
    role: str = Field(..., max_length=100, description="Caregiver, Clinician, Judge, Researcher")
    usability_score: int = Field(..., ge=1, le=5)
    trust_score: int = Field(..., ge=1, le=5)
    report_usefulness_score: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None

class HumanValidationSessionResponse(BaseModel):
    id: uuid.UUID
    participant_id: str
    role: str
    usability_score: int
    trust_score: int
    report_usefulness_score: int
    comments: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


