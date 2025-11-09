from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.database.models import RentalStatusEntity


class RentalStatusRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, status: str) -> RentalStatusEntity:
        status_obj = RentalStatusEntity(status=status)
        self.session.add(status_obj)
        self.session.commit()
        self.session.refresh(status_obj)
        return status_obj

    def delete(self, status_id: int):
        status = self.session.query(RentalStatusEntity).filter(RentalStatusEntity.id == status_id).first()
        if status:
            self.session.delete(status)
            self.session.commit()

    def get_by_id(self, status_id: int) -> Optional[RentalStatusEntity]:
        return self.session.get(RentalStatusEntity, status_id)

    def get_all(self) -> List[RentalStatusEntity]:
        return list(
            self.session.scalars(
                select(RentalStatusEntity)
            )
            .all()
        )

    def update(self, status_id: int, status: str) -> RentalStatusEntity:
        status_obj = self.session.get(RentalStatusEntity, status_id)
        status_obj.status = status
        self.session.commit()
        self.session.refresh(status_obj)
        return status_obj