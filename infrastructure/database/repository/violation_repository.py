from sqlalchemy.orm import Session


class ViolationRepository:
    def __init__(self, session: Session):
        self.session = session