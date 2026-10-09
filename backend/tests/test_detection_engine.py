import pytest
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.infrastructure.models.alerts import DetectionRule, Alert
from app.infrastructure.repositories.rules import SQLAlchemyDetectionRuleRepository
from app.infrastructure.schemas.rules import DetectionRuleCreate
from app.application.services.detection import DetectionService

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


def test_detection_service_matches_only_supported_rule_logic(db_session):
    repo = SQLAlchemyDetectionRuleRepository(db_session)
    rule = repo.create({
        "name": "Critical login failure",
        "severity": "HIGH",
        "confidence_score": 80,
        "query_logic": '{"event_type": "login_failure", "severity": "CRITICAL"}',
    })
    service = DetectionService(db_session, repo)
    created = service.run_detection({"event_type": "login_failure", "severity": "CRITICAL", "event_id": "evt-1"})
    assert len(created) == 1
    assert created[0].detection_rule_id == rule.id
    assert service.run_detection({"event_type": "login_failure", "severity": "CRITICAL", "event_id": "evt-1"}) == []
    assert service.run_detection({"event_type": "process_creation", "severity": "CRITICAL", "event_id": "evt-2"}) == []
