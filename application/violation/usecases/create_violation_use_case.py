from sqlalchemy.orm import Session

from application.violation.schemas import ViolationCreate, ViolationRead
from infrastructure.database.repository import ViolationRepository


class CreateViolationUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.violation_repo = ViolationRepository(db)

    def execute(self, violation_data: ViolationCreate) -> ViolationRead:
        violation_obj = self.violation_repo.create(
            rental_id=violation_data.rental_id,
            violation_type_id=violation_data.violation_type_id,
            description=violation_data.description,
            fine_amount=violation_data.fine_amount,
            violation_date=violation_data.violation_date,
            is_paid=violation_data.is_paid
            )
        return ViolationRead.model_validate(violation_obj)