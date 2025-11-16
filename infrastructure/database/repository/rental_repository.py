from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session

from infrastructure.database.models import RentalEntity, ViolationEntity


class RentalRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, rental_id: int) -> Optional[RentalEntity]:
        return self.session.get(RentalEntity, rental_id)

    def get_by_user_id(self, user_id: int) -> List[RentalEntity]:
        return (
            self.session.query(RentalEntity)
            .filter(RentalEntity.client.user_id == user_id)
            .all()
        )

    def get_by_user_and_id(self, user_id: int, rental_id: int):
        return (
            self.session.query(RentalEntity)
            .filter(
                RentalEntity.id == rental_id,
                RentalEntity.user_id == user_id
            )
            .first()
        )

    def get_all(self) -> List[RentalEntity]:
        return list(
            self.session.scalars(
                select(RentalEntity)
            )
            .all()
        )

    def create(
            self, client_id: int, car_id: int,
            start_date: datetime, end_date: datetime,
            total_amount: Decimal, rental_status_id: int
    ) -> RentalEntity:
        rental_obj = RentalEntity(
            client_id=client_id,
            car_id=car_id,
            start_date=start_date,
            end_date=end_date,
            total_amount=total_amount,
            rental_status_id=rental_status_id
        )
        self.session.add(rental_obj)
        self.session.commit()
        self.session.refresh(rental_obj)
        return rental_obj

    def delete(self, rental_id: int):
        rental = self.session.query(RentalEntity).filter(RentalEntity.id == rental_id).first()
        if rental:
            self.session.delete(rental)
            self.session.commit()

    def update(
            self, rental_id: int, car_id: int,
            start_date: datetime, end_date: datetime,
            total_amount: Decimal, rental_status_id: int
    ) -> RentalEntity:
        rental_obj = self.session.get(RentalEntity, rental_id)
        rental_obj.car_id = car_id
        rental_obj.start_date = start_date
        rental_obj.end_date = end_date
        rental_obj.total_amount = total_amount
        rental_obj.rental_status_id = rental_status_id
        self.session.commit()
        self.session.refresh(rental_obj)
        return rental_obj

    def filter(
            self,
            car_id: Optional[int] = None,
            client_id: Optional[int] = None
    ) -> List[RentalEntity]:
        query = select(RentalEntity)

        filters = []
        if car_id:
            filters.append(RentalEntity.car_id == car_id)
        if client_id:
            filters.append(RentalEntity.client_id == client_id)

        if filters:
            query = query.where(and_(*filters))

        return list(self.session.scalars(query).all())

    def statistic_get_rentals(self, start_date: datetime, end_date: datetime):
        base_query = (
            select(RentalEntity)
            .where(RentalEntity.start_date >= start_date)
            .where(RentalEntity.end_date <= end_date)
        )
        rentals = list(self.session.scalars(base_query).all())

        total_count = len(rentals)

        if total_count == 0:
            return rentals, 0, 0

        violation_count_query = (
            select(func.count(func.distinct(ViolationEntity.rental_id)))
            .join(RentalEntity, RentalEntity.id == ViolationEntity.rental_id)
            .where(RentalEntity.start_date >= start_date)
            .where(RentalEntity.end_date <= end_date)
        )

        violation_count = self.session.scalar(violation_count_query) or 0

        percent_with_violations = (violation_count / total_count) * 100
        percent_without_violations = 100 - percent_with_violations

        return rentals, percent_with_violations, percent_without_violations