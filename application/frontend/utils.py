from fastapi import Request
from sqlalchemy.orm import Session
from application.auth.utils.jwt import decode_token
from infrastructure.database.repository import UserRepository
from infrastructure.database.database_session import get_db


async def get_current_user_async(request: Request, db: Session = None):
    """Асинхронная версия get_current_user для фронтенда"""
    if db is None:
        from infrastructure.database.database_session import get_db
        db = next(get_db())
    
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

