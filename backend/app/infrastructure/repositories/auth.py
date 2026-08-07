import hashlib
from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from app.domain.repositories.auth import RefreshTokenRepository
from app.infrastructure.models.auth import RefreshToken, EmailVerificationToken

class SQLAlchemyRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self, db: Session):
        self.db = db

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def get_by_hash(self, token: str) -> Optional[RefreshToken]:
        token_hash = self._hash_token(token)
        return self.db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash, RefreshToken.is_revoked == False).first()

    def create(self, token_data: dict) -> RefreshToken:
        token_data["token_hash"] = self._hash_token(token_data["token"])
        del token_data["token"]
        token = RefreshToken(**token_data)
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def revoke(self, token_id: UUID) -> None:
        token = self.db.query(RefreshToken).filter(RefreshToken.id == token_id).first()
        if token:
            token.is_revoked = True
            self.db.commit()

class SQLAlchemyEmailVerificationTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def create(self, user_id: UUID, token: str, expires_at: datetime) -> EmailVerificationToken:
        token_hash = self._hash_token(token)
        verification_token = EmailVerificationToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.db.add(verification_token)
        self.db.commit()
        self.db.refresh(verification_token)
        return verification_token

    def get_by_hash(self, token: str) -> Optional[EmailVerificationToken]:
        token_hash = self._hash_token(token)
        return self.db.query(EmailVerificationToken).filter(EmailVerificationToken.token_hash == token_hash, EmailVerificationToken.is_used == False).first()

    def mark_as_used(self, token_id: UUID) -> None:
        token = self.db.query(EmailVerificationToken).filter(EmailVerificationToken.id == token_id).first()
        if token:
            token.is_used = True
            self.db.commit()


