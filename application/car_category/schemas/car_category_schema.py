from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class CarCategoryBase(BaseModel):
    category_name: str = Field(..., examples=["Economy"])
    description: str = Field(..., examples=["Budget-friendly small cars"])
    base_cost: Decimal = Field(..., examples=["45.00"])


class CarCategoryCreate(CarCategoryBase):
    pass


class CarCategoryRead(CarCategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CarCategoryUpdate(CarCategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)