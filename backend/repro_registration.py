import sys
import os
from uuid import UUID, uuid4
import asyncio

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Force environment variables before importing settings
os.environ["SECRET_KEY"] = "debug_secret_key_for_reproduction_1234567890"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=engine)

from app.core.database import Base
from app.infrastructure.models.iam import User, Role
from app.infrastructure.repositories.iam import SQLAlchemyUserRepository, SQLAlchemyRoleRepository
from app.infrastructure.repositories.auth import SQLAlchemyRefreshTokenRepository
from app.infrastructure.repositories.audit import SQLAlchemyAuditRepository
from app.application.services.auth import AuthService
from app.application.services.audit import AuditService
from app.infrastructure.schemas.iam import UserCreate

async def repro():
    print("Starting Registration Reproduction (SQLite In-Memory)...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Seed the specific role with the known UUID
        soc_analyst_id = UUID("202eac2d-2ffe-4e23-9520-ce7ebfb71ed9")
        role = Role(id=soc_analyst_id, name="SOC Analyst")
        db.add(role)
        db.commit()
        print(f"Seeded Role: {role.name} with ID: {role.id}")

        user_repo = SQLAlchemyUserRepository(db)
        role_repo = SQLAlchemyRoleRepository(db)
        
        # Mock dependencies that aren't critical for role_id tracing
        class MockRefreshTokenRepo:
            def create(self, data): pass
        class MockAuditRepo:
            def log_action(self, *args, **kwargs): pass
        
        refresh_token_repo = MockRefreshTokenRepo()
        audit_repo = MockAuditRepo()
        
        # We need a real AuditService because AuthService depends on it, 
        # but we can mock its internal log_action.
        audit_service = AuditService(audit_repo)
        audit_service.log_action = lambda *args, **kwargs: None

        auth_service = AuthService(user_repo, role_repo, refresh_token_repo, audit_service)
        
        user_in = UserCreate(
            email="test_repro@example.com",
            full_name="Test User",
            password="ComplexPassword123!"
        )
        
        print("\n--- Calling register_user ---")
        # We use a dummy IP address
        await auth_service.register_user(user_in, "127.0.0.1")
        print("--- register_user completed ---\n")
        
    except Exception as e:
        print(f"\nCAUGHT EXCEPTION: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(repro())
