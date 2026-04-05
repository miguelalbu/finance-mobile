from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    """
    Responsável pelas regras de negócio de autenticação.
    (Single Responsibility Principle)
    """

    def register(self, db: Session, data: RegisterRequest) -> User:
        if user_repository.get_by_email(db, data.email):
            raise ValueError("Email já cadastrado")
        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        return user_repository.create(db, user)

    def login(self, db: Session, data: LoginRequest) -> Optional[str]:
        user = user_repository.get_by_email(db, data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            return None
        return create_access_token(subject=str(user.id))

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return user_repository.get_by_id(db, user_id)


auth_service = AuthService()
