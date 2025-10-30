from sqlalchemy.orm import Session


class CarStatusRepository:
    def __init__(self, session: Session):
        self.session = session