from sqlalchemy.orm import Session


class CarCategoryRepository:
    def __init__(self, session: Session):
        self.session = session