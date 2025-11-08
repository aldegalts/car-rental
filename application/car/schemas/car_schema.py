from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class CarBase(BaseModel):
    brand: str = Field(..., examples=["Porsche"])
    model: str = Field(..., examples=["911"])
    year: int = Field(..., examples=[2025])
    category_id: int = Field(..., examples=[1])
    license_plate: str = Field(..., examples=["А111АА"])
    color_id: int = Field(..., examples=[1])
    daily_cost: Decimal = Field(..., examples=["70000.00"])
    car_status_id: int = Field(..., examples=[1])


class CarCreate(CarBase):
    pass


class CarUpdate(CarBase):
    id: int = Field(..., examples=[1])

    model_config = ConfigDict(from_attributes=True)


class CarRead(CarBase):
    id: int

    model_config = ConfigDict(from_attributes=True)