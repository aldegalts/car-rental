from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class ViolationBase(BaseModel):
    rental_id: int = Field(..., examples=[1])
    violation_type_id: int = Field(..., examples=[1])
    description: str = Field(..., examples=["Проезд на красный свет"])
    fine_amount: Decimal = Field(..., examples=[500.00])
    violation_date: datetime
    is_paid: bool = Field(..., examples=[True])


class ViolationCreate(ViolationBase):
    pass


class ViolationUpdate(ViolationBase):
    id: int = Field(..., examples=[1])

    model_config = ConfigDict(from_attributes=True)


class ViolationRead(ViolationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)