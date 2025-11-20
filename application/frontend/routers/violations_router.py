from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from application.frontend.templates import templates
from application.frontend.utils import get_current_user_async
from infrastructure.database.database_session import get_db
import httpx

router = APIRouter(tags=["Frontend Violations"], include_in_schema=False)

BASE_URL = "http://localhost:8000"


@router.get("/account/violations", response_class=HTMLResponse)
async def my_violations(request: Request, db: Session = Depends(get_db)):
    """Страница моих нарушений"""
    current_user = await get_current_user_async(request, db)
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.get(f"{BASE_URL}/violations/")
        
        if response.status_code == 200:
            violations = response.json()
        else:
            violations = []
        
        # Получаем типы нарушений
        types_resp = await client.get(f"{BASE_URL}/violation_types/")
        types = {t["id"]: t for t in types_resp.json()} if types_resp.status_code == 200 else {}
        
        # Получаем аренды
        for violation in violations:
            violation["type"] = types.get(violation.get("violation_type_id"), {})
            if violation.get("rental_id"):
                rental_resp = await client.get(f"{BASE_URL}/rentals/{violation['rental_id']}")
                violation["rental"] = rental_resp.json() if rental_resp.status_code == 200 else {}
    
    return templates.TemplateResponse(
        "violations/my.html",
        {
            "request": request,
            "current_user": current_user,
            "violations": violations
        }
    )


@router.get("/account/violations/{violation_id}", response_class=HTMLResponse)
async def violation_detail(
    request: Request,
    violation_id: int,
    db: Session = Depends(get_db)
):
    """Страница детальной информации о нарушении"""
    current_user = await get_current_user_async(request, db)
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.get(f"{BASE_URL}/violations/{violation_id}")
        
        if response.status_code != 200:
            return RedirectResponse(url="/account/violations", status_code=302)
        
        violation = response.json()
        
        # Получаем дополнительные данные
        types_resp = await client.get(f"{BASE_URL}/violation_types/")
        types = {t["id"]: t for t in types_resp.json()} if types_resp.status_code == 200 else {}
        
        violation["type"] = types.get(violation.get("violation_type_id"), {})
        
        if violation.get("rental_id"):
            rental_resp = await client.get(f"{BASE_URL}/rentals/{violation['rental_id']}")
            violation["rental"] = rental_resp.json() if rental_resp.status_code == 200 else {}
    
    return templates.TemplateResponse(
        "violations/detail.html",
        {
            "request": request,
            "current_user": current_user,
            "violation": violation
        }
    )


@router.get("/info/violation-types", response_class=HTMLResponse)
async def violation_types_list(request: Request, db: Session = Depends(get_db)):
    """Страница списка типов нарушений (доступна всем)"""
    current_user = await get_current_user_async(request, db)
    
    async with httpx.AsyncClient(follow_redirects=False) as client:
        response = await client.get(f"{BASE_URL}/violation_types/")
        
        if response.status_code == 200:
            violation_types = response.json()
        else:
            violation_types = []
    
    return templates.TemplateResponse(
        "violation_types/list.html",
        {
            "request": request,
            "current_user": current_user,
            "violation_types": violation_types
        }
    )

