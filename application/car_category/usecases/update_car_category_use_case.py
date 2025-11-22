from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from application.car_category.schemas import CarCategoryUpdate, CarCategoryRead
from infrastructure.database.repository import CarCategoryRepository


class UpdateCarCategoryUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_category_repo = CarCategoryRepository(db)

    def execute(self, category_data: CarCategoryUpdate) -> CarCategoryRead:
        car_category = self.car_category_repo.get_by_id(category_data.id)
        if car_category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Статус не найден")

        category_res = self.car_category_repo.update(
            category_id=category_data.id,
            category_name=category_data.category_name,
            description=category_data.description,
            base_cost=category_data.base_cost)

        return CarCategoryRead.model_validate(category_res)