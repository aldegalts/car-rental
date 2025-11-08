from decimal import Decimal
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.database.models import CarCategoryEntity


class CarCategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, category_name: str, description: str, base_cost: Decimal) -> CarCategoryEntity:
        category_obj = CarCategoryEntity(category_name=category_name, description=description, base_cost=base_cost)
        self.session.add(category_obj)
        self.session.commit()
        self.session.refresh(category_obj)
        return category_obj

    def delete(self, category_id: int):
        category = self.session.query(CarCategoryEntity).filter(CarCategoryEntity.id == category_id).first()
        if category:
            self.session.delete(category)
            self.session.commit()

    def get_by_id(self, category_id: int) -> Optional[CarCategoryEntity]:
        return self.session.get(CarCategoryEntity, category_id)

    def update(self, category_id: int, category_name: str, description: str, base_cost: Decimal) -> CarCategoryEntity:
        category_obj = self.session.get(CarCategoryEntity, category_id)
        category_obj.category_name = category_name
        category_obj.description = description
        category_obj.base_cost = base_cost
        self.session.commit()
        self.session.refresh(category_obj)
        return category_obj

    def get_all(self) -> List[CarCategoryEntity]:
        return list(
            self.session.scalars(
                select(CarCategoryEntity)
            )
            .all()
        )