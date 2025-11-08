from datetime import date

from pydantic import BaseModel, ConfigDict


class ClientBase(BaseModel):
    name: str
    surname: str
    birth_date: date
    phone: str
    email: str
    driver_license: str
    license_expiry_date: date
    user_id: id


class ClientCreate(ClientBase):
    id: int


class ClientUpdate(ClientBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ClientRead(ClientBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
