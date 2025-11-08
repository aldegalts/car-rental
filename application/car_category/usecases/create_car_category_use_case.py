from sqlalchemy.orm import Session

from application.car_category.schemas import CarCategoryCreate, CarCategoryRead
from infrastructure.database.repository import CarCategoryRepository


class CreateCarCategoryUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_category_repo = CarCategoryRepository(db)

    def execute(self, category_data: CarCategoryCreate) -> CarCategoryRead:
        category_obj = self.car_category_repo.create(
            category_name=category_data.category_name,
            description=category_data.description,
            base_cost=category_data.base_cost)
        return CarCategoryRead.model_validate(category_obj)