from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from application.client.schemas import ClientRead
from infrastructure.database.repository import ClientRepository


class GetClientByIdUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.client_repo = ClientRepository(db)

    def execute(self, client_id) -> ClientRead:
        client = self.client_repo.get_by_id(client_id)
        if client is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

        return ClientRead.model_validate(client)