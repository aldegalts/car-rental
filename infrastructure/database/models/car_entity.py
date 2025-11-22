from sqlalchemy import Column, BigInteger, String, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from .base import Base


class CarEntity(Base):
    __tablename__ = 'cars'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    category_id = Column(BigInteger, ForeignKey("car_categories.id"), nullable=False)
    license_plate = Column(String(20), nullable=False, unique=True)
    color_id = Column(BigInteger, ForeignKey("car_colors.id"), nullable=False)
    daily_cost = Column(Numeric(10, 2), nullable=False)
    car_status_id = Column(BigInteger, ForeignKey("car_statuses.id"), nullable=False)

    car_status = relationship("CarStatusEntity", back_populates="cars")
    color = relationship("CarColorEntity", back_populates="cars")
    category = relationship("CarCategoryEntity", back_populates="cars")
