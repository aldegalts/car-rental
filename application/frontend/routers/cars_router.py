from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal

from application.frontend.templates import templates
from application.frontend.utils import get_current_user_async
from infrastructure.database.database_session import get_db
import httpx

router = APIRouter(tags=["Frontend Cars"])

BASE_URL = "http://localhost:8000"


@router.get("/cars", response_class=HTMLResponse)
async def cars_list(
    request: Request,
    brand: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    color_id: Optional[int] = Query(None),
    min_year: Optional[int] = Query(None),
    max_year: Optional[int] = Query(None),
    min_cost: Optional[float] = Query(None),
    max_cost: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """Страница каталога машин"""
    current_user = await get_current_user_async(request, db)
    
    # Получаем фильтры
    filters = {}
    if brand:
        filters["brand"] = brand
    if model:
        filters["model"] = model
    if category_id:
        filters["category_id"] = category_id
    if color_id:
        filters["color_id"] = color_id
    if min_year:
        filters["min_year"] = min_year
    if max_year:
        filters["max_year"] = max_year
    if min_cost:
        filters["min_cost"] = min_cost
    if max_cost:
        filters["max_cost"] = max_cost
    
    cookies = dict(request.cookies)
    
    # Получаем список машин
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        if filters:
            response = await client.get(f"{BASE_URL}/cars/filter", params=filters)
        else:
            response = await client.get(f"{BASE_URL}/cars/")
        
        if response.status_code == 200:
            cars = response.json()
        else:
            cars = []
        
        # Получаем категории, цвета и статусы для фильтров
        categories_resp = await client.get(f"{BASE_URL}/car_categories/")
        categories = categories_resp.json() if categories_resp.status_code == 200 else []
        
        colors_resp = await client.get(f"{BASE_URL}/car_colors/")
        colors = colors_resp.json() if colors_resp.status_code == 200 else []
    
    return templates.TemplateResponse(
        "cars/list.html",
        {
            "request": request,
            "current_user": current_user,
            "cars": cars,
            "categories": categories,
            "colors": colors,
            "filters": filters
        }
    )


@router.get("/cars/{car_id}", response_class=HTMLResponse)
async def car_detail(
    request: Request,
    car_id: int,
    db: Session = Depends(get_db)
):
    """Страница детальной информации о машине"""
    current_user = await get_current_user_async(request, db)
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.get(f"{BASE_URL}/cars/{car_id}")
        
        if response.status_code != 200:
            return RedirectResponse(url="/cars", status_code=302)
        
        car = response.json()
        
        # Получаем категорию, цвет и статус
        category_resp = await client.get(f"{BASE_URL}/car_categories/")
        categories = {c["id"]: c for c in category_resp.json()} if category_resp.status_code == 200 else {}
        
        color_resp = await client.get(f"{BASE_URL}/car_colors/")
        colors = {c["id"]: c for c in color_resp.json()} if color_resp.status_code == 200 else {}
        
        status_resp = await client.get(f"{BASE_URL}/car_statuses/")
        statuses = {s["id"]: s for s in status_resp.json()} if status_resp.status_code == 200 else {}
        
        car["category"] = categories.get(car.get("category_id"), {})
        car["color"] = colors.get(car.get("color_id"), {})
        car["status"] = statuses.get(car.get("car_status_id"), {})
    
    return templates.TemplateResponse(
        "cars/detail.html",
        {
            "request": request,
            "current_user": current_user,
            "car": car
        }
    )

