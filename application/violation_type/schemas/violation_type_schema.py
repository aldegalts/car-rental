from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class ViolationTypeBase(BaseModel):
    type_name: str = Field(..., examples=["Нарушение правил дорожного движения"])
    daily_cost: Decimal = Field(..., examples=["500.00"])
    description: str = Field(..., examples=["Включает в себя оплату административного сбора компании за обработку штрафа и оплату штрафа за нарушение ПДД (например, превышение скорости или проезд на красный свет)."])


class ViolationTypeCreate(ViolationTypeBase):
    pass


class ViolationTypeUpdate(ViolationTypeBase):
    id: int = Field(..., examples=[1])

    model_config = ConfigDict(from_attributes=True)


class ViolationTypeRead(ViolationTypeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)