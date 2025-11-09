from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from application.violation_type.schemas import ViolationTypeUpdate, ViolationTypeRead
from infrastructure.database.repository import ViolationTypeRepository


class UpdateViolationTypeUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.violation_type_repo = ViolationTypeRepository(db)

    def execute(self, type_data: ViolationTypeUpdate) -> ViolationTypeRead:
        v_type = self.violation_type_repo.get_by_id(type_data.id)
        if v_type is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")

        v_type_res = self.violation_type_repo.update(
            type_id=type_data.id,
            type_name=type_data.type_name,
            default_fine=type_data.default_fine,
            description=type_data.description
        )

        return ViolationTypeRead.model_validate(v_type_res)