from sqlalchemy.orm import Session

from infrastructure.database.repository import ViolationRepository


class DeleteViolationUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.violation_repo = ViolationRepository(db)

    def execute(self, violation_id: int):
        return self.violation_repo.delete(violation_id)