from datetime import datetime
from sqlalchemy.orm import Session

from infrastructure.database.repository import (
    RentalRepository,
    CarRepository,
    CarStatusRepository,
    RentalStatusRepository,
)


class CompleteExpiredRentalsUseCase:
    ACTIVE_RENTAL_STATUS = "Активна"
    COMPLETED_RENTAL_STATUS = "Завершена"
    RENTED_CAR_STATUS = "В аренде"
    AVAILABLE_CAR_STATUS = "Доступна для аренды"

    def __init__(self, db: Session):
        self.db = db
        self.rental_repo = RentalRepository(db)
        self.car_repo = CarRepository(db)
        self.car_status_repo = CarStatusRepository(db)
        self.rental_status_repo = RentalStatusRepository(db)

    def execute(self) -> int:
        active_status = self.rental_status_repo.get_by_status(self.ACTIVE_RENTAL_STATUS)
        if active_status is None:
            return 0

        completed_status = self.rental_status_repo.get_by_status(self.COMPLETED_RENTAL_STATUS)
        if completed_status is None:
            try:
                completed_status = self.rental_status_repo.create(self.COMPLETED_RENTAL_STATUS)
            except Exception:
                return 0

        available_car_status = self.car_status_repo.get_by_status(self.AVAILABLE_CAR_STATUS)
        if available_car_status is None:
            try:
                available_car_status = self.car_status_repo.create(self.AVAILABLE_CAR_STATUS)
            except Exception:
                return 0

        expired_rentals = self.rental_repo.get_expired_active_rentals(active_status.id)

        completed_count = 0
        for rental in expired_rentals:
            try:
                self.rental_repo.update_status(rental.id, completed_status.id)

                self.car_repo.update_status(rental.car_id, available_car_status.id)
                completed_count += 1
            except Exception:
                continue

        return completed_count



