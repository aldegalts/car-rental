from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.car_status.schemas import CarStatusRead, CarStatusCreate, CarStatusUpdate
from application.car_status.usecases import CreateCarStatusUseCase, DeleteCarStatusUseCase, GetAllCarStatusesUseCase, \
    UpdateCarStatusUseCase
from application.dependencies import get_current_user
from infrastructure.database.database_session import get_db
from infrastructure.database.models import UserEntity

router = APIRouter(prefix="/car_statuses", tags=["Car Statuses"])


@router.get("/", response_model=List[CarStatusRead])
def get_all_statuses(
        db: Session = Depends(get_db)
):
    return GetAllCarStatusesUseCase(db).execute()


@router.post("/", response_model=CarStatusRead, status_code=status.HTTP_201_CREATED)
def add_status(
    status_data: CarStatusCreate,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только администратор может добавлять статус машин")

    return CreateCarStatusUseCase(db).execute(status_data)


@router.delete("/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_status(
    status_id: int,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только администратор может удалять статус машин")

    DeleteCarStatusUseCase(db).execute(status_id)
    return {"detail": "Car status deleted successfully"}


@router.put("/{status_id}", response_model=CarStatusRead)
def update_status(
    status_data: CarStatusUpdate,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только администратор может изменять статус машин")

    return UpdateCarStatusUseCase(db).execute(status_data)