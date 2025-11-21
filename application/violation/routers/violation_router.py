from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.dependencies import get_current_user
from application.violation.schemas import ViolationRead, ViolationCreate, ViolationUpdate
from application.violation.usecases import CreateViolationUseCase, DeleteViolationUseCase, GetAllUserViolationsUseCase, \
    UpdateViolationUseCase, GetViolationByIdUseCase, GetUserViolationByIdUseCase
from infrastructure.database.database_session import get_db
from infrastructure.database.models import UserEntity

router = APIRouter(prefix="/violations", tags=["Violations"])


@router.get("/", response_model=List[ViolationRead])
def get_all_violations(
        current_user: UserEntity = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return GetAllUserViolationsUseCase(db).execute(current_user.id)


@router.get("/{violation_id}", response_model=ViolationRead)
def get_violation_by_id(
        violation_id: int,
        current_user: UserEntity = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if current_user.role.role_name == "admin":
        return GetViolationByIdUseCase(db).execute(violation_id)
    elif current_user.role.role_name == "user":
        return GetUserViolationByIdUseCase(db).execute(current_user.id, violation_id)


@router.post("/", response_model=ViolationRead, status_code=status.HTTP_201_CREATED)
def add_violation(
    violation_data: ViolationCreate,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только администратор может добавлять нарушения")

    return CreateViolationUseCase(db).execute(violation_data)


@router.delete("/{violation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_violation(
    violation_id: int,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только администратор может удалять нарушения")

    DeleteViolationUseCase(db).execute(violation_id)
    return {"detail": "Violation deleted successfully"}


@router.put("/{violation_id}", response_model=ViolationRead)
def update_violation(
    violation_data: ViolationUpdate,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только администратор может изменять нарушения")

    return UpdateViolationUseCase(db).execute(violation_data)