from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from application.client.schemas import ClientRead
from infrastructure.database.repository import ClientRepository


class GetClientByUserIdUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.client_repo = ClientRepository(db)

    def execute(self, user_id: int) -> ClientRead:
        client = self.client_repo.get_by_user_id(user_id)
        if client is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Клиент не найден")

        return ClientRead.model_validate(client)







