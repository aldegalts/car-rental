from sqlalchemy.orm import Session

from application.client.schemas import ClientCreate, ClientRead
from infrastructure.database.repository import ClientRepository


class CreateClientUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.client_repo = ClientRepository(db)

    def execute(self, client_data: ClientCreate) -> ClientRead:
        client_obj = self.client_repo.create(
            name=client_data.name,
            surname=client_data.surname,
            birth_date=client_data.birth_date,
            phone=client_data.phone,
            email=client_data.email,
            driver_license=client_data.driver_license,
            license_expiry_date=client_data.license_expiry_date,
            user_id=client_data.user_id
            )
        return ClientRead.model_validate(client_obj)