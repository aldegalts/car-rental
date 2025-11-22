from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from application.violation.schemas import ViolationUpdate, ViolationRead
from infrastructure.database.repository import ViolationRepository


class UpdateViolationUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.violation_repo = ViolationRepository(db)

    def execute(self, violation_data: ViolationUpdate) -> ViolationRead:
        violation = self.violation_repo.get_by_id(violation_data.id)
        if violation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Нарушение не найдено")

        violation_res = self.violation_repo.update(
            violation_id=violation_data.id,
            rental_id=violation_data.rental_id,
            violation_type_id=violation_data.violation_type_id,
            description=violation_data.description,
            fine_amount=violation_data.fine_amount,
            violation_date=violation_data.violation_date,
            is_paid=violation_data.is_paid
        )

        return ViolationRead.model_validate(violation_res)