import pytest
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.infrastructure.models.alerts import DetectionRule, Alert
from app.infrastructure.repositories.rules import SQLAlchemyDetectionRuleRepository
from app.infrastructure.schemas.rules import DetectionRuleCreate

# Use SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

def test_rule_repository_create_and_get(db_session):
    repo = SQLAlchemyDetectionRuleRepository(db_session)
    rule_data = {
        "name": "SQL Injection Detection",
        "severity": "CRITICAL",
        "confidence_score": 90,
        "query_logic": "SELECT * FROM logs WHERE query LIKE '%UNION%'"
    }
    
    rule = repo.create(rule_data)
    assert rule.id is not None
    assert rule.name == "SQL Injection Detection"
    
    retrieved = repo.get_by_id(rule.id)
    assert retrieved is not None
    assert retrieved.name == rule.name
