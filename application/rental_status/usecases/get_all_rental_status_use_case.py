from typing import List

from sqlalchemy.orm import Session

from application.rental_status.schemas import RentalStatusRead
from infrastructure.database.repository import RentalStatusRepository


class GetAllRentalStatusesUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.rental_status_repo = RentalStatusRepository(db)

    def execute(self) -> List[RentalStatusRead]:
        statuses = self.rental_status_repo.get_all()
        return [RentalStatusRead.model_validate(s) for s in statuses]