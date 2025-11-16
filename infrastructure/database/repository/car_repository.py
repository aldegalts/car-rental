from decimal import Decimal
from typing import Optional, List

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from infrastructure.database.models import CarEntity


class CarRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, car_id: int) -> Optional[CarEntity]:
        return self.session.get(CarEntity, car_id)

    def get_all(self) -> List[CarEntity]:
        return list(
            self.session.scalars(
                select(CarEntity)
            )
            .all()
        )

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

    def delete(self, car_id: int):
        car = self.session.query(CarEntity).filter(CarEntity.id == car_id).first()
        if car:
            self.session.delete(car)
            self.session.commit()

    def update(
            self, car_id: int, brand: str, model: str,
            year: int, category_id: int, license_plate: str,
            color_id: int, daily_cost: Decimal, car_status_id: int
    ) -> CarEntity:
        car_obj = self.session.get(CarEntity, car_id)
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

    def filter(
            self,
            brand: Optional[str] = None,
            model: Optional[str] = None,
            category_id: Optional[int] = None,
            color_id: Optional[int] = None,
            min_year: Optional[int] = None,
            max_year: Optional[int] = None,
            min_cost: Optional[Decimal] = None,
            max_cost: Optional[Decimal] = None
    ) -> List[CarEntity]:
        query = select(CarEntity)

        filters = []
        if brand:
            filters.append(CarEntity.brand.ilike(f"%{brand}%"))
        if model:
            filters.append(CarEntity.model.ilike(f"%{model}%"))
        if category_id:
            filters.append(CarEntity.category_id == category_id)
        if color_id:
            filters.append(CarEntity.color_id == color_id)
        if min_year:
            filters.append(CarEntity.year >= min_year)
        if max_year:
            filters.append(CarEntity.year <= max_year)
        if min_cost:
            filters.append(CarEntity.daily_cost >= min_cost)
        if max_cost:
            filters.append(CarEntity.daily_cost <= max_cost)

        if filters:
            query = query.where(and_(*filters))

        return list(self.session.scalars(query).all())