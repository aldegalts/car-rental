from sqlalchemy.orm import Session

from application.car_status.schemas import CarStatusCreate, CarStatusRead
from infrastructure.database.repository import CarStatusRepository


class CreateCarStatusUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_status_repo = CarStatusRepository(db)

    def execute(self, status_data: CarStatusCreate) -> CarStatusRead:
        status_obj = self.car_status_repo.create(status=status_data.status)
        return CarStatusRead.model_validate(status_obj)