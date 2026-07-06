from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class ThreatFeed(Base):
    __tablename__ = "threat_feeds"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    url: Mapped[Optional[str]] = mapped_column(String(512))  # Sync URL
    feed_type: Mapped[str] = mapped_column(String(100))  # e.g., ABUSEIPDB, VIRUSTOTAL, ALIENVAULT, GREYNOISE, URLHAUS, CIRCL, CUSTOM
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    iocs: Mapped[List["IOCRecord"]] = relationship("IOCRecord", back_populates="feed", cascade="all, delete-orphan")

class IOCRecord(Base):
    __tablename__ = "ioc_records"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    value: Mapped[str] = mapped_column(String(512), unique=True, index=True)  # IP, Domain, Hash
    type: Mapped[str] = mapped_column(String(50), index=True)  # IPV4, IPV6, DOMAIN, URL, SHA256, SHA1, MD5, REGISTRY_KEY, PROCESS, EMAIL
    risk_score: Mapped[int] = mapped_column(Integer, default=0, index=True)  # 0-100
    tags: Mapped[Optional[dict]] = mapped_column(JSON)  # list of tags (e.g., ["malware", "botnet"])
    mitre_attack_mapping: Mapped[Optional[dict]] = mapped_column(JSON)  # associated MITRE techniques
    description: Mapped[Optional[str]] = mapped_column(Text)
    references: Mapped[Optional[dict]] = mapped_column(JSON)  # list of source urls or identifiers
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    threat_feed_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("threat_feeds.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    feed: Mapped[Optional[ThreatFeed]] = relationship("ThreatFeed", back_populates="iocs")

class ThreatIntelligence(Base):
    __tablename__ = "threat_intelligence"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255), index=True)
    source: Mapped[str] = mapped_column(String(100))  # CISA, MITRE, internal
    external_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)  # CVE-2023-XXXX, etc.
    content: Mapped[Optional[dict]] = mapped_column(JSON)  # rich intel report data
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
