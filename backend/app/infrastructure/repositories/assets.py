from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.domain.repositories.assets import AssetRepository
from app.infrastructure.models import Asset

class SQLAlchemyAssetRepository(AssetRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: UUID) -> Optional[Asset]:
        return self.db.query(Asset).filter(Asset.id == id).first()

    def create(self, asset_in: dict) -> Asset:
        asset = Asset(**asset_in)
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def list(self) -> List[Asset]:
        return self.db.query(Asset).all()
