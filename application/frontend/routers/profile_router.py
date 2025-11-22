from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import date

from application.frontend.templates import templates
from application.frontend.utils import get_current_user_async
from infrastructure.database.database_session import get_db
import httpx

router = APIRouter(tags=["Frontend Profile"])

BASE_URL = "http://localhost:8000"


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user_async(request, db)
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    if current_user.role.role_name != "user":
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.get(f"{BASE_URL}/clients/profile")
        
        if response.status_code == 200:
            client_data = response.json()
        elif response.status_code == 404:
            return RedirectResponse(url="/profile/fill", status_code=302)
        else:
            client_data = None
    
    return templates.TemplateResponse(
        "profile/view.html",
        {
            "request": request,
            "current_user": current_user,
            "client": client_data
        }
    )


@router.get("/profile/fill", response_class=HTMLResponse)
async def fill_profile_page(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user_async(request, db)
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    if current_user.role.role_name != "user":
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    
    return templates.TemplateResponse(
        "profile/fill.html",
        {
            "request": request,
            "current_user": current_user
        }
    )


@router.post("/profile/fill", response_class=HTMLResponse)
async def fill_profile_submit(
    request: Request,
    name: str = Form(...),
    surname: str = Form(...),
    birth_date: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    driver_license: str = Form(...),
    license_expiry_date: str = Form(...),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user_async(request, db)
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    cookies = dict(request.cookies)
    
    client_data = {
        "name": name,
        "surname": surname,
        "birth_date": birth_date,
        "phone": phone,
        "email": email,
        "driver_license": driver_license,
        "license_expiry_date": license_expiry_date,
        "user_id": current_user.id
    }
    
    try:
        async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
            response = await client.post(f"{BASE_URL}/clients/", json=client_data)
            
            if response.status_code == 201:
                return RedirectResponse(url="/profile", status_code=302)
            else:
                error = response.json().get("detail", "Ошибка при сохранении данных")
                return templates.TemplateResponse(
                    "profile/fill.html",
                    {
                        "request": request,
                        "current_user": current_user,
                        "error": error
                    }
                )
    except Exception as e:
        return templates.TemplateResponse(
            "profile/fill.html",
            {
                "request": request,
                "current_user": current_user,
                "error": f"Ошибка: {str(e)}"
            }
        )

