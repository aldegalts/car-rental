from fastapi import Depends, Request
from sqlalchemy.orm import Session

from application.auth.utils.jwt import decode_token
from infrastructure.database.repository import UserRepository
from infrastructure.database.database_session import get_db

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if not token:
        return None

    payload = decode_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = UserRepository(db).get_by_id(user_id)
    if not user:
        return None

    return user
