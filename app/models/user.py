from sqlalchemy import Column, Integer, String, Numeric, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class UserRole(str, enum.Enum):
#перечисление ролей, а не просто bool is_admin
#почему: если завтра появится третья роль (например модератор), enum расширяется одной строкой, а bool пришлось бы переделывать в отдельное поле
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
#стандартный первичный ключ, ничего нового

    email = Column(String(255), unique=True, index=True, nullable=False)
#unique=True на уровне базы, а не только проверка в коде
#почему: проверка в Python-коде это race condition сама по себе, если два запроса одновременно регистрируются с одним email, constraint в базе твоя последняя линия защиты

    hashed_password = Column(String(255), nullable=False)
#та же логика что в таск-трекере, bcrypt хеш, не трогаем пароль в открытом виде никогда

    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
#RBAC на минималках, но этого достаточно для двухуровневой системы user/admin
#в admin_service потом будет проверка current_user.role == UserRole.ADMIN

    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
 
    personal_discount_percent = Column(Numeric(5, 2), default=0)
#Numeric, а не Float
#почему: Float хранит деньги/проценты неточно из-за бинарного округления (классический пример 0.1 + 0.2 != 0.3), для денег и скидок в проде всегда Numeric/Decimal

    orders = relationship("Order", back_populates="user")
#связь один-ко-многим, один юзер может иметь много заказов

    admin_actions = relationship("AdminAction", back_populates="admin")