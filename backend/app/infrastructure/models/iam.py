from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

# Association table for Many-to-Many relationship between Roles and Permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

class Permission(Base):
    __tablename__ = "permissions"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary=role_permissions, back_populates="permissions"
    )

class Role(Base):
    __tablename__ = "roles"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    permissions: Mapped[List[Permission]] = relationship(
        "Permission", secondary=role_permissions, back_populates="roles"
    )
    users: Mapped[List["User"]] = relationship("User", back_populates="role")

from app.infrastructure.models.mixins import SoftDeleteMixin

from app.domain.enums.user import ApprovalStatus

# ... (rest of imports)

# ... (Role, Permission, role_permissions)

class User(Base, SoftDeleteMixin):
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Onboarding Fields
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approval_status: Mapped[ApprovalStatus] = mapped_column(String(50), default=ApprovalStatus.PENDING)
    approved_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rejected_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    registration_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    registration_device: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_login_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    last_login_device: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id", ondelete="RESTRICT"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    role: Mapped[Role] = relationship("Role", back_populates="users")
    login_history: Mapped[List["LoginHistory"]] = relationship("LoginHistory", back_populates="user", cascade="all, delete-orphan")
    api_keys: Mapped[List["APIKey"]] = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    assigned_alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="assigned_user", foreign_keys="[Alert.assigned_user_id]")
    assigned_incidents: Mapped[List["Incident"]] = relationship("Incident", back_populates="assigned_user", foreign_keys="[Incident.assigned_user_id]")
    assigned_cases: Mapped[List["Case"]] = relationship("Case", back_populates="assigned_user", foreign_keys="[Case.assigned_user_id]")


class LoginHistory(Base):
    __tablename__ = "login_history"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    ip_address: Mapped[str] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(50))  # SUCCESS, FAILED
    failure_reason: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped[User] = relationship("User", back_populates="login_history")

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    key_prefix: Mapped[str] = mapped_column(String(8), unique=True)  # First 8 chars of API Key for quick lookup
    hashed_key: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    user: Mapped[User] = relationship("User", back_populates="api_keys")
