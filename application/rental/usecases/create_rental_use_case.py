from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from application.rental.schemas import RentalCreate, RentalRead
from infrastructure.database.repository import (
    RentalRepository,
    CarRepository,
    CarStatusRepository,
    RentalStatusRepository,
)


class CreateRentalUseCase:
    ACTIVE_RENTAL_STATUS = "Активна"
    RENTED_CAR_STATUS = "В аренде"

    def __init__(self, db: Session):
        self.db = db
        self.rental_repo = RentalRepository(db)
        self.car_repo = CarRepository(db)
        self.car_status_repo = CarStatusRepository(db)
        self.rental_status_repo = RentalStatusRepository(db)

    def execute(self, rental_data: RentalCreate) -> RentalRead:
        car = self.car_repo.get_by_id(rental_data.car_id)
        if car is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")

        current_car_status = getattr(car.car_status, "status", None)
        if current_car_status and current_car_status.lower() == self.RENTED_CAR_STATUS.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The car is not available for rent")

        rental_status_id = rental_data.rental_status_id
        if rental_status_id is None:
            rental_status = self.rental_status_repo.get_by_status(self.ACTIVE_RENTAL_STATUS)
            if rental_status is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Active rental status is not configured"
                )
            rental_status_id = rental_status.id

        rental_obj = self.rental_repo.create(
            client_id=rental_data.client_id,
            car_id=rental_data.car_id,
            start_date=rental_data.start_date,
            end_date=rental_data.end_date,
            total_amount=rental_data.total_amount,
            rental_status_id=rental_status_id
            )

        rented_status = self.car_status_repo.get_by_status(self.RENTED_CAR_STATUS)
        if rented_status is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Rented car status is not configured"
            )
        self.car_repo.update_status(rental_data.car_id, rented_status.id)

        return RentalRead.model_validate(rental_obj)