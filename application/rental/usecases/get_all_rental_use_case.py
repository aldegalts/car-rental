from typing import List

from sqlalchemy.orm import Session

from application.rental.schemas import RentalRead
from infrastructure.database.repository import RentalRepository


class GetAllRentalUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.rental_repo = RentalRepository(db)

    def execute(self) -> List[RentalRead]:
        rentals = self.rental_repo.get_all()
        return [RentalRead.model_validate(r) for r in rentals]