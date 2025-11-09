from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class RentalBase(BaseModel):
    client_id: int
    car_id: int
    start_date: datetime
    end_date: datetime
    total_amount: Decimal
    rental_status_id: int


class RentalCreate(RentalBase):
    pass


class RentalUpdate(RentalBase):
    id: int = Field(..., examples=[1])

    model_config = ConfigDict(from_attributes=True)


class RentalRead(RentalBase):
    id: int = Field(..., examples=[1])

    model_config = ConfigDict(from_attributes=True)