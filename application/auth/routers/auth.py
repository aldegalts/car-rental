from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from infrastructure.database.database_session import get_db
from application.auth.schemas import UserCreate, UserLogin, UserResponse, RefreshRequest, AccessTokenResponse
from application.auth.usecases import RegisterUserUseCase, LoginUserUseCase, RefreshAccessTokenUseCase

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return RegisterUserUseCase(db).register_user(user_data)


@router.post("/login")
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    return LoginUserUseCase(db).login_user(login_data)


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh_access_token(request: RefreshRequest, db: Session = Depends(get_db)):
    return RefreshAccessTokenUseCase(db).refresh_access_token(request)
