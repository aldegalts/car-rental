from typing import List

from sqlalchemy.orm import Session

from application.client.schemas import ClientRead
from infrastructure.database.repository import ClientRepository


class GetAllClientsUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.client_repo = ClientRepository(db)

    def execute(self) -> List[ClientRead]:
        clients = self.client_repo.get_all()
        return [ClientRead.model_validate(c) for c in clients]