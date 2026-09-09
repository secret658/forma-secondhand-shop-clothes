import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.api.dependencies import get_db
from app.database import Base
from app.main import app

#SQLite in-memory для быстрых тестов, не гоняем настоящий MySQL на каждый запуск
#StaticPool нужен, чтобы все подключения шли через одно и то же соединение
#без него каждый запрос открывал бы новую пустую in-memory базу
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    from app.limiter import limiter

    limiter.reset()
    #без этого 5-запросов-в-минуту лимит на /auth/register накопится
    #от предыдущих тестов и следующие тесты начнут падать с 429

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    #пересоздаем базу перед каждым тестом, чтобы тесты не зависели друг от друга


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    #регистрируем и логиним тестового юзера, возвращаем готовый заголовок
    #чтобы не дублировать эти 3 строчки в каждом тесте где нужна авторизация
    client.post("/auth/register", json={"email": "test@test.com", "password": "testpass123"})
    response = client.post("/auth/login", json={"email": "test@test.com", "password": "testpass123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, db_session):
    #для эндпоинтов с require_admin (создание категорий, /admin/*)
    #обычный auth_headers тут не подойдет, там role по умолчанию USER
    from app.models.user import User, UserRole

    client.post("/auth/register", json={"email": "admin@test.com", "password": "testpass123"})
    user = db_session.query(User).filter(User.email == "admin@test.com").first()
    user.role = UserRole.ADMIN
    db_session.commit()

    response = client.post("/auth/login", json={"email": "admin@test.com", "password": "testpass123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}