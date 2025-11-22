from datetime import timedelta
from fastapi import HTTPException, status, Response
from sqlalchemy.orm import Session

from application.auth.schemas import UserLogin, UserResponse
from application.auth.utils.security import verify_password
from application.auth.utils.jwt import create_access_token, create_refresh_token

import os

from infrastructure.database.models import RefreshTokenEntity
from infrastructure.database.repository import UserRepository, RefreshTokenRepository

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

class LoginUserUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.refresh_token_repo = RefreshTokenRepository(db)

    def login_user(self, login_data: UserLogin, response: Response) -> UserResponse:
        user = self.user_repository.get_by_username(login_data.username)
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неправильное имя пользователя или пароль",
            )

        access_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": str(user.id), "role": user.role.role_name}

        access_token = create_access_token(payload, access_expires)
        refresh_token_value, expires_at = create_refresh_token(payload)

        refresh_token_entity = RefreshTokenEntity(
            user_id=user.id,
            token=refresh_token_value,
            expires_at=expires_at
        )
        self.refresh_token_repo.add(refresh_token_entity)

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/"
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token_value,
            httponly=True,
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            path="/"
        )

        return UserResponse(
            id = user.id,
            username = user.username,
            role = user.role.role_name,
        )