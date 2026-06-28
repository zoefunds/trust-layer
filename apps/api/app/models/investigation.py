import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Numeric, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base


class Investigation(Base):
    __tablename__ = "investigations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    protocol_name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending")
    contract_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tx_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    validators: Mapped[list["Validator"]] = relationship("Validator", back_populates="investigation", cascade="all, delete")
    report: Mapped[Optional["Report"]] = relationship("Report", back_populates="investigation", uselist=False, cascade="all, delete")


class Validator(Base):
    __tablename__ = "validators"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    investigation_id: Mapped[str] = mapped_column(String, ForeignKey("investigations.id"), nullable=False, index=True)
    validator_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending")
    findings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    sources: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="validators")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    investigation_id: Mapped[str] = mapped_column(String, ForeignKey("investigations.id"), nullable=False, unique=True)
    overall_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    team_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    funding_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    product_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    github_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    community_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    tokenomics_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    security_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    onchain_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    reputation_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    risk_level: Mapped[str] = mapped_column(String, default="unknown")
    consensus_result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    evidence: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    verified_claims: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    disputed_claims: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    unresolved_claims: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="report")
