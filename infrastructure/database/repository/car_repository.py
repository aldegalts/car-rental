from sqlalchemy.orm import Session


class CarRepository:
    def __init__(self, session: Session):
        self.session = session