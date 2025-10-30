from sqlalchemy import BigInteger, Column, String
from sqlalchemy.orm import relationship

from .base import Base


class CarColorEntity(Base):
    __tablename__ = 'car_colors'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    color = Column(String(50), nullable=False)

    cars = relationship("CarEntity", back_populates="color", cascade="all, delete-orphan")