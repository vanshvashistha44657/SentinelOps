from typing import Optional, List
from uuid import UUID
from app.domain.repositories.iocs import IOCRepository
from app.infrastructure.schemas.iocs import IOCCreate, IOCUpdate, IOCResponse
from app.infrastructure.models.threat_intel import IOCRecord

class IOCService:
    def __init__(self, ioc_repo: IOCRepository):
        self.ioc_repo = ioc_repo

    async def get_ioc(self, ioc_id: UUID) -> Optional[IOCResponse]:
        ioc = self.ioc_repo.get_by_id(ioc_id)
        if not ioc:
            return None
        return IOCResponse.model_validate(ioc)

    async def create_ioc(self, ioc_in: IOCCreate) -> IOCResponse:
        ioc = self.ioc_repo.create(ioc_in.model_dump())
        return IOCResponse.model_validate(ioc)

    async def update_ioc(self, ioc_id: UUID, ioc_update: IOCUpdate) -> Optional[IOCResponse]:
        ioc = self.ioc_repo.update(ioc_id, ioc_update.model_dump(exclude_unset=True))
        if not ioc:
            return None
        return IOCResponse.model_validate(ioc)

    async def list_iocs(self) -> List[IOCResponse]:
        iocs = self.ioc_repo.list()
        return [IOCResponse.model_validate(ioc) for ioc in iocs]
