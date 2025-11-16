from datetime import date
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.database.models import ClientEntity


class ClientRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
            self, name: str, surname: str,
            birth_date: date, phone: str, email: str,
            driver_license: str, license_expiry_date: date, user_id: int
    ) -> ClientEntity:
        client_obj = ClientEntity(
            name=name,
            surname=surname,
            birth_date=birth_date,
            phone=phone,
            email=email,
            driver_license=driver_license,
            license_expiry_date=license_expiry_date,
            user_id=user_id
        )
        self.session.add(client_obj)
        self.session.commit()
        self.session.refresh(client_obj)
        return client_obj

    def get_by_id(self, client_id: int) -> Optional[ClientEntity]:
        return self.session.get(ClientEntity, client_id)

    def get_all(self) -> List[ClientEntity]:
        return list(
            self.session.scalars(
                select(ClientEntity)
            )
            .all()
        )

    def update(
            self, client_id: int, name: str, surname: str, phone: str, email: str, driver_license: str
    ) -> ClientEntity:
        client_obj = self.session.get(ClientEntity, client_id)
        client_obj.name = name
        client_obj.surname = surname
        client_obj.phone = phone
        client_obj.email = email
        client_obj.driver_license = driver_license
        self.session.commit()
        self.session.refresh(client_obj)
        return client_obj