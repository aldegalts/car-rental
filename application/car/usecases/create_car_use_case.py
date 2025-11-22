from sqlalchemy.orm import Session

from application.car.schemas import CarCreate, CarRead
from infrastructure.database.repository import CarRepository


class CreateCarUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_repo = CarRepository(db)

    def execute(self, car_data: CarCreate) -> CarRead:
        car_obj = self.car_repo.create(
            brand=car_data.brand,
            model=car_data.model,
            year=car_data.year,
            category_id=car_data.category_id,
            license_plate=car_data.license_plate,
            color_id=car_data.color_id,
            daily_cost=car_data.daily_cost,
            car_status_id=car_data.car_status_id,
            )
        return CarRead.model_validate(car_obj)