from typing import List

from sqlalchemy.orm import Session

from application.car_status.schemas import CarStatusRead
from infrastructure.database.repository import CarStatusRepository


class GetAllCarStatusesUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_status_repo = CarStatusRepository(db)

    def execute(self) -> List[CarStatusRead]:
        statuses = self.car_status_repo.get_all()
        return [CarStatusRead.model_validate(s) for s in statuses]