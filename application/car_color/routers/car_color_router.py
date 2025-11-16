from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.car_color.schemas import CarColorRead, CarColorCreate, CarColorUpdate
from application.car_color.usecases import CreateCarColorUseCase, DeleteCarColorUseCase, GetAllCarColorsUseCase, \
    UpdateCarColorUseCase
from application.dependencies import get_current_user
from infrastructure.database.database_session import get_db
from infrastructure.database.models import UserEntity

router = APIRouter(prefix="/car_colors", tags=["Car Colors"])


@router.get("/", response_model=List[CarColorRead])
def get_all_colors(
        db: Session = Depends(get_db)
):
    return GetAllCarColorsUseCase(db).execute()


@router.post("/", response_model=CarColorRead, status_code=status.HTTP_201_CREATED)
def add_color(
    color_data: CarColorCreate,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can create car colors")

    return CreateCarColorUseCase(db).execute(color_data)


@router.delete("/{color_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_color(
    color_id: int,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can delete car colors")

    DeleteCarColorUseCase(db).execute(color_id)
    return {"detail": "Color deleted successfully"}


@router.put("/{color_id}", response_model=CarColorRead)
def update_color(
    color_data: CarColorUpdate,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can update car colors")

    return UpdateCarColorUseCase(db).execute(color_data)