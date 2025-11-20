from fastapi import APIRouter, Depends, Request, Form, Query, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from decimal import Decimal

from application.frontend.templates import templates
from application.frontend.utils import get_current_user_async
from infrastructure.database.database_session import get_db
import httpx

router = APIRouter(tags=["Frontend Admin"])

BASE_URL = "http://localhost:8000"


def check_admin(current_user):
    """Проверка прав администратора"""
    if not current_user or current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещен")


@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """Главная страница администратора"""
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        # Получаем статистику
        stats_resp = await client.get(f"{BASE_URL}/cars/")
        cars_count = len(stats_resp.json()) if stats_resp.status_code == 200 else 0
        
        clients_resp = await client.get(f"{BASE_URL}/clients/")
        clients_count = len(clients_resp.json()) if clients_resp.status_code == 200 else 0
        
        # Для получения всех аренд не передаем параметры - FastAPI создаст пустой RentalFilter
        rentals_resp = await client.get(f"{BASE_URL}/rentals/")
        rentals_count = len(rentals_resp.json()) if rentals_resp.status_code == 200 else 0
    
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "stats": {
                "cars": cars_count,
                "clients": clients_count,
                "rentals": rentals_count
            }
        }
    )


# ========== КЛИЕНТЫ ==========
@router.get("/admin/clients", response_class=HTMLResponse)
async def admin_clients(request: Request, db: Session = Depends(get_db)):
    """Список клиентов"""
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.get(f"{BASE_URL}/clients/")
        clients = response.json() if response.status_code == 200 else []
    
    return templates.TemplateResponse(
        "admin/clients/list.html",
        {
            "request": request,
            "current_user": current_user,
            "clients": clients
        }
    )


@router.get("/admin/clients/{client_id}", response_class=HTMLResponse)
async def admin_client_detail(
    request: Request,
    client_id: int,
    db: Session = Depends(get_db)
):
    """Детали клиента"""
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.get(f"{BASE_URL}/clients/{client_id}")
        if response.status_code != 200:
            return RedirectResponse(url="/admin/clients", status_code=302)
        
        client_data = response.json()
    
    return templates.TemplateResponse(
        "admin/clients/detail.html",
        {
            "request": request,
            "current_user": current_user,
            "client": client_data
        }
    )


@router.get("/admin/clients/{client_id}/edit", response_class=HTMLResponse)
async def admin_client_edit_page(
    request: Request,
    client_id: int,
    db: Session = Depends(get_db)
):
    """Страница редактирования клиента"""
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.get(f"{BASE_URL}/clients/{client_id}")
        if response.status_code != 200:
            return RedirectResponse(url="/admin/clients", status_code=302)
        
        client_data = response.json()
    
    return templates.TemplateResponse(
        "admin/clients/edit.html",
        {
            "request": request,
            "current_user": current_user,
            "client": client_data
        }
    )


@router.post("/admin/clients/{client_id}/edit", response_class=HTMLResponse)
async def admin_client_edit_submit(
    request: Request,
    client_id: int,
    name: str = Form(...),
    surname: str = Form(...),
    birth_date: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    driver_license: str = Form(...),
    license_expiry_date: str = Form(...),
    db: Session = Depends(get_db)
):
    """Обработка формы редактирования клиента"""
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    
    client_data = {
        "id": client_id,
        "name": name,
        "surname": surname,
        "birth_date": birth_date,
        "phone": phone,
        "email": email,
        "driver_license": driver_license,
        "license_expiry_date": license_expiry_date,
        "user_id": client_id  # Нужно получить из существующего клиента
    }
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        # Сначала получаем существующего клиента для user_id
        get_resp = await client.get(f"{BASE_URL}/clients/{client_id}")
        if get_resp.status_code == 200:
            existing = get_resp.json()
            client_data["user_id"] = existing.get("user_id")
        
        response = await client.put(f"{BASE_URL}/clients/{client_id}", json=client_data)
        
        if response.status_code == 200:
            return RedirectResponse(url=f"/admin/clients/{client_id}", status_code=302)
        else:
            error = response.json().get("detail", "Ошибка при обновлении")
            return templates.TemplateResponse(
                "admin/clients/edit.html",
                {
                    "request": request,
                    "current_user": current_user,
                    "client": client_data,
                    "error": error
                }
            )


