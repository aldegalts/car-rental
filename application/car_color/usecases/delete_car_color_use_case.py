from sqlalchemy.orm import Session

from infrastructure.database.repository import CarColorRepository


class DeleteCarColorUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_color_repo = CarColorRepository(db)

    def execute(self, color_id: int):
        return self.car_color_repo.delete(color_id)