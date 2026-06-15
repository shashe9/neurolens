import uuid
from datetime import datetime, date
from typing import Optional, List
from enum import Enum
from sqlalchemy import String, Text, Integer, Boolean, Date, DateTime, ForeignKey, Table, Column, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base

# ==========================================
# Enums
# ==========================================

class ObservationType(str, Enum):
    GENERAL = "general"
    CONCERN = "concern"
    MILESTONE = "milestone"


class InteractionType(str, Enum):
    ACCEPTED = "accepted"
    OVERRIDDEN = "overridden"
    MANUAL_ONLY = "manual_only"
    IGNORED = "ignored"

# ==========================================
# Association Tables for Many-to-Many
# ==========================================

# Parent-Child link association table
parent_child_links = Table(
    "parent_child_links",
    Base.metadata,
    Column("parent_id", ForeignKey("parents.id", ondelete="CASCADE"), primary_key=True),
    Column("child_id", ForeignKey("children.id", ondelete="CASCADE"), primary_key=True),
    Column("relationship_type", String(50), nullable=False, default="parent")
)

# Milestone-EvidenceSource link association table
milestone_sources = Table(
    "milestone_sources",
    Base.metadata,
    Column("milestone_id", ForeignKey("milestones.id", ondelete="CASCADE"), primary_key=True),
    Column("source_id", ForeignKey("evidence_sources.id", ondelete="CASCADE"), primary_key=True)
)

# ==========================================
# Model Declarations
# ==========================================

class Parent(Base):
    __tablename__ = "parents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    children: Mapped[List["Child"]] = relationship(
        secondary=parent_child_links, back_populates="parents"
    )
    observations: Mapped[List["Observation"]] = relationship(
        foreign_keys="[Observation.parent_id]", back_populates="parent"
    )


class Child(Base):
    __tablename__ = "children"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    initial_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Soft deletion metadata
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("parents.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    parents: Mapped[List[Parent]] = relationship(
        secondary=parent_child_links, back_populates="children"
    )
    observations: Mapped[List["Observation"]] = relationship(back_populates="child", cascade="all, delete-orphan")
    milestone_statuses: Mapped[List["MilestoneStatus"]] = relationship(back_populates="child", cascade="all, delete-orphan")
    visits: Mapped[List["ClinicalVisit"]] = relationship(back_populates="child", cascade="all, delete-orphan")
    reports: Mapped[List["Report"]] = relationship(back_populates="child", cascade="all, delete-orphan")
    ai_suggestion_events: Mapped[List["AISuggestionEvent"]] = relationship(back_populates="child", cascade="all, delete-orphan")
    firsts: Mapped[List["First"]] = relationship(back_populates="child", cascade="all, delete-orphan")

    @property
    def display_first_name(self) -> str:
        if self.first_name == "Demo Child":
            if self.last_name == "A":
                return "Rohan"
            elif self.last_name == "B":
                return "Emma"
            elif self.last_name == "C":
                return "Liam"
        return self.first_name

    @property
    def display_last_name(self) -> str:
        if self.first_name == "Demo Child":
            if self.last_name == "A":
                return "Verma"
            elif self.last_name == "B":
                return "Smith"
            elif self.last_name == "C":
                return "Carter"
        return self.last_name


class DevelopmentalDomain(Base):
    __tablename__ = "developmental_domains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    milestones: Mapped[List["Milestone"]] = relationship(back_populates="domain")
    observations: Mapped[List["Observation"]] = relationship(back_populates="domain")


class EvidenceSource(Base):
    __tablename__ = "evidence_sources"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    organization: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    # Relationships
    milestones: Mapped[List["Milestone"]] = relationship(
        secondary=milestone_sources, back_populates="sources"
    )


