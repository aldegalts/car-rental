from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

from application.frontend.templates import templates
from application.frontend.utils import get_current_user_async
from infrastructure.database.database_session import get_db
from infrastructure.database.models import UserEntity

# Импорты для API вызовов
import httpx

router = APIRouter(tags=["Frontend"])

BASE_URL = "http://localhost:8000"


async def make_api_request(method: str, url: str, data: dict = None, cookies: dict = None):
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        if method == "GET":
            response = await client.get(url, params=data)
        elif method == "POST":
            response = await client.post(url, json=data)
        elif method == "PUT":
            response = await client.put(url, json=data)
        elif method == "DELETE":
            response = await client.delete(url)
        return response


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return RedirectResponse(url="/catalog", status_code=302)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user_async(request, db)
    if current_user:
        if current_user.role.role_name == "admin":
            return RedirectResponse(url="/admin/dashboard", status_code=302)
        else:
            return RedirectResponse(url="/profile", status_code=302)
    
    return templates.TemplateResponse("login.html", {"request": request, "current_user": None})


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    from fastapi import Response as FastAPIResponse
    from application.auth.schemas import UserLogin
    from application.auth.usecases import LoginUserUseCase
    import os
    
    try:
        login_data = UserLogin(username=username, password=password)
        login_use_case = LoginUserUseCase(db)

        temp_response = FastAPIResponse()
        user_data = login_use_case.login_user(login_data, temp_response)

        redirect_response = RedirectResponse(
            url="/profile" if user_data.role == "user" else "/admin/dashboard",
            status_code=302
        )

        ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
        REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

        if hasattr(temp_response, 'headers'):
            set_cookie_values = temp_response.headers.getlist("set-cookie")
            for cookie_str in set_cookie_values:
                cookie_parts = cookie_str.split(";")
                name_value = cookie_parts[0].split("=", 1)
                if len(name_value) == 2:
                    cookie_name = name_value[0].strip()
                    cookie_value = name_value[1].strip()
                    
                    if cookie_name == "access_token":
                        max_age = ACCESS_TOKEN_EXPIRE_MINUTES * 60
                    elif cookie_name == "refresh_token":
                        max_age = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
                    else:
                        max_age = None
                    
                    redirect_response.set_cookie(
                        key=cookie_name,
                        value=cookie_value,
                        httponly=True,
                        max_age=max_age,
                        path="/"
                    )
        

        if not hasattr(temp_response, 'headers') or not temp_response.headers.getlist("set-cookie"):
            from application.auth.utils.jwt import create_access_token, create_refresh_token
            from datetime import timedelta
            from infrastructure.database.repository import RefreshTokenRepository
            
            payload = {"sub": str(user_data.id), "role": user_data.role}
            access_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(payload, access_expires)
            refresh_token_value, expires_at = create_refresh_token(payload)
            
            from infrastructure.database.models import RefreshTokenEntity
            refresh_token_repo = RefreshTokenRepository(db)
            refresh_token_entity = RefreshTokenEntity(
                user_id=user_data.id,
                token=refresh_token_value,
                expires_at=expires_at
            )
            refresh_token_repo.add(refresh_token_entity)
            
            redirect_response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                path="/"
            )
            redirect_response.set_cookie(
                key="refresh_token",
                value=refresh_token_value,
                httponly=True,
                max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
                path="/"
            )
        
        return redirect_response
    except HTTPException as e:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "current_user": None, "error": e.detail}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "current_user": None, "error": f"Ошибка: {str(e)}"}
        )


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user_async(request, db)
    if current_user:
        return RedirectResponse(url="/profile", status_code=302)
    
    return templates.TemplateResponse("register.html", {"request": request, "current_user": None})


@router.post("/register", response_class=HTMLResponse)
async def register_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    try:
        async with httpx.AsyncClient(follow_redirects=False) as client:
            response = await client.post(
                f"{BASE_URL}/auth/register",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 201:
                return RedirectResponse(url="/login", status_code=302)
            else:
                error = response.json().get("detail", "Ошибка регистрации")
                return templates.TemplateResponse(
                    "register.html",
                    {"request": request, "current_user": None, "error": error}
                )
    except Exception as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "current_user": None, "error": f"Ошибка: {str(e)}"}
        )


@router.post("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    cookies = dict(request.cookies)
    try:
        async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
            await client.post(f"{BASE_URL}/auth/logout")
    except:
        pass
    
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


@router.get("/about", response_class=HTMLResponse)
async def about_page(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user_async(request, db)
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "current_user": current_user,
            "developer": {
                "name": "Дегальцева Алина Евгеньевна",
                "university": "Воронежского государственного университета",
                "faculty": "Факультет компьютерных наук",
                "course": "3 курс",
                "group": "4 группа"
            }
        }
    )

