from sqlalchemy.orm import Session

from application.rental_status.schemas import RentalStatusCreate, RentalStatusRead
from infrastructure.database.repository import RentalStatusRepository


class CreateRentalStatusUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.rental_status_repo = RentalStatusRepository(db)

    def execute(self, status_data: RentalStatusCreate) -> RentalStatusRead:
        status_obj = self.rental_status_repo.create(status=status_data.status)
        return RentalStatusRead.model_validate(status_obj)