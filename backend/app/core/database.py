from sqlalchemy import create_engine
from sqlalchemy.orm import registry, sessionmaker, declarative_base
from app.core.config import settings

# Create engine for synchronous / standard SQLAlchemy connection
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Standard Session Local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base for models
Base = declarative_base()

def get_db():
    """
    FastAPI Dependency to yield a database session.
    Ensures safe automatic closing of sessions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
