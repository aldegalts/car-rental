from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from sqlalchemy.orm import Session

from application.admin.usecases import RentalStatisticUseCase
from application.dependencies import get_current_user
from infrastructure.database.database_session import get_db
from infrastructure.database.models import UserEntity

router = APIRouter(tags=["Admin Statistic"])


@router.get("/admin/rental-statistic")
def get_rental_stats(
    start_date: datetime,
    end_date: datetime,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role.role_name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can view rental statistics"
        )

    return RentalStatisticUseCase(db).execute(start_date, end_date)
