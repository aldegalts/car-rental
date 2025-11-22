from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from application.violation.schemas import ViolationRead
from infrastructure.database.repository import ViolationRepository


class GetUserViolationByIdUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.violation_repo = ViolationRepository(db)

    def execute(self, current_user_id: int, violation_id: int) -> ViolationRead:
        violation = self.violation_repo.get_by_user_and_id(current_user_id, violation_id)
        if violation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Нарушение не найдено"
            )
        return ViolationRead.model_validate(violation)