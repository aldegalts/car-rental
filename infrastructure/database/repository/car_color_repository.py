from sqlalchemy.orm import Session


class CarColorRepository:
    def __init__(self, session: Session):
        self.session = session