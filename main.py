from fastapi import FastAPI
from application.auth.routers import auth, auth_swagger
from application.car_category.routers import car_category_router
from application.car_color.routers import car_color_router
from application.car_status.routers import car_status_router

app = FastAPI(title="Car rental")

app.include_router(auth.router)
app.include_router(car_color_router.router)
app.include_router(car_status_router.router)
app.include_router(car_category_router.router)


app.include_router(auth_swagger.router)