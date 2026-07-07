from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.application.services.ingestion import IngestionService
from app.application.services.parser import DefaultLogParser
from app.infrastructure.repositories.logs import SQLAlchemyLogRepository
from app.infrastructure.schemas.logs import LogCreate, LogResponse

router = APIRouter(prefix="/ingest", tags=["Log Ingestion"])

def get_ingestion_service(db: Session = Depends(get_db)) -> IngestionService:
    log_repo = SQLAlchemyLogRepository(db)
    parser = DefaultLogParser()
    return IngestionService(log_repo, parser)

@router.post("/", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
def ingest_log(
    log_in: LogCreate,
    ingestion_service: IngestionService = Depends(get_ingestion_service)
):
    return ingestion_service.ingest_log(log_in)
