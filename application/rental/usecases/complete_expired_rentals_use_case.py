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
        """
        Завершает все истекшие активные аренды и освобождает автомобили.
        Возвращает количество завершенных аренд.
        """
        # Получаем статусы
        active_status = self.rental_status_repo.get_by_status(self.ACTIVE_RENTAL_STATUS)
        if active_status is None:
            return 0

        completed_status = self.rental_status_repo.get_by_status(self.COMPLETED_RENTAL_STATUS)
        if completed_status is None:
            # Пытаемся создать статус "Завершена", если его нет
            try:
                completed_status = self.rental_status_repo.create(self.COMPLETED_RENTAL_STATUS)
            except Exception:
                return 0

        available_car_status = self.car_status_repo.get_by_status(self.AVAILABLE_CAR_STATUS)
        if available_car_status is None:
            # Пытаемся создать статус "Доступна для аренды", если его нет
            try:
                available_car_status = self.car_status_repo.create(self.AVAILABLE_CAR_STATUS)
            except Exception:
                return 0

        # Получаем истекшие активные аренды
        expired_rentals = self.rental_repo.get_expired_active_rentals(active_status.id)

        # Завершаем каждую аренду и освобождаем автомобиль
        completed_count = 0
        for rental in expired_rentals:
            try:
                # Обновляем статус аренды на "Завершена"
                self.rental_repo.update_status(rental.id, completed_status.id)

                # Освобождаем автомобиль (меняем статус на "Доступна для аренды")
                self.car_repo.update_status(rental.car_id, available_car_status.id)
                completed_count += 1
            except Exception:
                # Пропускаем аренду при ошибке, продолжаем обработку остальных
                continue

        return completed_count

