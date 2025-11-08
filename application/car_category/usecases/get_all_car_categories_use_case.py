from typing import List

from sqlalchemy.orm import Session

from application.car_category.schemas import CarCategoryRead
from infrastructure.database.repository import CarCategoryRepository


class GetAllCarCategoriesUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_category_repo = CarCategoryRepository(db)

    def execute(self) -> List[CarCategoryRead]:
        categories = self.car_category_repo.get_all()
        return [CarCategoryRead.model_validate(c) for c in categories]