from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.dependencies import get_current_user
from application.violation.schemas import ViolationRead, ViolationCreate, ViolationUpdate
from application.violation.usecases import CreateViolationUseCase, DeleteViolationUseCase, GetAllUserViolationsUseCase, \
    UpdateViolationUseCase
from infrastructure.database.database_session import get_db

router = APIRouter(prefix="/violations", tags=["Violations"])


@router.post("/", response_model=ViolationRead, status_code=status.HTTP_201_CREATED)
def add_violation(
    violation_data: ViolationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can create violations")

    return CreateViolationUseCase(db).execute(violation_data)


@router.delete("/{violation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_violation(
    violation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can delete violations")

    DeleteViolationUseCase(db).execute(violation_id)
    return {"detail": "Violation deleted successfully"}


@router.get("/", response_model=List[ViolationRead])
def get_all_violations(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return GetAllUserViolationsUseCase(db).execute(current_user.id)


@router.put("/{violation_id}", response_model=ViolationRead)
def update_violation(
    violation_data: ViolationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can update violations")

    return UpdateViolationUseCase(db).execute(violation_data)