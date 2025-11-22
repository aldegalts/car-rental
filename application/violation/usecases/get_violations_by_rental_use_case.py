from typing import List

from sqlalchemy.orm import Session

from application.violation.schemas import ViolationRead
from infrastructure.database.repository import ViolationRepository


class GetViolationsByRentalUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.violation_repo = ViolationRepository(db)

    def execute(self, rental_id: int) -> List[ViolationRead]:
        violations = self.violation_repo.get_by_rental_id(rental_id)
        return [ViolationRead.model_validate(v) for v in violations]


