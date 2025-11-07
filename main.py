from fastapi import FastAPI
from application.auth.routers import auth, auth_swagger
from application.car_color.routers import car_color_router

app = FastAPI(title="Аренда авто")

app.include_router(auth.router)
app.include_router(car_color_router.router)



app.include_router(auth_swagger.router)