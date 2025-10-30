from sqlalchemy.orm import Session


class ViolationTypeRepository:
    def __init__(self, session: Session):
        self.session = session