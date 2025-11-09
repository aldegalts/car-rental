from sqlalchemy.orm import Session

from application.violation_type.schemas import ViolationTypeCreate, ViolationTypeRead
from infrastructure.database.repository import ViolationTypeRepository


class CreateViolationTypeUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.violation_type_repo = ViolationTypeRepository(db)

    def execute(self, violation_type_data: ViolationTypeCreate) -> ViolationTypeRead:
        violation_type_obj = self.violation_type_repo.create(
            type_name=violation_type_data.type_name,
            default_fine=violation_type_data.default_fine,
            description=violation_type_data.description
        )
        return ViolationTypeRead.model_validate(violation_type_obj)