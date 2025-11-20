from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.client.schemas import ClientRead, ClientCreate, ClientUpdate
from application.client.usecases import CreateClientUseCase, UpdateClientUseCase, GetAllClientsUseCase
from application.client.usecases.get_client_by_id_use_case import GetClientByIdUseCase
from application.client.usecases.get_client_by_user_id_use_case import GetClientByUserIdUseCase
from application.dependencies import get_current_user
from infrastructure.database.database_session import get_db
from infrastructure.database.models import UserEntity

router = APIRouter(prefix="/clients", tags=["Client"])


@router.get("/", response_model=List[ClientRead])
def get_all_clients(
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can get all clients")

    return GetAllClientsUseCase(db).execute()


@router.get("/profile", response_model=ClientRead)
def get_profile(
        current_user: UserEntity = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if current_user.role.role_name != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only user can get his profile")

    return GetClientByUserIdUseCase(db).execute(current_user.id)


@router.get("/{client_id}", response_model=ClientRead)
def get_client_by_id(
        client_id: int,
        current_user: UserEntity = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can get client by id")

    return GetClientByIdUseCase(db).execute(client_id)


@router.post("/", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def add_client(
    client_data: ClientCreate,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only authorized user can add client")

    return CreateClientUseCase(db).execute(client_data)


@router.put("/{client_id}", response_model=ClientRead)
def update_client(
    client_data: ClientUpdate,
    current_user: UserEntity = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can update clients")

    return UpdateClientUseCase(db).execute(client_data)