class Milestone(Base):
    __tablename__ = "milestones"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    domain_id: Mapped[int] = mapped_column(ForeignKey("developmental_domains.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    age_range_low: Mapped[int] = mapped_column(Integer, nullable=False)  # in months
    age_range_high: Mapped[int] = mapped_column(Integer, nullable=False) # in months

    # Relationships
    domain: Mapped[DevelopmentalDomain] = relationship(back_populates="milestones")
    sources: Mapped[List[EvidenceSource]] = relationship(
        secondary=milestone_sources, back_populates="milestones"
    )
    statuses: Mapped[List["MilestoneStatus"]] = relationship(back_populates="milestone", cascade="all, delete-orphan")
    evidences: Mapped[List["ObservationMilestoneEvidence"]] = relationship(back_populates="milestone", cascade="all, delete-orphan")
    ai_suggestion_events: Mapped[List["AISuggestionEvent"]] = relationship(back_populates="selected_milestone")


class MilestoneStatus(Base):
    __tablename__ = "milestone_statuses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), nullable=False)
    milestone_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("milestones.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # not_started, in_progress, achieved
    observed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    child: Mapped[Child] = relationship(back_populates="milestone_statuses")
    milestone: Mapped[Milestone] = relationship(back_populates="statuses")


class Observation(Base):
    __tablename__ = "observations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), nullable=False)
    parent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    entry_type: Mapped[ObservationType] = mapped_column(String(50), nullable=False)
    domain_id: Mapped[Optional[int]] = mapped_column(ForeignKey("developmental_domains.id", ondelete="SET NULL"), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    context_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    observer_relation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_regression: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    structured_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    structuring_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    embedding_vector: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    recurrence_group_id: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True, index=True)
    quality_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Soft deletion metadata
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("parents.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    child: Mapped[Child] = relationship(back_populates="observations")
    parent: Mapped[Parent] = relationship(foreign_keys=[parent_id], back_populates="observations")
    domain: Mapped[Optional[DevelopmentalDomain]] = relationship(back_populates="observations")
    milestone_evidences: Mapped[List["ObservationMilestoneEvidence"]] = relationship(back_populates="observation", cascade="all, delete-orphan")
    ai_suggestion_events: Mapped[List["AISuggestionEvent"]] = relationship(back_populates="observation")


class ObservationMilestoneEvidence(Base):
    __tablename__ = "observation_milestone_evidence"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    observation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("observations.id", ondelete="CASCADE"), nullable=False)
    milestone_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("milestones.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    observation: Mapped["Observation"] = relationship(back_populates="milestone_evidences")
    milestone: Mapped["Milestone"] = relationship(back_populates="evidences")


# TODO: Future Architecture Pivot for DoctorPatientRelationship
# class DoctorPatientRelationship(Base):
#     __tablename__ = "doctor_patient_relationships"
#     id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
#     doctor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
#     child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), nullable=False)
#     relationship_status: Mapped[str] = mapped_column(String(50), default="active")  # active, inactive
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    specialization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    clinic_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    visits: Mapped[List["ClinicalVisit"]] = relationship(back_populates="doctor")


class ClinicalVisit(Base):
    __tablename__ = "clinical_visits"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), nullable=False)
    visit_date: Mapped[date] = mapped_column(Date, nullable=False)
    clinician_name: Mapped[str] = mapped_column(String(100), nullable=False)
    visit_priority: Mapped[str] = mapped_column(String(50), nullable=False)  # routine, urgent, consultation
    concern_level: Mapped[str] = mapped_column(String(50), nullable=False)   # low, medium, high
    concern_note: Mapped[str] = mapped_column(Text, nullable=False)
    doctor_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    child: Mapped[Child] = relationship(back_populates="visits")
    reports: Mapped[List["Report"]] = relationship(back_populates="visit")
    doctor: Mapped[Optional[Doctor]] = relationship(back_populates="visits")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), nullable=False)
    visit_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("clinical_visits.id", ondelete="SET NULL"), nullable=True)
    report_json: Mapped[dict] = mapped_column(JSON, nullable=False) # Stores the complete compiled JSON snapshot
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    period_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    period_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # draft, final

    # Relationships
    child: Mapped[Child] = relationship(back_populates="reports")
    visit: Mapped[Optional[ClinicalVisit]] = relationship(back_populates="reports")


class AISuggestionEvent(Base):
    __tablename__ = "ai_suggestion_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    observation_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("observations.id", ondelete="SET NULL"), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)

    suggested_domains: Mapped[dict] = mapped_column(JSON, nullable=False)
    suggested_milestones: Mapped[dict] = mapped_column(JSON, nullable=False)

    selected_domain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    selected_milestone_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("milestones.id", ondelete="SET NULL"), nullable=True)

    max_similarity: Mapped[float] = mapped_column(Float, nullable=False)
    relevance_rank: Mapped[str] = mapped_column(String(50), nullable=False)
    interaction_type: Mapped[InteractionType] = mapped_column(String(50), nullable=False, index=True)

    model_version: Mapped[str] = mapped_column(String(50), nullable=False, default="oie_v1_multilingual")
    processing_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    error_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    child: Mapped["Child"] = relationship(back_populates="ai_suggestion_events")
    observation: Mapped[Optional["Observation"]] = relationship(back_populates="ai_suggestion_events")
    selected_milestone: Mapped[Optional["Milestone"]] = relationship(back_populates="ai_suggestion_events")


class SuggestionFeedback(Base):
    __tablename__ = "suggestion_feedback"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    parent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("parents.id", ondelete="CASCADE"), nullable=False, index=True)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    ai_suggestion_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ai_suggestion_events.id", ondelete="SET NULL"), nullable=True)
    milestone_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("milestones.id", ondelete="CASCADE"), nullable=False)
    feedback_type: Mapped[str] = mapped_column(String(50), nullable=False)  # helpful, not_helpful
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    parent: Mapped["Parent"] = relationship()
    child: Mapped["Child"] = relationship()
    ai_suggestion_event: Mapped[Optional["AISuggestionEvent"]] = relationship()
    milestone: Mapped["Milestone"] = relationship()


class HumanValidationSession(Base):
    __tablename__ = "human_validation_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    participant_id: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)  # Caregiver, Clinician, Judge, Researcher
    usability_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5 scale
    trust_score: Mapped[int] = mapped_column(Integer, nullable=False)      # 1-5 scale
    report_usefulness_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5 scale
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class DomainTrendSnapshot(Base):
    __tablename__ = "domain_trend_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("developmental_domains.id", ondelete="CASCADE"), nullable=False)
    activity_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    variety_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    recommendation_text: Mapped[str] = mapped_column(Text, nullable=False)
    domain_id: Mapped[int] = mapped_column(ForeignKey("developmental_domains.id", ondelete="CASCADE"), nullable=False)
    served_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    interacted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class LongitudinalChangeSummary(Base):
    __tablename__ = "longitudinal_change_summaries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("developmental_domains.id", ondelete="CASCADE"), nullable=False)
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class First(Base):
    __tablename__ = "firsts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    is_first: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    first_title: Mapped[str] = mapped_column(String(255), nullable=False)
    first_date: Mapped[date] = mapped_column(Date, nullable=False)
    linked_observation_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("observations.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    child: Mapped[Child] = relationship(back_populates="firsts")
    observation: Mapped[Optional[Observation]] = relationship()


class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    recommendation_id: Mapped[str] = mapped_column(String(100), nullable=False)
    recommendation_type: Mapped[str] = mapped_column(String(50), nullable=False)  # activity, guide, question
    shown_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    helpful: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dismissed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    feedback_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class ActivityOutcome(Base):
    __tablename__ = "activity_outcomes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    attempted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    parent_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    observed_change: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


