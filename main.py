from fastapi import FastAPI
from application.auth.routers import auth

app = FastAPI(title="Аренда авто")

app.include_router(auth.router)
