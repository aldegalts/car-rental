import os
from datetime import timedelta

from fastapi import APIRouter, Form, Depends, status, HTTPException
from sqlalchemy.orm import Session

from application.auth.schemas import TokenPairResponse
from application.auth.utils.jwt import create_access_token, create_refresh_token
from application.auth.utils.security import verify_password
from infrastructure.database.database_session import get_db
from infrastructure.database.repository import UserRepository

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

router = APIRouter(prefix="/token", tags=["Auth Swagger"])

@router.post("", response_model=TokenPairResponse)
def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = UserRepository(db).get_by_username(username)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user.id), "role": user.role.role_name}
    access_token = create_access_token(payload, access_expires)
    refresh_token = create_refresh_token(payload)

    return TokenPairResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )