from decimal import Decimal
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.database.models import CarEntity


class CarRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
            self, brand: str, model: str,
            year: int, category_id: int, license_plate: str,
            color_id: int, daily_cost: Decimal, car_status_id: int
    ) -> CarEntity:
        car_obj = CarEntity(
            brand=brand,
            model=model,
            year=year,
            category_id=category_id,
            license_plate=license_plate,
            color_id=color_id,
            daily_cost=daily_cost,
            car_status_id=car_status_id
        )
        self.session.add(car_obj)
        self.session.commit()
        self.session.refresh(car_obj)
        return car_obj

    def get_by_id(self, car_id: int) -> Optional[CarEntity]:
        return self.session.get(CarEntity, car_id)

    def update(
            self, brand: str, model: str,
            year: int, category_id: int, license_plate: str,
            color_id: int, daily_cost: Decimal, car_status_id: int
    ) -> CarEntity:
        car_obj = self.session.get(CarEntity, category_id)
        car_obj.brand = brand
        car_obj.model = model
        car_obj.year = year
        car_obj.category_id = category_id
        car_obj.license_plate = license_plate
        car_obj.color_id = color_id
        car_obj.daily_cost = daily_cost
        car_obj.car_status_id=car_status_id
        self.session.commit()
        self.session.refresh(car_obj)
        return car_obj

    def delete(self, car_id: int):
        car = self.session.query(CarEntity).filter(CarEntity.id == car_id).first()
        if car:
            self.session.delete(car)
            self.session.commit()

    def get_all(self) -> List[CarEntity]:
        return list(
            self.session.scalars(
                select(CarEntity)
            )
            .all()
        )