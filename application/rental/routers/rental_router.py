from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.dependencies import get_current_user
from application.client.usecases.get_client_by_user_id_use_case import GetClientByUserIdUseCase
from application.rental.schemas import RentalRead, RentalCreate, RentalUpdate, RentalFilter
from application.rental.usecases import CreateRentalUseCase, DeleteRentalUseCase, GetAllUserRentalsUseCase, \
    UpdateRentalUseCase, GetUserRentalByIdUseCase, GetAllRentalsUseCase, GetRentalByIdUseCase
from infrastructure.database.database_session import get_db
from infrastructure.database.models import UserEntity

router = APIRouter(prefix="/rentals", tags=["Rentals"])


@router.get("/", response_model=List[RentalRead])
def get_all_rentals(
        car_id: Optional[int] = None,
        client_id: Optional[int] = None,
        current_user: UserEntity = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can view all rentals")

    filters = RentalFilter(
        car_id=car_id,
        client_id=client_id
    )
    return GetAllRentalsUseCase(db).execute(filters)


@router.get("/my", response_model=List[RentalRead])
def get_all_user_rentals(
        current_user: UserEntity = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return GetAllUserRentalsUseCase(db).execute(current_user.id)


@router.get("/{rental_id}", response_model=RentalRead)
def get_user_rental_by_id(
        rental_id: int,
        current_user: UserEntity = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if current_user.role.role_name == "admin":
        return GetRentalByIdUseCase(db).execute(rental_id)
    elif current_user.role.role_name == "user":
        return GetUserRentalByIdUseCase(db).execute(current_user.id, rental_id)


@router.post("/", response_model=RentalRead, status_code=status.HTTP_201_CREATED)
def add_rental(
    rental_data: RentalCreate,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        GetClientByUserIdUseCase(db).execute(current_user.id)
    except HTTPException as exc:
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Only authorized user with client data can rental cars")
        raise

    if current_user.role.role_name != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only authorized user with client data can rental cars")

    return CreateRentalUseCase(db).execute(rental_data)


@router.delete("/{rental_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rental(
    rental_id: int,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can delete rentals")

    DeleteRentalUseCase(db).execute(rental_id)
    return {"detail": "Rental deleted successfully"}


@router.put("/{rental_id}", response_model=RentalRead)
def update_rental(
    rental_data: RentalUpdate,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can update rentals")

    return UpdateRentalUseCase(db).execute(rental_data)