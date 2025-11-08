from sqlalchemy.orm import Session

from infrastructure.database.repository import CarRepository


class DeleteCarUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_repo = CarRepository(db)

    def execute(self, car_id: int):
        return self.car_repo.delete(car_id)