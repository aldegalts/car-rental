from sqlalchemy.orm import Session

from application.rental.schemas import RentalRead
from infrastructure.database.repository import RentalRepository


class GetRentalByIdUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.rental_repo = RentalRepository(db)

    def execute(self, rental_id: int) -> RentalRead:
        rental = self.rental_repo.get_by_id(rental_id)
        return RentalRead.model_validate(rental)