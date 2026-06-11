import uuid
from datetime import datetime, date
from typing import Optional, List
from enum import Enum
from sqlalchemy import String, Text, Integer, Boolean, Date, DateTime, ForeignKey, Table, Column, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base

# ==========================================
# Enums
# ==========================================

class ObservationType(str, Enum):
    GENERAL = "general"
    CONCERN = "concern"
    MILESTONE = "milestone"

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
    observations: Mapped[List["Observation"]] = relationship(back_populates="milestone")


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
    milestone_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("milestones.id", ondelete="SET NULL"), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    context_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    observer_relation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_regression: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Soft deletion metadata
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("parents.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    child: Mapped[Child] = relationship(back_populates="observations")
    parent: Mapped[Parent] = relationship(foreign_keys=[parent_id], back_populates="observations")
    domain: Mapped[Optional[DevelopmentalDomain]] = relationship(back_populates="observations")
    milestone: Mapped[Optional[Milestone]] = relationship(back_populates="observations")


class ClinicalVisit(Base):
    __tablename__ = "clinical_visits"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), nullable=False)
    visit_date: Mapped[date] = mapped_column(Date, nullable=False)
    clinician_name: Mapped[str] = mapped_column(String(100), nullable=False)
    visit_priority: Mapped[str] = mapped_column(String(50), nullable=False)  # routine, urgent, consultation
    concern_level: Mapped[str] = mapped_column(String(50), nullable=False)   # low, medium, high
    concern_note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    child: Mapped[Child] = relationship(back_populates="visits")
    reports: Mapped[List["Report"]] = relationship(back_populates="visit")


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
