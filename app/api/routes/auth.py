from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.limiter import limiter
from app.models.user import User
from app.schemas.user import Token, UserLogin, UserOut, UserRegister
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
@limiter.limit("5/minute")
def register(request: Request, data: UserRegister, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register(email=data.email, password=data.password)
    return user


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, data: UserLogin, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.authenticate(email=data.email, password=data.password)
    token = service.create_access_token(user)
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    #по токену возвращает текущего юзера
    #нужен фронту чтобы восстанавливать сессию после обновления страницы,
    #не полагаясь на данные из формы логина которые сбрасываются при reload
    return current_user