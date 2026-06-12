from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
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
    title = Column(String(500), nullable=False)
    document_number = Column(String(100), nullable=True, unique=True)
    abstract = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)  # GPT-4 generated plain-English summary
    impact_level = Column(String(20), nullable=True)  # "high", "medium", "low"
    publication_date = Column(DateTime, nullable=True)
    effective_date = Column(DateTime, nullable=True)
    source_url = Column(Text, nullable=True)
    raw_content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    source_id = Column(Integer, ForeignKey("regulatory_sources.id"), nullable=True)
    industry_id = Column(Integer, ForeignKey("industries.id"), nullable=True)

    source = relationship("RegulatorySource", back_populates="regulations")
    industry = relationship("Industry", back_populates="regulations")
    alerts = relationship("Alert", back_populates="regulation")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"), nullable=False)
    regulation_id = Column(Integer, ForeignKey("regulations.id"), nullable=False)
    sent_at = Column(DateTime, nullable=True)
    is_read = Column(Boolean, default=False)
    delivery_status = Column(String(50), default="pending")  # "pending", "sent", "failed"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    subscriber = relationship("Subscriber", back_populates="alerts")
    regulation = relationship("Regulation", back_populates="alerts")
