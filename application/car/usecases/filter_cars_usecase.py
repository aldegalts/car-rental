from typing import List

from sqlalchemy.orm import Session

from application.car.schemas import CarFilter, CarRead
from infrastructure.database.repository import CarRepository


class FilterCarUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_repo = CarRepository(db)

    def execute(self, filters: CarFilter) -> List[CarRead]:
        cars = self.car_repo.filter(
            brand=filters.brand,
            model=filters.model,
            category_id=filters.category_id,
            color_id=filters.color_id,
            min_year=filters.min_year,
            max_year=filters.max_year,
            min_cost=filters.min_cost,
            max_cost=filters.max_cost,
        )
        return [CarRead.model_validate(car) for car in cars]
