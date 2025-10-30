from sqlalchemy import Column, BigInteger, ForeignKey, DateTime, func, Numeric
from sqlalchemy.orm import relationship

from .base import Base


class RentalEntity(Base):
    __tablename__ = "rentals"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    client_id = Column(BigInteger, ForeignKey("clients.id"), nullable=False)
    car_id = Column(BigInteger, ForeignKey("cars.id"), nullable=False)
    start_date = Column(DateTime(timezone=False), nullable=False, server_default=func.now())
    end_date = Column(DateTime(timezone=False), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    rental_status_id = Column(BigInteger, ForeignKey("rental_status.id"), nullable=False)

    violations = relationship("ViolationEntity", back_populates="rental", cascade="all, delete-orphan")
    rental_status = relationship("RentalStatusEntity", back_populates="rentals")