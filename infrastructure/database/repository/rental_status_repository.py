from sqlalchemy.orm import Session


class RentalStatusRepository:
    def __init__(self, session: Session):
        self.session = session