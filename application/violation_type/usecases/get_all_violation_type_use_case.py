from typing import List

from sqlalchemy.orm import Session

from application.violation_type.schemas import ViolationTypeRead
from infrastructure.database.repository import ViolationTypeRepository


class GetAllViolationTypesUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.violation_type_repo = ViolationTypeRepository(db)

    def execute(self) -> List[ViolationTypeRead]:
        types = self.violation_type_repo.get_all()
        return [ViolationTypeRead.model_validate(t) for t in types]