import re

from pydantic import BaseModel, EmailStr, field_validator

from app.models.user import UserRole


class UserRegister(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Пароль должен быть не короче 8 символов")
        if len(value) > 72:
            #bcrypt физически не умеет больше 72 байт, без этой проверки
            #длинный пароль уронит хеширование необработанным исключением
            raise ValueError("Пароль не должен быть длиннее 72 символов")
        if not re.search(r"[A-Za-zА-Яа-я]", value):
            raise ValueError("Пароль должен содержать хотя бы одну букву")
        if not re.search(r"\d", value):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    role: UserRole
    personal_discount_percent: float

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"