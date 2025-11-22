from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime

from sqlalchemy.orm import Session

from application.admin.usecases import RentalStatisticUseCase
from application.dependencies import get_current_user
from infrastructure.database.database_session import get_db
from infrastructure.database.models import UserEntity

router = APIRouter(tags=["Admin Statistic"])


@router.get("/admin/rental-statistic")
def get_rental_stats(
    start_date: str = Query(..., description="Дата начала в формате ISO (YYYY-MM-DDTHH:mm:ss)"),
    end_date: str = Query(..., description="Дата окончания в формате ISO (YYYY-MM-DDTHH:mm:ss)"),
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор может просматривать статистику"
        )

    try:
        if len(start_date) == 16:
            start_date = start_date + ":00"
        if len(end_date) == 16:
            end_date = end_date + ":00"
        
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неправильный формат даты: {str(e)}"
        )

    return RentalStatisticUseCase(db).execute(start_dt, end_dt)
