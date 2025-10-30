from sqlalchemy import Column, BigInteger, String, Numeric, Text
from sqlalchemy.orm import relationship

from .base import Base


class CarCategoryEntity(Base):
    __tablename__ = "car_categories"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    base_cost = Column(Numeric(10, 2), nullable=False)

    cars = relationship("CarEntity", back_populates="category", cascade="all, delete-orphan")
