from pydantic import BaseModel, Field, ConfigDict


class RentalStatusBase(BaseModel):
    status: str = Field(..., examples=["Активна"])


class RentalStatusCreate(RentalStatusBase):
    pass


class RentalStatusRead(RentalStatusBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RentalStatusUpdate(RentalStatusBase):
    id: int

    model_config = ConfigDict(from_attributes=True)