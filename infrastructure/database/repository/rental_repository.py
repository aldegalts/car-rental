from sqlalchemy.orm import Session


class RentalRepository:
    def __init__(self, session: Session):
        self.session = session