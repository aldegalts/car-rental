from sqlalchemy.orm import Session

from application.car_color.schemas import CarColorCreate, CarColorRead
from infrastructure.database.repository import CarColorRepository


class CreateCarColorUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_color_repo = CarColorRepository(db)

    def execute(self, color_data: CarColorCreate) -> CarColorRead:
        color_obj = self.car_color_repo.create(color=color_data.color, color_hex=color_data.hex)
        return CarColorRead.model_validate(color_obj)