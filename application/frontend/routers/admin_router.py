import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple
from urllib.parse import quote_plus

import httpx
from fastapi import APIRouter, Depends, Request, Form, Query, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from application.car.usecases import GetCarUseCase
from application.client.usecases.get_client_by_id_use_case import GetClientByIdUseCase
from application.frontend.templates import templates
from application.frontend.utils import get_current_user_async
from application.rental.usecases import GetRentalByIdUseCase
from application.rental_status.usecases import GetAllRentalStatusesUseCase
from application.violation.usecases import GetViolationsByRentalUseCase
from application.violation_type.usecases import GetAllViolationTypesUseCase
from infrastructure.database.database_session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Frontend Admin"])

BASE_URL = "http://localhost:8000"


def check_admin(current_user):
    if not current_user or current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещен")


def _current_time_iso() -> str:
    return datetime.utcnow().replace(second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M")


def _format_datetime_local(datetime_str: Optional[str]) -> Optional[str]:
    if not datetime_str:
        return None
    try:
        sanitized_value = datetime_str.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(sanitized_value)
        return parsed.strftime("%Y-%m-%dT%H:%M")
    except ValueError:
        return datetime_str[:16]


async def _fetch_violation_types(client: httpx.AsyncClient):
    response = await client.get(f"{BASE_URL}/violation_types/")
    if response.status_code == 200:
        return response.json()
    return []


async def _load_rental_detail(
    client: httpx.AsyncClient,
    rental_id: int
):
    rental_resp = await client.get(f"{BASE_URL}/rentals/{rental_id}")
    if rental_resp.status_code != 200:
        return None, [], []

    rental = rental_resp.json()

    status_resp = await client.get(f"{BASE_URL}/rental_statuses/")
    statuses = {s["id"]: s for s in status_resp.json()} if status_resp.status_code == 200 else {}

    car_resp = await client.get(f"{BASE_URL}/cars/{rental.get('car_id')}")
    car = car_resp.json() if car_resp.status_code == 200 else {}

    client_resp = await client.get(f"{BASE_URL}/clients/{rental.get('client_id')}")
    client_data = client_resp.json() if client_resp.status_code == 200 else {}

    rental["status"] = statuses.get(rental.get("rental_status_id"), {})
    rental["car"] = car
    rental["client"] = client_data

    violations_resp = await client.get(f"{BASE_URL}/violations/rental/{rental_id}")
    violations = violations_resp.json() if violations_resp.status_code == 200 else []

    violation_types = await _fetch_violation_types(client)
    violation_types_map = {v["id"]: v for v in violation_types}

    for violation in violations:
        violation["type"] = violation_types_map.get(violation.get("violation_type_id"), {})

    return rental, violations, violation_types


def _load_rental_detail_from_db(
    db: Session,
    rental_id: int
) -> Tuple[Optional[dict], list, list]:
    try:
        rental_model = GetRentalByIdUseCase(db).execute(rental_id)
    except HTTPException:
        return None, [], []

    rental = rental_model.model_dump(mode="json")

    try:
        car_model = GetCarUseCase(db).execute(rental["car_id"])
        rental["car"] = car_model.model_dump(mode="json")
    except HTTPException:
        rental["car"] = {}

    try:
        client_model = GetClientByIdUseCase(db).execute(rental["client_id"])
        rental["client"] = client_model.model_dump(mode="json")
    except HTTPException:
        rental["client"] = {}

    try:
        statuses = GetAllRentalStatusesUseCase(db).execute()
        statuses_map = {status.id: status.model_dump(mode="json") for status in statuses}
    except Exception:
        statuses_map = {}
    rental["status"] = statuses_map.get(rental.get("rental_status_id"), {})

    try:
        violation_types_models = GetAllViolationTypesUseCase(db).execute()
        violation_types = [v.model_dump(mode="json") for v in violation_types_models]
    except Exception:
        violation_types = []

    violation_types_map = {v["id"]: v for v in violation_types}

    try:
        violations_models = GetViolationsByRentalUseCase(db).execute(rental_id)
        violations = [violation.model_dump(mode="json") for violation in violations_models]
    except Exception:
        violations = []

    for violation in violations:
        violation["type"] = violation_types_map.get(violation.get("violation_type_id"), {})

    return rental, violations, violation_types


async def _get_rental_detail_data(
    rental_id: int,
    cookies: dict,
    db: Session
) -> Tuple[Optional[dict], list, list]:
    try:
        async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
            rental, violations, violation_types = await _load_rental_detail(client, rental_id)
    except httpx.HTTPError as exc:
        logger.warning("Failed to load rental %s via API: %s. Falling back to DB.", rental_id, exc)
        return _load_rental_detail_from_db(db, rental_id)

    if rental is None:
        return None, [], []

    return rental, violations, violation_types


@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        stats_resp = await client.get(f"{BASE_URL}/cars/")
        cars_count = len(stats_resp.json()) if stats_resp.status_code == 200 else 0
        
        clients_resp = await client.get(f"{BASE_URL}/clients/")
        clients_count = len(clients_resp.json()) if clients_resp.status_code == 200 else 0

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


@router.get("/admin/clients", response_class=HTMLResponse)
async def admin_clients(request: Request, db: Session = Depends(get_db)):
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


@router.get("/admin/rentals", response_class=HTMLResponse)
async def admin_rentals(
    request: Request,
    car_id: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    filters = {}
    params = {}

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
        if params:
            response = await client.get(f"{BASE_URL}/rentals/", params=params)
        else:
            response = await client.get(f"{BASE_URL}/rentals/")
        rentals = response.json() if response.status_code == 200 else []

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
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)

    message = request.query_params.get("message")
    cookies = dict(request.cookies)

    rental, violations, violation_types = await _get_rental_detail_data(rental_id, cookies, db)
    if rental is None:
        return RedirectResponse(url="/admin/rentals", status_code=302)

    return templates.TemplateResponse(
        "admin/rentals/detail.html",
        {
            "request": request,
            "current_user": current_user,
            "rental": rental,
            "violations": violations,
            "violation_types": violation_types,
            "current_time_iso": _current_time_iso(),
            "message": message
        }
    )


@router.post("/admin/rentals/{rental_id}/violations", response_class=HTMLResponse)
async def admin_rental_add_violation(
    request: Request,
    rental_id: int,
    violation_type_id: int = Form(...),
    description: str = Form(...),
    fine_amount: str = Form(...),
    violation_date: str = Form(...),
    is_paid: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)

    cookies = dict(request.cookies)
    form_data = {
        "violation_type_id": violation_type_id,
        "description": description,
        "fine_amount": fine_amount,
        "violation_date": violation_date,
        "is_paid": bool(is_paid)
    }

    try:
        fine_value = str(Decimal(fine_amount))
    except InvalidOperation:
        error = "Некорректная сумма штрафа"
        rental, violations, violation_types = await _get_rental_detail_data(rental_id, cookies, db)
        if rental is None:
            return RedirectResponse(url="/admin/rentals", status_code=302)
        return templates.TemplateResponse(
            "admin/rentals/detail.html",
            {
                "request": request,
                "current_user": current_user,
                "rental": rental,
                "violations": violations,
                "violation_types": violation_types,
                "current_time_iso": _current_time_iso(),
                "form_data": form_data,
                "error": error
            }
        )

    violation_date_value = violation_date
    if violation_date_value and len(violation_date_value) == 16:
        violation_date_value = violation_date_value + ":00"

    payload = {
        "rental_id": rental_id,
        "violation_type_id": violation_type_id,
        "description": description,
        "fine_amount": fine_value,
        "violation_date": violation_date_value,
        "is_paid": bool(is_paid)
    }

    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.post(f"{BASE_URL}/violations/", json=payload)
        if response.status_code == 201:
            success_message = quote_plus("Нарушение добавлено")
            return RedirectResponse(
                url=f"/admin/rentals/{rental_id}?message={success_message}",
                status_code=303
            )
        error_detail = response.json().get("detail", "Не удалось сохранить нарушение")

    rental, violations, violation_types = await _get_rental_detail_data(rental_id, cookies, db)
    if rental is None:
        return RedirectResponse(url="/admin/rentals", status_code=302)

    return templates.TemplateResponse(
        "admin/rentals/detail.html",
        {
            "request": request,
            "current_user": current_user,
            "rental": rental,
            "violations": violations,
            "violation_types": violation_types,
            "current_time_iso": _current_time_iso(),
            "form_data": form_data,
            "error": error_detail
        }
    )


@router.get("/admin/rentals/{rental_id}/violations/{violation_id}/edit", response_class=HTMLResponse)
async def admin_rental_violation_edit_page(
    request: Request,
    rental_id: int,
    violation_id: int,
    db: Session = Depends(get_db)
):
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)

    cookies = dict(request.cookies)

    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        violation_resp = await client.get(f"{BASE_URL}/violations/{violation_id}")
        if violation_resp.status_code != 200:
            return RedirectResponse(url=f"/admin/rentals/{rental_id}", status_code=302)

        violation = violation_resp.json()
        if violation.get("rental_id") != rental_id:
            return RedirectResponse(url=f"/admin/rentals/{rental_id}", status_code=302)

        violation_types = await _fetch_violation_types(client)

    return templates.TemplateResponse(
        "admin/violations/edit.html",
        {
            "request": request,
            "current_user": current_user,
            "violation": violation,
            "violation_types": violation_types,
            "violation_date_value": _format_datetime_local(violation.get("violation_date"))
        }
    )


