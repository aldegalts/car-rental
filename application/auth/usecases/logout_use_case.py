from fastapi import Response
from sqlalchemy.orm import Session

from infrastructure.database.repository import RefreshTokenRepository


class LogoutUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.refresh_token_repo = RefreshTokenRepository(db)

    def execute(self, refresh_token: str, response: Response):
        if refresh_token:
            self.refresh_token_repo.delete(refresh_token)

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return {"message": "Logged out successfully"}