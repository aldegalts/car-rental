from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from application.rental_status.schemas import RentalStatusUpdate, RentalStatusRead
from infrastructure.database.repository import RentalStatusRepository


class UpdateRentalStatusUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.rental_status_repo = RentalStatusRepository(db)

    def execute(self, status_data: RentalStatusUpdate) -> RentalStatusRead:
        rental_status = self.rental_status_repo.get_by_id(status_data.id)
        if rental_status is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")

        status_res = self.rental_status_repo.update(status_data.id, status_data.status)

        return RentalStatusRead.model_validate(status_res)