@router.post("/admin/rentals/{rental_id}/violations/{violation_id}/edit", response_class=HTMLResponse)
async def admin_rental_violation_edit_submit(
    request: Request,
    rental_id: int,
    violation_id: int,
    violation_type_id: int = Form(...),
    description: str = Form(...),
    fine_amount: str = Form(...),
    violation_date: str = Form(...),
    is_paid: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)

    cookies = dict(request.cookies)
    violation = {
        "id": violation_id,
        "rental_id": rental_id,
        "violation_type_id": violation_type_id,
        "description": description,
        "fine_amount": fine_amount,
        "violation_date": violation_date,
        "is_paid": bool(is_paid)
    }

    try:
        fine_value = str(Decimal(fine_amount))
    except InvalidOperation:
        async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
            violation_types = await _fetch_violation_types(client)
        return templates.TemplateResponse(
            "admin/violations/edit.html",
            {
                "request": request,
                "current_user": current_user,
                "violation": violation,
                "violation_types": violation_types,
                "violation_date_value": violation_date,
                "error": "Некорректная сумма штрафа"
            }
        )

    violation_date_value = violation_date
    if violation_date_value and len(violation_date_value) == 16:
        violation_date_value = violation_date_value + ":00"

    payload = {
        "id": violation_id,
        "rental_id": rental_id,
        "violation_type_id": violation_type_id,
        "description": description,
        "fine_amount": fine_value,
        "violation_date": violation_date_value,
        "is_paid": bool(is_paid)
    }

    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.put(f"{BASE_URL}/violations/{violation_id}", json=payload)
        if response.status_code == 200:
            success_message = quote_plus("Нарушение обновлено")
            return RedirectResponse(
                url=f"/admin/rentals/{rental_id}?message={success_message}",
                status_code=303
            )

        violation_types = await _fetch_violation_types(client)
        error_detail = response.json().get("detail", "Не удалось обновить нарушение")

    return templates.TemplateResponse(
        "admin/violations/edit.html",
        {
            "request": request,
            "current_user": current_user,
            "violation": violation,
            "violation_types": violation_types,
            "violation_date_value": violation_date,
            "error": error_detail
        }
    )


@router.post("/admin/rentals/{rental_id}/violations/{violation_id}/delete", response_class=HTMLResponse)
async def admin_rental_violation_delete(
    request: Request,
    rental_id: int,
    violation_id: int,
    db: Session = Depends(get_db)
):
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)

    cookies = dict(request.cookies)

    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.delete(f"{BASE_URL}/violations/{violation_id}")
        if response.status_code in (200, 204):
            success_message = quote_plus("Нарушение удалено")
            return RedirectResponse(
                url=f"/admin/rentals/{rental_id}?message={success_message}",
                status_code=303
            )
        error_detail = response.json().get("detail", "Не удалось удалить нарушение")

    rental, violations, violation_types = await _get_rental_detail_data(rental_id, cookies, db)
    if rental is None:
        return RedirectResponse(url="/admin/rentals", status_code=302)

    return templates.TemplateResponse(
        "admin/rentals/detail.html",
        {
            "request": request,
            "current_user": current_user,
            "rental": rental,
            "violations": violations,
            "violation_types": violation_types,
            "current_time_iso": _current_time_iso(),
            "error": error_detail
        }
    )


@router.get("/admin/rentals/{rental_id}/edit", response_class=HTMLResponse)
async def admin_rental_edit_page(
    request: Request,
    rental_id: int,
    db: Session = Depends(get_db)
):
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.get(f"{BASE_URL}/rentals/{rental_id}")
        if response.status_code != 200:
            return RedirectResponse(url="/admin/rentals", status_code=302)
        
        rental = response.json()

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
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        await client.delete(f"{BASE_URL}/rentals/{rental_id}")
    
    return RedirectResponse(url="/admin/rentals", status_code=302)


@router.get("/admin/violation-types", response_class=HTMLResponse)
async def admin_violation_types(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)

    message = request.query_params.get("message")
    cookies = dict(request.cookies)

    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        violation_types = await _fetch_violation_types(client)

    return templates.TemplateResponse(
        "admin/violation_types/list.html",
        {
            "request": request,
            "current_user": current_user,
            "violation_types": violation_types,
            "message": message
        }
    )


