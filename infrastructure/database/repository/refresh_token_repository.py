from sqlalchemy.orm import Session

from infrastructure.database.models import RefreshTokenEntity


class RefreshTokenRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, token: RefreshTokenEntity):
        self.session.add(token)
        self.session.commit()