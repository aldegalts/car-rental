from pydantic import BaseModel, Field, ConfigDict


class CarStatusBase(BaseModel):
    status: str = Field(..., examples=["Comfort"])


class CarStatusCreate(CarStatusBase):
    pass


class CarStatusRead(CarStatusBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CarStatusUpdate(CarStatusBase):
    id: int

    model_config = ConfigDict(from_attributes=True)