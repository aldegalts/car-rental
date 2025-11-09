from sqlalchemy.orm import Session

from infrastructure.database.repository import RentalStatusRepository


class DeleteRentalStatusUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.rental_status_repo = RentalStatusRepository(db)

    def execute(self, status_id: int):
        return self.rental_status_repo.delete(status_id)