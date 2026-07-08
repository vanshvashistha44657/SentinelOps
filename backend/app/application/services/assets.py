from typing import Optional, List
from uuid import UUID
from app.domain.repositories.assets import AssetRepository
from app.infrastructure.schemas.assets import AssetCreate, AssetResponse
from app.infrastructure.models.assets import Asset
from app.application.services.audit import AuditService

class AssetService:
    def __init__(self, asset_repo: AssetRepository, audit_service: AuditService):
        self.asset_repo = asset_repo
        self.audit_service = audit_service

    async def get_asset(self, asset_id: UUID) -> Optional[AssetResponse]:
        asset = self.asset_repo.get_by_id(asset_id)
        if not asset:
            return None
        return AssetResponse.model_validate(asset)

    async def create_asset(self, asset_in: AssetCreate, user_id: UUID, ip_address: str) -> AssetResponse:
        asset = self.asset_repo.create(asset_in.model_dump())
        self.audit_service.log_action(user_id, ip_address, "assets", "ASSET_CREATE", None, {"asset_id": str(asset.id)})
        return AssetResponse.model_validate(asset)

    async def list_assets(self) -> List[AssetResponse]:
        assets = self.asset_repo.list()
        return [AssetResponse.model_validate(a) for a in assets]
