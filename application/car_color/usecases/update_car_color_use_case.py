from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from application.car_color.schemas import CarColorUpdate, CarColorRead
from infrastructure.database.repository import CarColorRepository


class UpdateCarColorUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_color_repo = CarColorRepository(db)

    def execute(self, color_data: CarColorUpdate) -> CarColorRead:
        color = self.car_color_repo.get_by_id(color_data.id)
        if color is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Color not found")

        color_res = self.car_color_repo.update(color_data.id, color_data.color, color_data.hex)

        return CarColorRead.model_validate(color_res)