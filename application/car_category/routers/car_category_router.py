from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.car_category.schemas import CarCategoryRead, CarCategoryCreate, CarCategoryUpdate
from application.car_category.usecases import CreateCarCategoryUseCase, DeleteCarCategoryUseCase, \
    GetAllCarCategoriesUseCase, UpdateCarCategoryUseCase
from application.dependencies import get_current_user
from infrastructure.database.database_session import get_db

router = APIRouter(prefix="/car_categories", tags=["Car Categories"])


@router.post("/", response_model=CarCategoryRead, status_code=status.HTTP_201_CREATED)
def add_category(
    category_data: CarCategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can create car categories")

    return CreateCarCategoryUseCase(db).execute(category_data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can delete car categories")

    DeleteCarCategoryUseCase(db).execute(category_id)
    return {"detail": "Car category deleted successfully"}


@router.get("/", response_model=List[CarCategoryRead])
def get_all_categories(db: Session = Depends(get_db)):
    return GetAllCarCategoriesUseCase(db).execute()


@router.put("/{category_id}", response_model=CarCategoryRead)
def add_category(
    category_data: CarCategoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can update car categories")

    return UpdateCarCategoryUseCase(db).execute(category_data)