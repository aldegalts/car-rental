from typing import List

from sqlalchemy.orm import Session

from application.rental.schemas import RentalRead, RentalFilter
from infrastructure.database.repository import RentalRepository
from application.rental.usecases.complete_expired_rentals_use_case import CompleteExpiredRentalsUseCase


class GetAllRentalsUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.rental_repo = RentalRepository(db)

    def execute(self, filters: RentalFilter) -> List[RentalRead]:
        # Автоматически завершаем истекшие аренды перед получением списка
        CompleteExpiredRentalsUseCase(self.db).execute()
        
        rentals = self.rental_repo.filter(
            car_id=filters.car_id,
            client_id=filters.client_id
        )
        return [RentalRead.model_validate(r) for r in rentals]