from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class CarCategoryBase(BaseModel):
    category_name: str = Field(..., examples=["Эконом"])
    description: str = Field(..., examples=["Компактные и экономичные машины"])
    base_cost: Decimal = Field(..., examples=["1500.00"])


class CarCategoryCreate(CarCategoryBase):
    pass


class CarCategoryRead(CarCategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CarCategoryUpdate(CarCategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)