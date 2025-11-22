from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy.orm import Session

from infrastructure.database.models import ViolationEntity, RentalEntity, ClientEntity


class ViolationRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, violation_id: int) -> Optional[ViolationEntity]:
        return self.session.get(ViolationEntity, violation_id)

    def get_by_user_id(self, user_id: int) -> List[ViolationEntity]:
        return (
            self.session.query(ViolationEntity)
            .join(ViolationEntity.rental)
            .join(RentalEntity.client)
            .filter(ClientEntity.user_id == user_id)
            .order_by(ViolationEntity.violation_date.desc())
            .all()
        )

    def get_by_rental_id(self, rental_id: int) -> List[ViolationEntity]:
        return (
            self.session.query(ViolationEntity)
            .filter(ViolationEntity.rental_id == rental_id)
            .order_by(ViolationEntity.violation_date.desc())
            .all()
        )

    def get_by_user_and_id(self, user_id: int, violation_id: int):
        return (
            self.session.query(ViolationEntity)
            .join(ViolationEntity.rental)
            .join(RentalEntity.client)
            .filter(
                ViolationEntity.id == violation_id,
                ClientEntity.user_id == user_id
            )
            .first()
        )

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

    def delete(self, violation_id: int):
        violation = self.session.query(ViolationEntity).filter(ViolationEntity.id == violation_id).first()
        if violation:
            self.session.delete(violation)
            self.session.commit()

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