# ========== АРЕНДЫ ==========
@router.get("/admin/rentals", response_class=HTMLResponse)
async def admin_rentals(
    request: Request,
    car_id: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Список аренд с фильтрацией"""
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    filters = {}
    params = {}
    
    # Обрабатываем пустые строки как None и конвертируем в int
    def parse_int_or_none(value: Optional[str]) -> Optional[int]:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    car_id_int = parse_int_or_none(car_id)
    client_id_int = parse_int_or_none(client_id)
    
    if car_id_int:
        filters["car_id"] = car_id_int
        params["car_id"] = car_id_int
    if client_id_int:
        filters["client_id"] = client_id_int
        params["client_id"] = client_id_int
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        # Если есть фильтры, передаем их, иначе не передаем params вообще
        if params:
            response = await client.get(f"{BASE_URL}/rentals/", params=params)
        else:
            response = await client.get(f"{BASE_URL}/rentals/")
        rentals = response.json() if response.status_code == 200 else []
        
        # Получаем дополнительные данные
        status_resp = await client.get(f"{BASE_URL}/rental_statuses/")
        statuses = {s["id"]: s for s in status_resp.json()} if status_resp.status_code == 200 else {}
        
        cars_resp = await client.get(f"{BASE_URL}/cars/")
        cars = {c["id"]: c for c in cars_resp.json()} if cars_resp.status_code == 200 else {}
        
        clients_resp = await client.get(f"{BASE_URL}/clients/")
        clients = {c["id"]: c for c in clients_resp.json()} if clients_resp.status_code == 200 else {}
        
        for rental in rentals:
            rental["status"] = statuses.get(rental.get("rental_status_id"), {})
            rental["car"] = cars.get(rental.get("car_id"), {})
            rental["client"] = clients.get(rental.get("client_id"), {})
    
    return templates.TemplateResponse(
        "admin/rentals/list.html",
        {
            "request": request,
            "current_user": current_user,
            "rentals": rentals,
            "cars": list(cars.values()),
            "clients": list(clients.values()),
            "filters": filters
        }
    )


@router.get("/admin/rentals/{rental_id}", response_class=HTMLResponse)
async def admin_rental_detail(
    request: Request,
    rental_id: int,
    db: Session = Depends(get_db)
):
    """Детали аренды"""
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.get(f"{BASE_URL}/rentals/{rental_id}")
        if response.status_code != 200:
            return RedirectResponse(url="/admin/rentals", status_code=302)
        
        rental = response.json()
        
        # Получаем дополнительные данные
        status_resp = await client.get(f"{BASE_URL}/rental_statuses/")
        statuses = {s["id"]: s for s in status_resp.json()} if status_resp.status_code == 200 else {}
        
        car_resp = await client.get(f"{BASE_URL}/cars/{rental.get('car_id')}")
        car = car_resp.json() if car_resp.status_code == 200 else {}
        
        client_resp = await client.get(f"{BASE_URL}/clients/{rental.get('client_id')}")
        client = client_resp.json() if client_resp.status_code == 200 else {}
        
        rental["status"] = statuses.get(rental.get("rental_status_id"), {})
        rental["car"] = car
        rental["client"] = client
    
    return templates.TemplateResponse(
        "admin/rentals/detail.html",
        {
            "request": request,
            "current_user": current_user,
            "rental": rental
        }
    )


@router.get("/admin/rentals/{rental_id}/edit", response_class=HTMLResponse)
async def admin_rental_edit_page(
    request: Request,
    rental_id: int,
    db: Session = Depends(get_db)
):
    """Страница редактирования аренды"""
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.get(f"{BASE_URL}/rentals/{rental_id}")
        if response.status_code != 200:
            return RedirectResponse(url="/admin/rentals", status_code=302)
        
        rental = response.json()
        
        # Получаем списки для выбора
        status_resp = await client.get(f"{BASE_URL}/rental_statuses/")
        statuses = status_resp.json() if status_resp.status_code == 200 else []
        
        cars_resp = await client.get(f"{BASE_URL}/cars/")
        cars = cars_resp.json() if cars_resp.status_code == 200 else []
        
        clients_resp = await client.get(f"{BASE_URL}/clients/")
        clients = clients_resp.json() if clients_resp.status_code == 200 else []
    
    return templates.TemplateResponse(
        "admin/rentals/edit.html",
        {
            "request": request,
            "current_user": current_user,
            "rental": rental,
            "statuses": statuses,
            "cars": cars,
            "clients": clients
        }
    )


@router.post("/admin/rentals/{rental_id}/edit", response_class=HTMLResponse)
async def admin_rental_edit_submit(
    request: Request,
    rental_id: int,
    client_id: int = Form(...),
    car_id: int = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    total_amount: str = Form(...),
    rental_status_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Обработка формы редактирования аренды"""
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    
    rental_data = {
        "id": rental_id,
        "client_id": client_id,
        "car_id": car_id,
        "start_date": start_date,
        "end_date": end_date,
        "total_amount": total_amount,
        "rental_status_id": rental_status_id
    }
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.put(f"{BASE_URL}/rentals/{rental_id}", json=rental_data)
        
        if response.status_code == 200:
            return RedirectResponse(url=f"/admin/rentals/{rental_id}", status_code=302)
        else:
            error = response.json().get("detail", "Ошибка при обновлении")
            # Получаем данные для повторного отображения формы
            status_resp = await client.get(f"{BASE_URL}/rental_statuses/")
            statuses = status_resp.json() if status_resp.status_code == 200 else []
            cars_resp = await client.get(f"{BASE_URL}/cars/")
            cars = cars_resp.json() if cars_resp.status_code == 200 else []
            clients_resp = await client.get(f"{BASE_URL}/clients/")
            clients = clients_resp.json() if clients_resp.status_code == 200 else []
            
            return templates.TemplateResponse(
                "admin/rentals/edit.html",
                {
                    "request": request,
                    "current_user": current_user,
                    "rental": rental_data,
                    "statuses": statuses,
                    "cars": cars,
                    "clients": clients,
                    "error": error
                }
            )


@router.post("/admin/rentals/{rental_id}/delete", response_class=HTMLResponse)
async def admin_rental_delete(
    request: Request,
    rental_id: int,
    db: Session = Depends(get_db)
):
    """Удаление аренды"""
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        await client.delete(f"{BASE_URL}/rentals/{rental_id}")
    
    return RedirectResponse(url="/admin/rentals", status_code=302)


# ========== СТАТИСТИКА ==========
@router.get("/admin/statistics", response_class=HTMLResponse)
async def admin_statistics(
    request: Request,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Страница статистики"""
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    stats = None
    
    if start_date and end_date:
        # Конвертируем datetime-local формат в ISO формат для API
        # datetime-local: "2025-11-20T10:00" -> ISO: "2025-11-20T10:00:00"
        try:
            # Если дата уже в правильном формате, оставляем как есть
            # Иначе добавляем секунды если их нет
            if len(start_date) == 16:  # "YYYY-MM-DDTHH:mm"
                start_date_iso = start_date + ":00"
            else:
                start_date_iso = start_date
            
            if len(end_date) == 16:  # "YYYY-MM-DDTHH:mm"
                end_date_iso = end_date + ":00"
            else:
                end_date_iso = end_date
        except Exception:
            start_date_iso = start_date
            end_date_iso = end_date
        
        async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
            response = await client.get(
                f"{BASE_URL}/admin/rental-statistic",
                params={"start_date": start_date_iso, "end_date": end_date_iso}
            )
            if response.status_code == 200:
                stats = response.json()
    
    return templates.TemplateResponse(
        "admin/statistics.html",
        {
            "request": request,
            "current_user": current_user,
            "stats": stats,
            "start_date": start_date,
            "end_date": end_date
        }
    )

