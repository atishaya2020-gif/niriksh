from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.postgres import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="investigator")
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Case(Base):
    __tablename__ = "cases"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_number: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    records: Mapped[list["RawRecord"]] = relationship(back_populates="case", cascade="all, delete-orphan")


PROCESSING_STATUSES = [
    "RECEIVED",
    "VALIDATING",
    "PERSISTING_RECORDS",
    "GRAPH_PENDING",
    "GRAPH_SYNCING",
    "MATCHING_PENDING",
    "MATCHING",
    "ALERTING_PENDING",
    "ALERTING",
    "COMPLETED",
    "COMPLETED_WITH_WARNINGS",
    "FAILED",
    "CANCELLED",
]


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    uploader_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(40), default="RECEIVED", index=True)
    stage: Mapped[str] = mapped_column(String(40), default="RECEIVED", index=True)
    source_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    source_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    record_ids: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    records_received: Mapped[int] = mapped_column(Integer, default=0)
    records_processed: Mapped[int] = mapped_column(Integer, default=0)
    entities_extracted: Mapped[int] = mapped_column(Integer, default=0)
    relationships_detected: Mapped[int] = mapped_column(Integer, default=0)
    matches_found: Mapped[int] = mapped_column(Integer, default=0)
    alerts_generated: Mapped[int] = mapped_column(Integer, default=0)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RawRecord(Base):
    __tablename__ = "raw_records"
    __table_args__ = (UniqueConstraint("case_id", "record_id", name="uq_raw_records_case_id_record_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    record_id: Mapped[str] = mapped_column(String(100), index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    category: Mapped[str] = mapped_column(String(100), index=True)
    incident_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    case: Mapped[Case] = relationship(back_populates="records")

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    alert_type: Mapped[str] = mapped_column(String(100), index=True)
    entity_id: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    case_id: Mapped[int | None] = mapped_column(
        ForeignKey("cases.id"),
        index=True,
        nullable=True,
    )

    risk_level: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    risk_score: Mapped[int] = mapped_column(Integer, default=0)

    reason: Mapped[str] = mapped_column(Text())
    confidence: Mapped[float] = mapped_column(default=0.0)

    status: Mapped[str] = mapped_column(
        String(30),
        default="NEW",
        index=True,
    )

    assigned_to: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


EVIDENCE_TYPES = [
    "CALL_RECORD",
    "FINANCIAL_TRANSACTION",
    "FIR_DOCUMENT",
    "DIGITAL_FORENSIC",
    "SURVEILLANCE",
    "WITNESS_STATEMENT",
    "DOCUMENT",
    "OTHER",
]

VERIFICATION_STATUSES = [
    "PENDING",
    "VERIFIED",
    "REJECTED",
    "REQUIRES_REVIEW",
]


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    record_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    evidence_type: Mapped[str] = mapped_column(String(50))
    source: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text())
    collection_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True)
    confidence: Mapped[float] = mapped_column(default=0.0)
    evidence_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    verified_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


MATCH_STATUSES = [
    "PENDING_REVIEW",
    "CONFIRMED",
    "REJECTED",
]


class EntityMatch(Base):
    __tablename__ = "entity_matches"
    __table_args__ = (UniqueConstraint("case_id", "source_entity_id", "candidate_entity_id", name="uq_entity_matches_case_source_candidate"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    source_entity_id: Mapped[str] = mapped_column(String(255), index=True)
    candidate_entity_id: Mapped[str] = mapped_column(String(255), index=True)
    source_entity_type: Mapped[str] = mapped_column(String(50))
    candidate_entity_type: Mapped[str] = mapped_column(String(50))
    match_score: Mapped[float] = mapped_column(default=0.0)
    confidence: Mapped[float] = mapped_column(default=0.0)
    matching_factors: Mapped[dict | None] = mapped_column("factors", JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="PENDING_REVIEW", index=True)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AccessRequest(Base):
    __tablename__ = "access_requests"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    username: Mapped[str] = mapped_column(
        String(100),
        index=True
    )

    requested_role: Mapped[str] = mapped_column(
        String(50),
        default="investigator"
    )

    department: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    reason: Mapped[str | None] = mapped_column(
        Text(),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING",
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
