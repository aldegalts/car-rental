from sqlalchemy.orm import Session


class ClientRepository:
    def __init__(self, session: Session):
        self.session = session