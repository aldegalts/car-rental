from decimal import Decimal
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.database.models import ViolationTypeEntity


class ViolationTypeRepository:
    def __init__(self, session: Session):
        self.session = session


    def get_by_id(self, type_id: int) -> Optional[ViolationTypeEntity]:
        return self.session.get(ViolationTypeEntity, type_id)

    def get_all(self) -> List[ViolationTypeEntity]:
        return list(
            self.session.scalars(
                select(ViolationTypeEntity)
            )
            .all()
        )

    def create(self, type_name: str, default_fine: Decimal, description: str) -> ViolationTypeEntity:
        v_type_obj = ViolationTypeEntity(
            type_name=type_name,
            default_fine=default_fine,
            description=description,
        )
        self.session.add(v_type_obj)
        self.session.commit()
        self.session.refresh(v_type_obj)
        return v_type_obj

    def delete(self, type_id: int):
        v_type = self.session.query(ViolationTypeEntity).filter(ViolationTypeEntity.id == type_id).first()
        if v_type:
            self.session.delete(v_type)
            self.session.commit()

    def update(self, type_id: int, type_name: str, default_fine: Decimal, description: str) -> ViolationTypeEntity:
        type_obj = self.session.get(ViolationTypeEntity, type_id)
        type_obj.type_name = type_name
        type_obj.default_fine = default_fine
        type_obj.description = description
        self.session.commit()
        self.session.refresh(type_obj)
        return type_obj