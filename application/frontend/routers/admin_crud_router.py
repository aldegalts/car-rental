from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal

from application.frontend.templates import templates
from application.frontend.utils import get_current_user_async
from infrastructure.database.database_session import get_db
import httpx

router = APIRouter(tags=["Frontend Admin CRUD"])

BASE_URL = "http://localhost:8000"


def check_admin(current_user):
    """Проверка прав администратора"""
    if not current_user or current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещен")


# ========== МАШИНЫ ==========
@router.get("/admin/cars", response_class=HTMLResponse)
async def admin_cars(request: Request, db: Session = Depends(get_db)):
    """Список машин для администратора"""
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.get(f"{BASE_URL}/cars/")
        cars = response.json() if response.status_code == 200 else []
        
        # Получаем дополнительные данные
        categories_resp = await client.get(f"{BASE_URL}/car_categories/")
        categories = {c["id"]: c for c in categories_resp.json()} if categories_resp.status_code == 200 else {}
        
        colors_resp = await client.get(f"{BASE_URL}/car_colors/")
        colors = {c["id"]: c for c in colors_resp.json()} if colors_resp.status_code == 200 else {}
        
        statuses_resp = await client.get(f"{BASE_URL}/car_statuses/")
        statuses = {s["id"]: s for s in statuses_resp.json()} if statuses_resp.status_code == 200 else {}
        
        for car in cars:
            car["category"] = categories.get(car.get("category_id"), {})
            car["color"] = colors.get(car.get("color_id"), {})
            car["status"] = statuses.get(car.get("car_status_id"), {})
    
    return templates.TemplateResponse(
        "admin/cars/list.html",
        {
            "request": request,
            "current_user": current_user,
            "cars": cars
        }
    )


@router.get("/admin/cars/create", response_class=HTMLResponse)
async def admin_car_create_page(request: Request, db: Session = Depends(get_db)):
    """Страница создания машины"""
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        categories_resp = await client.get(f"{BASE_URL}/car_categories/")
        categories = categories_resp.json() if categories_resp.status_code == 200 else []
        
        colors_resp = await client.get(f"{BASE_URL}/car_colors/")
        colors = colors_resp.json() if colors_resp.status_code == 200 else []
        
        statuses_resp = await client.get(f"{BASE_URL}/car_statuses/")
        statuses = statuses_resp.json() if statuses_resp.status_code == 200 else []
    
    return templates.TemplateResponse(
        "admin/cars/create.html",
        {
            "request": request,
            "current_user": current_user,
            "categories": categories,
            "colors": colors,
            "statuses": statuses
        }
    )


@router.post("/admin/cars/create", response_class=HTMLResponse)
async def admin_car_create_submit(
    request: Request,
    brand: str = Form(...),
    model: str = Form(...),
    year: int = Form(...),
    category_id: int = Form(...),
    license_plate: str = Form(...),
    color_id: int = Form(...),
    daily_cost: str = Form(...),
    car_status_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Обработка формы создания машины"""
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    
    car_data = {
        "brand": brand,
        "model": model,
        "year": year,
        "category_id": category_id,
        "license_plate": license_plate,
        "color_id": color_id,
        "daily_cost": daily_cost,
        "car_status_id": car_status_id
    }
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.post(f"{BASE_URL}/cars/", json=car_data)
        
        if response.status_code == 201:
            car = response.json()
            return RedirectResponse(url=f"/admin/cars", status_code=302)
        else:
            error = response.json().get("detail", "Ошибка при создании")
            # Получаем данные для повторного отображения формы
            categories_resp = await client.get(f"{BASE_URL}/car_categories/")
            categories = categories_resp.json() if categories_resp.status_code == 200 else []
            colors_resp = await client.get(f"{BASE_URL}/car_colors/")
            colors = colors_resp.json() if colors_resp.status_code == 200 else []
            statuses_resp = await client.get(f"{BASE_URL}/car_statuses/")
            statuses = statuses_resp.json() if statuses_resp.status_code == 200 else []
            
            return templates.TemplateResponse(
                "admin/cars/create.html",
                {
                    "request": request,
                    "current_user": current_user,
                    "categories": categories,
                    "colors": colors,
                    "statuses": statuses,
                    "error": error
                }
            )


@router.get("/admin/cars/{car_id}/edit", response_class=HTMLResponse)
async def admin_car_edit_page(
    request: Request,
    car_id: int,
    db: Session = Depends(get_db)
):
    """Страница редактирования машины"""
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.get(f"{BASE_URL}/cars/{car_id}")
        if response.status_code != 200:
            return RedirectResponse(url="/admin/cars", status_code=302)
        
        car = response.json()
        
        categories_resp = await client.get(f"{BASE_URL}/car_categories/")
        categories = categories_resp.json() if categories_resp.status_code == 200 else []
        
        colors_resp = await client.get(f"{BASE_URL}/car_colors/")
        colors = colors_resp.json() if colors_resp.status_code == 200 else []
        
        statuses_resp = await client.get(f"{BASE_URL}/car_statuses/")
        statuses = statuses_resp.json() if statuses_resp.status_code == 200 else []
    
    return templates.TemplateResponse(
        "admin/cars/edit.html",
        {
            "request": request,
            "current_user": current_user,
            "car": car,
            "categories": categories,
            "colors": colors,
            "statuses": statuses
        }
    )


@router.post("/admin/cars/{car_id}/edit", response_class=HTMLResponse)
async def admin_car_edit_submit(
    request: Request,
    car_id: int,
    brand: str = Form(...),
    model: str = Form(...),
    year: int = Form(...),
    category_id: int = Form(...),
    license_plate: str = Form(...),
    color_id: int = Form(...),
    daily_cost: str = Form(...),
    car_status_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Обработка формы редактирования машины"""
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    
    car_data = {
        "id": car_id,
        "brand": brand,
        "model": model,
        "year": year,
        "category_id": category_id,
        "license_plate": license_plate,
        "color_id": color_id,
        "daily_cost": daily_cost,
        "car_status_id": car_status_id
    }
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.put(f"{BASE_URL}/cars/{car_id}", json=car_data)
        
        if response.status_code == 200:
            return RedirectResponse(url="/admin/cars", status_code=302)
        else:
            error = response.json().get("detail", "Ошибка при обновлении")
            categories_resp = await client.get(f"{BASE_URL}/car_categories/")
            categories = categories_resp.json() if categories_resp.status_code == 200 else []
            colors_resp = await client.get(f"{BASE_URL}/car_colors/")
            colors = colors_resp.json() if colors_resp.status_code == 200 else []
            statuses_resp = await client.get(f"{BASE_URL}/car_statuses/")
            statuses = statuses_resp.json() if statuses_resp.status_code == 200 else []
            
            return templates.TemplateResponse(
                "admin/cars/edit.html",
                {
                    "request": request,
                    "current_user": current_user,
                    "car": car_data,
                    "categories": categories,
                    "colors": colors,
                    "statuses": statuses,
                    "error": error
                }
            )


@router.post("/admin/cars/{car_id}/delete", response_class=HTMLResponse)
async def admin_car_delete(
    request: Request,
    car_id: int,
    db: Session = Depends(get_db)
):
    """Удаление машины"""
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        await client.delete(f"{BASE_URL}/cars/{car_id}")
    
    return RedirectResponse(url="/admin/cars", status_code=302)

