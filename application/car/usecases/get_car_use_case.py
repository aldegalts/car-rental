from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from application.car.schemas import CarRead
from infrastructure.database.repository import CarRepository


class GetCarUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_repo = CarRepository(db)

    def execute(self, car_id) -> CarRead:
        car = self.car_repo.get_by_id(car_id)
        if car is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")

        return CarRead.model_validate(car)