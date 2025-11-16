from typing import List

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


@router.get("/{car_id}", response_model=CarRead)
def get_car_by_id(
        car_id: int,
        db: Session = Depends(get_db)
):
    return GetCarUseCase(db).execute(car_id)


@router.get("/filter", response_model=List[CarRead])
def filter_cars(
    filters: CarFilter,
    db: Session = Depends(get_db)
):
    return FilterCarUseCase(db).execute(filters)


@router.post("/", response_model=CarRead, status_code=status.HTTP_201_CREATED)
def add_car(
    car_data: CarCreate,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can create cars")

    return CreateCarUseCase(db).execute(car_data)


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(
    car_id: int,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can delete cars")

    DeleteCarUseCase(db).execute(car_id)
    return {"detail": "Car deleted successfully"}


@router.put("/{car_id}", response_model=CarRead)
def update_car(
    car_data: CarUpdate,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can update cars")

    return UpdateCarUseCase(db).execute(car_data)