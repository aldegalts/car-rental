from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship

from .base import Base


class CarStatusEntity(Base):
    __tablename__ = "car_statuses"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    status = Column(String(50), nullable=False, unique=True)

    cars = relationship("CarEntity", back_populates="car_status", cascade="all, delete-orphan")