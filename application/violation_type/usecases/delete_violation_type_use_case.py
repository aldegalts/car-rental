from sqlalchemy.orm import Session

from infrastructure.database.repository import ViolationTypeRepository


class DeleteViolationTypeUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.violation_type_repo = ViolationTypeRepository(db)

    def execute(self, type_id: int):
        return self.violation_type_repo.delete(type_id)