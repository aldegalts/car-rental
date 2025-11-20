from sqlalchemy.orm import Session

from application.rental.schemas import RentalRead
from infrastructure.database.repository import RentalRepository
from application.rental.usecases.complete_expired_rentals_use_case import CompleteExpiredRentalsUseCase


class GetUserRentalByIdUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.rental_repo = RentalRepository(db)

    def execute(self, current_user_id: int, rental_id: int) -> RentalRead:
        # Автоматически завершаем истекшие аренды перед получением
        CompleteExpiredRentalsUseCase(self.db).execute()
        
        rental = self.rental_repo.get_by_user_and_id(current_user_id, rental_id)
        return RentalRead.model_validate(rental)