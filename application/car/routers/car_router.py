from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.car.schemas import CarRead, CarCreate, CarUpdate, CarFilter
from application.car.usecases import CreateCarUseCase, DeleteCarUseCase, GetAllCarUseCase, UpdateCarUseCase, \
    GetCarUseCase, FilterCarUseCase
from application.dependencies import get_current_user
from infrastructure.database.database_session import get_db
from infrastructure.database.models import UserEntity

router = APIRouter(prefix="/cars", tags=["Cars"])


@router.get("/", response_model=List[CarRead])
def get_all_cars(
        db: Session = Depends(get_db)
):
    return GetAllCarUseCase(db).execute()


@router.get("/filter", response_model=List[CarRead])
def filter_cars(
    brand: Optional[str] = None,
    model: Optional[str] = None,
    category_id: Optional[int] = None,
    color_id: Optional[int] = None,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    min_cost: Optional[Decimal] = None,
    max_cost: Optional[Decimal] = None,
    db: Session = Depends(get_db)
):
    filters = CarFilter(
        brand=brand,
        model=model,
        category_id=category_id,
        color_id=color_id,
        min_year=min_year,
        max_year=max_year,
        min_cost=min_cost,
        max_cost=max_cost,
    )

    return FilterCarUseCase(db).execute(filters)


@router.get("/{car_id}", response_model=CarRead)
def get_car_by_id(
        car_id: int,
        db: Session = Depends(get_db)
):
    return GetCarUseCase(db).execute(car_id)


@router.post("/", response_model=CarRead, status_code=status.HTTP_201_CREATED)
def add_car(
    car_data: CarCreate,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только администратор может добавлять машины")

    return CreateCarUseCase(db).execute(car_data)


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(
    car_id: int,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только администратор может удалять машины")

    DeleteCarUseCase(db).execute(car_id)
    return {"detail": "Car deleted successfully"}


@router.put("/{car_id}", response_model=CarRead)
def update_car(
    car_data: CarUpdate,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только администратор может изменять машины")

    return UpdateCarUseCase(db).execute(car_data)