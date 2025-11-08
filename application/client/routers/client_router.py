from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.client.schemas import ClientRead, ClientCreate, ClientUpdate
from application.client.usecases import CreateClientUseCase, UpdateClientUseCase
from application.dependencies import get_current_user
from infrastructure.database.database_session import get_db

router = APIRouter(prefix="/client", tags=["Client"])


@router.post("/", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def add_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db)
):
    return CreateClientUseCase(db).execute(client_data)



@router.put("/{client_id}", response_model=ClientRead)
def add_car(
    client_data: ClientUpdate,
    db: Session = Depends(get_db)
):
    return UpdateClientUseCase(db).execute(client_data)