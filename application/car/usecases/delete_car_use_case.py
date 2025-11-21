from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from infrastructure.database.repository import CarRepository


class DeleteCarUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_repo = CarRepository(db)

    def execute(self, car_id: int):
        car = self.car_repo.get_by_id(car_id)
        if car is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Статус не найден")

        return self.car_repo.delete(car_id)