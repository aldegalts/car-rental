from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.database.models import CarColorEntity


class CarColorRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, color_id: int) -> Optional[CarColorEntity]:
        return self.session.get(CarColorEntity, color_id)

    def get_all(self) -> List[CarColorEntity]:
        return list(
            self.session.scalars(
                select(CarColorEntity)
            )
            .all()
        )

    def create(self, color: str, color_hex: str) -> CarColorEntity:
        color_obj = CarColorEntity(color=color, hex=color_hex)
        self.session.add(color_obj)
        self.session.commit()
        self.session.refresh(color_obj)
        return color_obj

    def delete(self, color_id: int):
        color = self.session.query(CarColorEntity).filter(CarColorEntity.id == color_id).first()
        if color:
            self.session.delete(color)
            self.session.commit()

    def update(self, color_id: int, color_name: str, color_hex: str) -> CarColorEntity:
        color_obj = self.session.get(CarColorEntity, color_id)
        color_obj.color = color_name
        color_obj.hex = color_hex
        self.session.commit()
        self.session.refresh(color_obj)
        return color_obj