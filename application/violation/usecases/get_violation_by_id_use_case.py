from sqlalchemy.orm import Session

from application.violation.schemas import ViolationRead
from infrastructure.database.repository import ViolationRepository


class GetViolationByIdUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.violation_repo = ViolationRepository(db)

    def execute(self, violation_id: int) -> ViolationRead:
        violation = self.violation_repo.get_by_id(violation_id)
        return ViolationRead.model_validate(violation)