from sqlalchemy.orm import Session

from infrastructure.database.models import RoleEntity


class RoleRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_role_name(self, role_name: str) -> RoleEntity | None:
        return (
            self.session.query(RoleEntity)
            .filter(RoleEntity.role_name == role_name)
            .first()
        )