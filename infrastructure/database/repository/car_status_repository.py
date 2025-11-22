from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.database.models import CarStatusEntity


class CarStatusRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_status(self, status: str) -> Optional[CarStatusEntity]:
        return (
            self.session.query(CarStatusEntity)
            .filter(CarStatusEntity.status == status)
            .first()
        )

    def get_by_id(self, status_id: int) -> Optional[CarStatusEntity]:
        return self.session.get(CarStatusEntity, status_id)

    def get_all(self) -> List[CarStatusEntity]:
        return list(
            self.session.scalars(
                select(CarStatusEntity)
            )
            .all()
        )

    def create(self, status: str) -> CarStatusEntity:
        status_obj = CarStatusEntity(status=status)
        self.session.add(status_obj)
        self.session.commit()
        self.session.refresh(status_obj)
        return status_obj

    def delete(self, status_id: int):
        status = self.session.query(CarStatusEntity).filter(CarStatusEntity.id == status_id).first()
        if status:
            self.session.delete(status)
            self.session.commit()

    def update(self, status_id: int, status: str) -> CarStatusEntity:
        status_obj = self.session.get(CarStatusEntity, status_id)
        status_obj.status = status
        self.session.commit()
        self.session.refresh(status_obj)
        return status_obj