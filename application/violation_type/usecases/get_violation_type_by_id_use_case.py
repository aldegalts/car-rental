from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from application.violation_type.schemas import ViolationTypeRead
from infrastructure.database.repository import ViolationTypeRepository


class GetViolationTypeByIdUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.violation_type_repo = ViolationTypeRepository(db)

    def execute(self, type_id: int) -> ViolationTypeRead:
        violation_type = self.violation_type_repo.get_by_id(type_id)
        if violation_type is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тип нарушения не найден")

        return ViolationTypeRead.model_validate(violation_type)




