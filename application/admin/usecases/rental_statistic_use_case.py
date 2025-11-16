from datetime import datetime

from sqlalchemy.orm import Session

from infrastructure.database.repository import RentalRepository


class RentalStatisticUseCase:

    def __init__(self, db: Session):
        self.db = db
        self.rental_repo = RentalRepository(db)

    def execute(self, start_date: datetime, end_date: datetime):
        rentals, p_with, p_without = self.rental_repo.statistic_get_rentals(start_date, end_date)

        return {
            "total_rentals": len(rentals),
            "rentals": rentals,
            "percent_with_violations": round(p_with, 2),
            "percent_without_violations": round(p_without, 2),
        }
