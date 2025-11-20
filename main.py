from fastapi import FastAPI

from application.admin.routers import documentation_router
from application.auth.routers import auth
from application.car.routers import car_router
from application.car_category.routers import car_category_router
from application.car_color.routers import car_color_router
from application.car_status.routers import car_status_router
from application.rental.routers import rental_router
from application.rental_status.routers import rental_status_router
from application.violation.routers import violation_router
from application.violation_type.routers import violation_type_router
from application.client.routers import client_router

# Фронтенд роутеры
from application.frontend.routers import frontend_router, cars_router, profile_router, rentals_router, violations_router
from application.frontend.routers import admin_router, admin_crud_router

app = FastAPI(title="Car rental", docs_url=None, redoc_url=None)

# API роутеры
app.include_router(auth.router)
app.include_router(car_color_router.router)
app.include_router(car_status_router.router)
app.include_router(car_category_router.router)
app.include_router(car_router.router)
app.include_router(rental_status_router.router)
app.include_router(rental_router.router)
app.include_router(violation_type_router.router)
app.include_router(violation_router.router)
app.include_router(client_router.router)
app.include_router(documentation_router.router)

# Фронтенд роутеры
app.include_router(frontend_router.router)
app.include_router(cars_router.router)
app.include_router(profile_router.router)
app.include_router(rentals_router.router)
app.include_router(violations_router.router)
app.include_router(admin_router.router)
app.include_router(admin_crud_router.router)
