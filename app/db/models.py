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
