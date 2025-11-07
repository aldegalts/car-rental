from sqlalchemy.orm import Session

from infrastructure.database.repository import CarStatusRepository


class DeleteCarStatusUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_status_repo = CarStatusRepository(db)

    def execute(self, status_id: int):
        return self.car_status_repo.delete(status_id)