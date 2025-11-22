from typing import List

from sqlalchemy.orm import Session

from application.violation.schemas import ViolationRead
from infrastructure.database.repository import ViolationRepository


class GetAllUserViolationsUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.violation_repo = ViolationRepository(db)

    def execute(self, current_user_id: int) -> List[ViolationRead]:
        violations = self.violation_repo.get_by_user_id(current_user_id)
        return [ViolationRead.model_validate(v) for v in violations]