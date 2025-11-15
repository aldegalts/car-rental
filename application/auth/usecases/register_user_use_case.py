from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from application.auth.schemas import UserCreate, UserResponse
from application.auth.utils.security import get_password_hash
from infrastructure.database.models import UserEntity

from infrastructure.database.repository import UserRepository, RoleRepository


class RegisterUserUseCase:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    def register_user(self, user_data: UserCreate) -> UserResponse:
        if self.user_repo.get_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        user_role = self.role_repo.get_by_role_name("user")
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default role 'user' not found in database"
            )

        hashed_password = get_password_hash(user_data.password)

        created_user = self.user_repo.create(
            UserEntity(
                username=user_data.username,
                password_hash=hashed_password,
                role_id=user_role.id
            )
        )

        return UserResponse(
            id=created_user.id,
            username=created_user.username,
            role=created_user.role.role_name
        )
