from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from application.car.schemas import CarUpdate, CarRead
from infrastructure.database.repository import CarRepository


class UpdateCarUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_repo = CarRepository(db)

    def execute(self, car_data: CarUpdate) -> CarRead:
        car = self.car_repo.get_by_id(car_data.id)
        if car is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")

        car_res = self.car_repo.update(
            brand=car_data.brand,
            model=car_data.model,
            year=car_data.year,
            category_id=car_data.category_id,
            license_plate=car_data.license_plate,
            color_id=car_data.color_id,
            daily_cost=car_data.daily_cost,
            car_status_id=car_data.car_status_id
        )

        return CarRead.model_validate(car_res)