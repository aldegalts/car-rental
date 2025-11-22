from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.dependencies import get_current_user
from application.violation_type.schemas import ViolationTypeRead, ViolationTypeCreate, ViolationTypeUpdate
from application.violation_type.usecases import CreateViolationTypeUseCase, DeleteViolationTypeUseCase, \
    GetAllViolationTypesUseCase, UpdateViolationTypeUseCase, GetViolationTypeByIdUseCase
from infrastructure.database.database_session import get_db
from infrastructure.database.models import UserEntity

router = APIRouter(prefix="/violation_types", tags=["Violation Types"])


@router.get("/", response_model=List[ViolationTypeRead])
def get_all_violation_types(
        db: Session = Depends(get_db)
):
    return GetAllViolationTypesUseCase(db).execute()


@router.get("/{violation_type_id}", response_model=ViolationTypeRead)
def get_violation_type_by_id(
        violation_type_id: int,
        db: Session = Depends(get_db)
):
    return GetViolationTypeByIdUseCase(db).execute(violation_type_id)


@router.post("/", response_model=ViolationTypeRead, status_code=status.HTTP_201_CREATED)
def add_violation_type(
    type_data: ViolationTypeCreate,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только администратор может добавлять типы нарушений")

    return CreateViolationTypeUseCase(db).execute(type_data)


@router.delete("/{violation_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_violation_type(
    violation_type_id: int,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только администратор может удалять нарушения")

    DeleteViolationTypeUseCase(db).execute(violation_type_id)
    return {"detail": "Violation type deleted successfully"}


@router.put("/{violation_type_id}", response_model=ViolationTypeRead)
def update_violation_type(
    violation_type_id: int,
    type_data: ViolationTypeUpdate,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только администратор может изменять нарушения")

    if type_data.id != violation_type_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID типа нарушения в пути и теле запроса не совпадают")

    return UpdateViolationTypeUseCase(db).execute(type_data)