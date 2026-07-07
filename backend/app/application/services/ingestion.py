from app.domain.repositories.logs import LogRepository
from app.domain.interfaces.parser import LogParser
from app.infrastructure.schemas.logs import LogCreate, LogResponse

class IngestionService:
    def __init__(self, log_repo: LogRepository, parser: LogParser):
        self.log_repo = log_repo
        self.parser = parser

    def ingest_log(self, log_in: LogCreate) -> LogResponse:
        parsed_data = self.parser.parse(log_in.raw_content)
        log_data = log_in.model_dump()
        log_data["parsed_content"] = parsed_data
        
        log = self.log_repo.create(log_data)
        return LogResponse.model_validate(log)
