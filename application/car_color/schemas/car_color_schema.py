from pydantic import BaseModel, Field, ConfigDict


class CarColorBase(BaseModel):
    color: str = Field(..., examples=["Red"])
    hex: str = Field(..., examples=["#FF0000"])


class CarColorCreate(CarColorBase):
    pass


class CarColorRead(CarColorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CarColorUpdate(CarColorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)