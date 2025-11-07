from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.car_status.schemas import CarStatusRead, CarStatusCreate, CarStatusUpdate
from application.car_status.usecases import CreateCarStatusUseCase, DeleteCarStatusUseCase, GetAllCarStatusesUseCase, \
    UpdateCarStatusUseCase
from application.dependencies import get_current_user
from infrastructure.database.database_session import get_db

router = APIRouter(prefix="/car_statuses", tags=["Car Statuses"])


@router.post("/", response_model=CarStatusRead, status_code=status.HTTP_201_CREATED)
def add_status(
    status_data: CarStatusCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can create car statuses")

    return CreateCarStatusUseCase(db).execute(status_data)


@router.delete("/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_status(
    status_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can delete car statuses")

    DeleteCarStatusUseCase(db).execute(status_id)
    return {"detail": "Car status deleted successfully"}


@router.get("/", response_model=List[CarStatusRead])
def get_all_statuses(db: Session = Depends(get_db)):
    return GetAllCarStatusesUseCase(db).execute()



@router.put("/{status_id}", response_model=CarStatusRead)
def add_status(
    status_data: CarStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can update car statuses")

    return UpdateCarStatusUseCase(db).execute(status_data)