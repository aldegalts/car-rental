from typing import List

from sqlalchemy.orm import Session

from application.car.schemas import CarRead
from infrastructure.database.repository import CarRepository


class GetAllCarUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_repo = CarRepository(db)

    def execute(self) -> List[CarRead]:
        cars = self.car_repo.get_all()
        return [CarRead.model_validate(c) for c in cars]