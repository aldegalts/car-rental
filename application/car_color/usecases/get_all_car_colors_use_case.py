from typing import List

from sqlalchemy.orm import Session

from application.car_color.schemas import CarColorRead
from infrastructure.database.repository import CarColorRepository


class GetAllCarColorsUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_color_repo = CarColorRepository(db)

    def execute(self) -> List[CarColorRead]:
        colors = self.car_color_repo.get_all()
        return [CarColorRead.model_validate(c) for c in colors]