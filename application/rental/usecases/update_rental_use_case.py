from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from application.rental.schemas import RentalRead, RentalUpdate
from infrastructure.database.repository import RentalRepository


class UpdateRentalUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.rental_repo = RentalRepository(db)

    def execute(self, rental_data: RentalUpdate) -> RentalRead:
        rental = self.rental_repo.get_by_id(rental_data.id)
        if rental is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Аренда не найдена")

        rental_res = self.rental_repo.update(
            rental_id=rental.id,
            car_id=rental.car_id,
            start_date=rental.start_date,
            end_date=rental.end_date,
            total_amount=rental.total_amount,
            rental_status_id=rental.rental_status_id
        )

        return RentalRead.model_validate(rental_res)