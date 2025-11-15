from fastapi import APIRouter, Depends, status, Response, Cookie
from sqlalchemy.orm import Session
from infrastructure.database.database_session import get_db
from application.auth.schemas import UserCreate, UserLogin, UserResponse, RefreshRequest, AccessTokenResponse
from application.auth.usecases import RegisterUserUseCase, LoginUserUseCase, RefreshAccessTokenUseCase, LogoutUseCase
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/auth", tags=["Auth"])
templates = Jinja2Templates(directory="templates")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return RegisterUserUseCase(db).register_user(user_data)


@router.post("/login")
def login_user(login_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    return LoginUserUseCase(db).login_user(login_data, response)


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh_access_token(request: RefreshRequest, db: Session = Depends(get_db)):
    return RefreshAccessTokenUseCase(db).refresh_access_token(request)


@router.post("/logout")
def logout(
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: str = Cookie(default=None)
):
    return LogoutUseCase(db).execute(refresh_token, response)