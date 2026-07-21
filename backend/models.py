from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from database import Base


subscriber_industries = Table(
    "subscriber_industries",
    Base.metadata,
    Column("subscriber_id", Integer, ForeignKey("subscribers.id")),
    Column("industry_id", Integer, ForeignKey("industries.id")),
)


class Industry(Base):
    __tablename__ = "industries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    subscribers = relationship("Subscriber", secondary=subscriber_industries, back_populates="industries")
    regulations = relationship("Regulation", back_populates="industry")


class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    industries = relationship("Industry", secondary=subscriber_industries, back_populates="subscribers")
    alerts = relationship("Alert", back_populates="subscriber")


class RegulatorySource(Base):
    __tablename__ = "regulatory_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)  # "federal_register", "rss", "state_site"
    url = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    last_checked = Column(DateTime, nullable=True)
    check_interval_minutes = Column(Integer, default=60)

    regulations = relationship("Regulation", back_populates="source")


class Regulation(Base):
    __tablename__ = "regulations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    document_number = Column(String(100), nullable=True, unique=True)
    abstract = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)  # GPT-4 generated plain-English summary
    impact_level = Column(String(20), nullable=True)  # "high", "medium", "low"
    publication_date = Column(DateTime, nullable=True)
    effective_date = Column(DateTime, nullable=True)
    source_url = Column(Text, nullable=True)
    raw_content = Column(Text, nullable=True)
    status = Column(String(30), default="draft", nullable=False)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    source_id = Column(Integer, ForeignKey("regulatory_sources.id"), nullable=True)
    industry_id = Column(Integer, ForeignKey("industries.id"), nullable=True)

    source = relationship("RegulatorySource", back_populates="regulations")
    industry = relationship("Industry", back_populates="regulations")
    alerts = relationship("Alert", back_populates="regulation")
    versions = relationship("RegulationVersion", back_populates="regulation")
    citations = relationship("Citation", back_populates="regulation")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"), nullable=False)
    regulation_id = Column(Integer, ForeignKey("regulations.id"), nullable=False)
    sent_at = Column(DateTime, nullable=True)
    is_read = Column(Boolean, default=False)
    delivery_status = Column(String(50), default="pending")  # "pending", "sent", "failed"
    delivery_key = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    subscriber = relationship("Subscriber", back_populates="alerts")
    regulation = relationship("Regulation", back_populates="alerts")


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), default="analyst", nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    tenant = relationship("Tenant")


class SourceSnapshot(Base):
    __tablename__ = "source_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("regulatory_sources.id"), nullable=False)
    fetched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(100), nullable=False)
    sha256 = Column(String(64), nullable=False, index=True)
    etag = Column(String(255), nullable=True)
    last_modified = Column(String(255), nullable=True)
    status = Column(String(30), default="complete", nullable=False)


class RegulationVersion(Base):
    __tablename__ = "regulation_versions"

    id = Column(Integer, primary_key=True, index=True)
    regulation_id = Column(Integer, ForeignKey("regulations.id"), nullable=False)
    snapshot_id = Column(Integer, ForeignKey("source_snapshots.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    normalized_content = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False)
    diff_from_previous = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    regulation = relationship("Regulation", back_populates="versions")


class Citation(Base):
    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)
    regulation_id = Column(Integer, ForeignKey("regulations.id"), nullable=False)
    snapshot_id = Column(Integer, ForeignKey("source_snapshots.id"), nullable=False)
    location = Column(String(255), nullable=False)
    quote = Column(Text, nullable=True)

    regulation = relationship("Regulation", back_populates="citations")


class ReviewDecision(Base):
    __tablename__ = "review_decisions"

    id = Column(Integer, primary_key=True, index=True)
    regulation_id = Column(Integer, ForeignKey("regulations.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    decision = Column(String(30), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class RetentionPolicy(Base):
    __tablename__ = "retention_policies"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), unique=True, nullable=False)
    customer_data_days = Column(Integer, default=365, nullable=False)
    audit_data_days = Column(Integer, default=730, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class DeletionJob(Base):
    __tablename__ = "deletion_jobs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(30), default="requested", nullable=False)
    deleted_records = Column(Integer, default=0, nullable=False)
    retained_public_provenance = Column(Integer, default=0, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PilotRun(Base):
    __tablename__ = "pilot_runs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    source_register = Column(String(255), nullable=False)
    status = Column(String(30), default="active", nullable=False)
    manual_items = Column(Integer, default=0, nullable=False)
    product_items = Column(Integer, default=0, nullable=False)
    missed_items = Column(Integer, default=0, nullable=False)
    correction_count = Column(Integer, default=0, nullable=False)
    time_saved_minutes = Column(Float, default=0, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PilotObservation(Base):
    __tablename__ = "pilot_observations"

    id = Column(Integer, primary_key=True, index=True)
    pilot_run_id = Column(Integer, ForeignKey("pilot_runs.id"), nullable=False)
    source_url = Column(Text, nullable=False)
    manual_found = Column(Boolean, default=False, nullable=False)
    product_found = Column(Boolean, default=False, nullable=False)
    correction_count = Column(Integer, default=0, nullable=False)
    manual_latency_seconds = Column(Float, nullable=True)
    product_latency_seconds = Column(Float, nullable=True)
    time_saved_minutes = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SourceHealth(Base):
    __tablename__ = "source_health"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("regulatory_sources.id"), unique=True, nullable=False)
    status = Column(String(30), default="unknown", nullable=False)
    last_success_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    consecutive_failures = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
