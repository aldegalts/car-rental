from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from application.dependencies import get_current_user
from application.rental.schemas import RentalRead, RentalCreate, RentalUpdate
from application.rental.usecases import CreateRentalUseCase, DeleteRentalUseCase, GetAllRentalUseCase, \
    UpdateRentalUseCase
from infrastructure.database.database_session import get_db

router = APIRouter(prefix="/rentals", tags=["Rentals"])


@router.post("/", response_model=RentalRead, status_code=status.HTTP_201_CREATED)
def add_rental(
    rental_data: RentalCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)

    return CreateRentalUseCase(db).execute(rental_data)


@router.delete("/{rental_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rental(
    rental_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can delete rentals")

    DeleteRentalUseCase(db).execute(rental_id)
    return {"detail": "Rental deleted successfully"}


@router.get("/", response_model=List[RentalRead])
def get_all_rentals(db: Session = Depends(get_db)):
    return GetAllRentalUseCase(db).execute()


@router.put("/{rental_id}", response_model=RentalRead)
def update_rental(
    rental_data: RentalUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can update rentals")

    return UpdateRentalUseCase(db).execute(rental_data)