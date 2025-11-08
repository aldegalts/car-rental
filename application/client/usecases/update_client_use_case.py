from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from application.client.schemas import ClientUpdate, ClientRead
from infrastructure.database.repository import ClientRepository


class UpdateClientUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.client_repo = ClientRepository(db)

    def execute(self, client_data: ClientUpdate) -> ClientRead:
        client = self.client_repo.get_by_id(client_data.id)
        if client is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")

        client_res = self.client_repo.update(
            client_id=client_data.id,
            name = client_data.name,
            surname = client_data.username,
            phone = client_data.phone,
            email = client_data.email,
            driver_license = client_data.driver_license
        )

        return ClientRead.model_validate(client_res)