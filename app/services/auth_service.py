from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.repositories.user_repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)

    def register(self, email: str, password: str) -> User:
        existing = self.repository.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Юзер с таким email уже есть"
            )

        hashed_password = pwd_context.hash(password)
        user = self.repository.create(email=email, hashed_password=hashed_password)
        return user

    def authenticate(self, email: str, password: str) -> User:
        user = self.repository.get_by_email(email)

        #если юзера вообще нет, все равно делаем hash-сравнение с фиктивным паролем
        #иначе по времени ответа можно было бы угадать существует ли email в базе
        if user is None:
            pwd_context.verify(password, pwd_context.hash("dummy_password_for_timing"))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль"
            )

        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Аккаунт заблокирован до {user.locked_until.strftime('%H:%M:%S')} из-за подозрительной активности",
            )

        if not pwd_context.verify(password, user.hashed_password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                user.locked_until = datetime.now(timezone.utc) + timedelta(
                    minutes=LOCKOUT_DURATION_MINUTES
                )
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль"
            )

        #успешный вход, сбрасываем счетчик
        user.failed_login_attempts = 0
        user.locked_until = None
        self.db.commit()

        return user

    def create_access_token(self, user: User) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload = {"sub": str(user.id), "exp": expire}
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token