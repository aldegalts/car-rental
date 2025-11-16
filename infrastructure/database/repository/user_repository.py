from sqlalchemy.orm import Session

from infrastructure.database.models import UserEntity


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: int) -> UserEntity | None:
        return self.session.query(UserEntity).filter(UserEntity.id == user_id).first()

    def get_by_username(self, username: str) -> UserEntity | None:
        return (
            self.session.query(UserEntity)
            .filter(UserEntity.username == username)
            .first()
        )

    def create(self, user: UserEntity) -> UserEntity:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user