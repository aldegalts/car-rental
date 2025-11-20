from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from application.frontend.templates import templates
from application.frontend.utils import get_current_user_async
from infrastructure.database.database_session import get_db
import httpx

router = APIRouter(tags=["Frontend Rentals"], include_in_schema=False)

BASE_URL = "http://localhost:8000"


@router.get("/account/rentals", response_class=HTMLResponse)
async def my_rentals(request: Request, db: Session = Depends(get_db)):
    """Страница моих аренд"""
    current_user = await get_current_user_async(request, db)
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    if current_user.role.role_name != "user":
        return RedirectResponse(url="/admin/rentals", status_code=302)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.get(f"{BASE_URL}/rentals/my")
        
        if response.status_code == 200:
            rentals = response.json()
        else:
            rentals = []
        
        # Получаем статусы аренд
        status_resp = await client.get(f"{BASE_URL}/rental_statuses/")
        statuses = {s["id"]: s for s in status_resp.json()} if status_resp.status_code == 200 else {}
        
        # Получаем машины
        cars_resp = await client.get(f"{BASE_URL}/cars/")
        cars = {c["id"]: c for c in cars_resp.json()} if cars_resp.status_code == 200 else {}
        
        for rental in rentals:
            rental["status"] = statuses.get(rental.get("rental_status_id"), {})
            rental["car"] = cars.get(rental.get("car_id"), {})
    
    return templates.TemplateResponse(
        "rentals/my.html",
        {
            "request": request,
            "current_user": current_user,
            "rentals": rentals
        }
    )


@router.get("/account/rentals/{rental_id}", response_class=HTMLResponse)
async def rental_detail(
    request: Request,
    rental_id: int,
    db: Session = Depends(get_db)
):
    """Страница детальной информации об аренде"""
    current_user = await get_current_user_async(request, db)
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.get(f"{BASE_URL}/rentals/{rental_id}")
        
        if response.status_code != 200:
            return RedirectResponse(
                url="/account/rentals" if current_user.role.role_name == "user" else "/admin/rentals",
                status_code=302
            )
        
        rental = response.json()
        
        # Получаем дополнительные данные
        status_resp = await client.get(f"{BASE_URL}/rental_statuses/")
        statuses = {s["id"]: s for s in status_resp.json()} if status_resp.status_code == 200 else {}
        
        car_resp = await client.get(f"{BASE_URL}/cars/{rental.get('car_id')}")
        car = car_resp.json() if car_resp.status_code == 200 else {}
        
        rental["status"] = statuses.get(rental.get("rental_status_id"), {})
        rental["car"] = car
    
    return templates.TemplateResponse(
        "rentals/detail.html",
        {
            "request": request,
            "current_user": current_user,
            "rental": rental
        }
    )


@router.get("/rentals/create/{car_id}", response_class=HTMLResponse)
async def create_rental_page(
    request: Request,
    car_id: int,
    db: Session = Depends(get_db)
):
    """Страница создания аренды"""
    current_user = await get_current_user_async(request, db)
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    cookies = dict(request.cookies)
    
    # Проверяем наличие данных клиента
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        client_resp = await client.get(f"{BASE_URL}/clients/profile")
        if client_resp.status_code != 200:
            return RedirectResponse(url="/profile/fill", status_code=302)
        
        client_data = client_resp.json()
        
        # Получаем данные машины
        car_resp = await client.get(f"{BASE_URL}/cars/{car_id}")
        if car_resp.status_code != 200:
            return RedirectResponse(url="/catalog", status_code=302)
        
        car = car_resp.json()

    start_date_value = datetime.now().strftime("%Y-%m-%dT%H:%M")
    
    return templates.TemplateResponse(
        "rentals/create.html",
        {
            "request": request,
            "current_user": current_user,
            "car": car,
            "client": client_data,
            "start_date_value": start_date_value
        }
    )


@router.post("/rentals/create", response_class=HTMLResponse)
async def create_rental_submit(
    request: Request,
    car_id: int = Form(...),
    end_date: str = Form(...),
    db: Session = Depends(get_db)
):
    """Обработка формы создания аренды"""
    current_user = await get_current_user_async(request, db)
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    cookies = dict(request.cookies)
    
    # Получаем данные клиента
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        client_resp = await client.get(f"{BASE_URL}/clients/profile")
        if client_resp.status_code != 200:
            return RedirectResponse(url="/profile/fill", status_code=302)
        
        client_data = client_resp.json()
        
        # Получаем данные машины для расчета стоимости
        car_resp = await client.get(f"{BASE_URL}/cars/{car_id}")
        if car_resp.status_code != 200:
            return RedirectResponse(url="/catalog", status_code=302)
        
        car = car_resp.json()
        
        # Рассчитываем количество дней и общую стоимость
        start = datetime.now()
        end = datetime.fromisoformat(end_date.replace("T", " "))

        if end < start:
            error = "Дата окончания не может быть раньше сегодняшнего дня"
            start_date_value = start.strftime("%Y-%m-%dT%H:%M")
            return templates.TemplateResponse(
                "rentals/create.html",
                {
                    "request": request,
                    "current_user": current_user,
                    "car": car,
                    "client": client_data,
                    "error": error,
                    "start_date_value": start_date_value
                }
            )

        start = start.replace(second=0, microsecond=0)
        days = (end - start).days + 1
        total_amount = float(car["daily_cost"]) * days
        
        rental_data = {
            "client_id": client_data["id"],
            "car_id": car_id,
            "start_date": start.isoformat(),
            "end_date": end_date,
            "total_amount": str(total_amount),
            "rental_status_id": None
        }
        
        response = await client.post(f"{BASE_URL}/rentals/", json=rental_data)
        
        if response.status_code == 201:
            rental = response.json()
            return RedirectResponse(url=f"/account/rentals/{rental['id']}", status_code=302)
        else:
            error = response.json().get("detail", "Ошибка при создании аренды")
            start_date_value = start.strftime("%Y-%m-%dT%H:%M")
            return templates.TemplateResponse(
                "rentals/create.html",
                {
                    "request": request,
                    "current_user": current_user,
                    "car": car,
                    "client": client_data,
                    "error": error,
                    "start_date_value": start_date_value
                }
            )

