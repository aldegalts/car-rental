from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.dependencies import get_current_user
from application.rental_status.schemas import RentalStatusRead, RentalStatusCreate, RentalStatusUpdate
from application.rental_status.usecases import CreateRentalStatusUseCase, DeleteRentalStatusUseCase, \
    GetAllRentalStatusesUseCase, UpdateRentalStatusUseCase
from infrastructure.database.database_session import get_db

router = APIRouter(prefix="/rental_statuses", tags=["Rental Statuses"])


@router.post("/", response_model=RentalStatusRead, status_code=status.HTTP_201_CREATED)
def add_status(
    status_data: RentalStatusCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can create rental statuses")

    return CreateRentalStatusUseCase(db).execute(status_data)


@router.delete("/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_status(
    status_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can delete rental statuses")

    DeleteRentalStatusUseCase(db).execute(status_id)
    return {"detail": "Rental status deleted successfully"}


@router.get("/", response_model=List[RentalStatusRead])
def get_all_statuses(db: Session = Depends(get_db)):
    return GetAllRentalStatusesUseCase(db).execute()



@router.put("/{status_id}", response_model=RentalStatusRead)
def update_status(
    status_data: RentalStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can update rental statuses")

    return UpdateRentalStatusUseCase(db).execute(status_data)