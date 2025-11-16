from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.database.models import ViolationEntity


class ViolationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
            self, rental_id: int, violation_type_id: int,
            description: str, fine_amount: Decimal,
            violation_date: datetime, is_paid: bool
    ) -> ViolationEntity:
        violation_obj = ViolationEntity(
            rental_id=rental_id,
            violation_type_id=violation_type_id,
            description=description,
            fine_amount=fine_amount,
            violation_date=violation_date,
            is_paid=is_paid
        )
        self.session.add(violation_obj)
        self.session.commit()
        self.session.refresh(violation_obj)
        return violation_obj

    def get_by_id(self, violation_id: int) -> Optional[ViolationEntity]:
        return self.session.get(ViolationEntity, violation_id)

    def update(
            self, violation_id: int, rental_id: int,
            violation_type_id: int, description: str,
            fine_amount: Decimal, violation_date: datetime,
            is_paid: bool
    ) -> ViolationEntity:
        violation_obj = self.session.get(ViolationEntity, violation_id)
        violation_obj.rental_id = rental_id
        violation_obj.violation_type_id = violation_type_id
        violation_obj.description = description
        violation_obj.fine_amount = fine_amount
        violation_obj.violation_date = violation_date
        violation_obj.is_paid = is_paid
        self.session.commit()
        self.session.refresh(violation_obj)
        return violation_obj

    def delete(self, violation_id: int):
        violation = self.session.query(ViolationEntity).filter(ViolationEntity.id == violation_id).first()
        if violation:
            self.session.delete(violation)
            self.session.commit()

    def get_by_user_id(self, user_id: int) -> List[ViolationEntity]:
        return (
            self.session.query(ViolationEntity)
            .filter(ViolationEntity.rental.client.user_id == user_id)
            .all()
        )