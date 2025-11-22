from sqlalchemy.orm import Session

from infrastructure.database.repository import RentalRepository


class DeleteRentalUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.rental_repo = RentalRepository(db)

    def execute(self, rental_id: int):
        return self.rental_repo.delete(rental_id)