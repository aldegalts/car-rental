from sqlalchemy.orm import Session

from infrastructure.database.repository import CarCategoryRepository


class DeleteCarCategoryUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.car_category_repo = CarCategoryRepository(db)

    def execute(self, category_id: int):
        return self.car_category_repo.delete(category_id)