from typing import TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import DatabaseException

T = TypeVar("T")

class BaseRepository:
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def get_by_id(self, id: Any) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def list(self) -> List[T]:
        return self.db.query(self.model).all()

    def create(self, data: dict) -> T:
        try:
            obj = self.model(**data)
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseException(f"Failed to create {self.model.__name__}: {str(e)}")

    def update(self, id: Any, data: dict) -> Optional[T]:
        try:
            obj = self.get_by_id(id)
            if obj:
                for key, value in data.items():
                    setattr(obj, key, value)
                self.db.commit()
                self.db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseException(f"Failed to update {self.model.__name__}: {str(e)}")

    def delete(self, id: Any) -> bool:
        try:
            obj = self.get_by_id(id)
            if obj:
                self.db.delete(obj)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseException(f"Failed to delete {self.model.__name__}: {str(e)}")