@router.post("/admin/violation-types", response_class=HTMLResponse)
async def admin_violation_type_create(
    request: Request,
    type_name: str = Form(...),
    default_fine: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)

    cookies = dict(request.cookies)
    form_data = {
        "type_name": type_name,
        "default_fine": default_fine,
        "description": description
    }

    try:
        fine_value = str(Decimal(default_fine))
    except InvalidOperation:
        async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
            violation_types = await _fetch_violation_types(client)
        return templates.TemplateResponse(
            "admin/violation_types/list.html",
            {
                "request": request,
                "current_user": current_user,
                "violation_types": violation_types,
                "form_data": form_data,
                "error": "Некорректная сумма штрафа"
            }
        )

    payload = {
        "type_name": type_name,
        "default_fine": fine_value,
        "description": description
    }

    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.post(f"{BASE_URL}/violation_types/", json=payload)
        if response.status_code == 201:
            success_message = quote_plus("Тип нарушения добавлен")
            return RedirectResponse(url=f"/admin/violation-types?message={success_message}", status_code=303)

        violation_types = await _fetch_violation_types(client)
        error_detail = response.json().get("detail", "Не удалось создать тип нарушения")

    return templates.TemplateResponse(
        "admin/violation_types/list.html",
        {
            "request": request,
            "current_user": current_user,
            "violation_types": violation_types,
            "form_data": form_data,
            "error": error_detail
        }
    )


@router.get("/admin/violation-types/{violation_type_id}/edit", response_class=HTMLResponse)
async def admin_violation_type_edit_page(
    request: Request,
    violation_type_id: int,
    db: Session = Depends(get_db)
):
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)

    cookies = dict(request.cookies)

    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.get(f"{BASE_URL}/violation_types/{violation_type_id}")
        if response.status_code != 200:
            return RedirectResponse(url="/admin/violation-types", status_code=302)
        violation_type = response.json()

    return templates.TemplateResponse(
        "admin/violation_types/edit.html",
        {
            "request": request,
            "current_user": current_user,
            "violation_type": violation_type
        }
    )


@router.post("/admin/violation-types/{violation_type_id}/edit", response_class=HTMLResponse)
async def admin_violation_type_edit_submit(
    request: Request,
    violation_type_id: int,
    type_name: str = Form(...),
    default_fine: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)

    cookies = dict(request.cookies)
    violation_type = {
        "id": violation_type_id,
        "type_name": type_name,
        "default_fine": default_fine,
        "description": description
    }

    try:
        fine_value = str(Decimal(default_fine))
    except InvalidOperation:
        return templates.TemplateResponse(
            "admin/violation_types/edit.html",
            {
                "request": request,
                "current_user": current_user,
                "violation_type": violation_type,
                "error": "Некорректная сумма штрафа"
            }
        )

    payload = {
        "id": violation_type_id,
        "type_name": type_name,
        "default_fine": fine_value,
        "description": description
    }

    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.put(f"{BASE_URL}/violation_types/{violation_type_id}", json=payload)
        if response.status_code == 200:
            success_message = quote_plus("Тип нарушения обновлен")
            return RedirectResponse(
                url=f"/admin/violation-types?message={success_message}",
                status_code=303
            )

        error_detail = response.json().get("detail", "Не удалось обновить тип нарушения")

    return templates.TemplateResponse(
        "admin/violation_types/edit.html",
        {
            "request": request,
            "current_user": current_user,
            "violation_type": violation_type,
            "error": error_detail
        }
    )


@router.post("/admin/violation-types/{violation_type_id}/delete", response_class=HTMLResponse)
async def admin_violation_type_delete(
    request: Request,
    violation_type_id: int,
    db: Session = Depends(get_db)
):
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)

    cookies = dict(request.cookies)

    async with httpx.AsyncClient(cookies=cookies, follow_redirects=False) as client:
        response = await client.delete(f"{BASE_URL}/violation_types/{violation_type_id}")
        if response.status_code in (200, 204):
            success_message = quote_plus("Тип нарушения удален")
            return RedirectResponse(
                url=f"/admin/violation-types?message={success_message}",
                status_code=303
            )

        violation_types = await _fetch_violation_types(client)
        error_detail = response.json().get("detail", "Не удалось удалить тип нарушения")

    return templates.TemplateResponse(
        "admin/violation_types/list.html",
        {
            "request": request,
            "current_user": current_user,
            "violation_types": violation_types,
            "error": error_detail
        }
    )


@router.get("/admin/statistics", response_class=HTMLResponse)
async def admin_statistics(
    request: Request,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user_async(request, db)
    check_admin(current_user)
    
    cookies = dict(request.cookies)
    stats = None
    
    if start_date and end_date:
        try:
            if len(start_date) == 16:
                start_date_iso = start_date + ":00"
            else:
                start_date_iso = start_date
            
            if len(end_date) == 16:
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

