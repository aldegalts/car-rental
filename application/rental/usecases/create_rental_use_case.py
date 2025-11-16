from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from application.rental.schemas import RentalCreate, RentalRead
from infrastructure.database.repository import RentalRepository, CarRepository


class CreateRentalUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.rental_repo = RentalRepository(db)
        self.car_repo = CarRepository(db)

    def execute(self, rental_data: RentalCreate) -> RentalRead:
        car = self.car_repo.get_by_id(rental_data.car_id)
        if car.car_status != "Доступна для аренды":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The car is not available for rent")

        rental_obj = self.rental_repo.create(
            client_id=rental_data.client_id,
            car_id=rental_data.car_id,
            start_date=rental_data.start_date,
            end_date=rental_data.end_date,
            total_amount=rental_data.total_amount,
            rental_status_id=rental_data.rental_status_id
            )
        return RentalRead.model_validate(rental_obj)