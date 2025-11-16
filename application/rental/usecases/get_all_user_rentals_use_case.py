from typing import List

from sqlalchemy.orm import Session

from application.rental.schemas import RentalRead
from infrastructure.database.repository import RentalRepository


class GetAllUserRentalsUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.rental_repo = RentalRepository(db)

    def execute(self, current_user_id: int) -> List[RentalRead]:
        rentals = self.rental_repo.get_by_user_id(current_user_id)
        return [RentalRead.model_validate(r) for r in rentals]