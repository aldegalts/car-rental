from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from application.car_status.schemas import CarStatusUpdate, CarStatusRead
from infrastructure.database.repository import CarStatusRepository


class UpdateCarStatusUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_status_repo = CarStatusRepository(db)

    def execute(self, status_data: CarStatusUpdate) -> CarStatusRead:
        car_status = self.car_status_repo.get_by_id(status_data.id)
        if car_status is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Статус не найден")

        status_res = self.car_status_repo.update(status_data.id, status_data.status)

        return CarStatusRead.model_validate(status_res)