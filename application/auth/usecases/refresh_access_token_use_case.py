from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from application.auth.utils.jwt import create_access_token, decode_token, is_refresh_token
from application.auth.schemas.token_schema import AccessTokenResponse, RefreshRequest

from infrastructure.database.repository import UserRepository


class RefreshAccessTokenUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def refresh_access_token(self, request: RefreshRequest) -> AccessTokenResponse:
        payload = decode_token(request.refresh_token)
        if not payload or not is_refresh_token(payload):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный или истекший токен обновления",
            )

        user_id = payload.get("sub")
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден")

        new_access_token = create_access_token(
            {"sub": str(user.id), "role": user.role.role_name}
        )
        return AccessTokenResponse(access_token=new_access_token)
