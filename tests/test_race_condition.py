import threading

import pytest
from sqlalchemy.orm import sessionmaker

from app.database import Base, engine
from app.models.category import Category
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderItemCreate
from app.services.auth_service import pwd_context
from app.services.order_service import OrderService

#этот тест бьет по настоящей MySQL из docker-compose, не по SQLite
#запускать через: docker compose exec app pytest tests/test_race_condition.py -v
#SQLite не поддерживает нормальную блокировку строк при параллельных подключениях,
#а весь смысл теста в том чтобы проверить SELECT FOR UPDATE на реальной базе

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def real_db_setup():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    category = Category(name="Race Test Category")
    session.add(category)
    session.commit()
    session.refresh(category)

    #stock_quantity=1, это ключевое: только один заказ должен пройти
    product = Product(
        name="Last Item",
        price=1000,
        stock_quantity=1,
        category_id=category.id,
    )
    session.add(product)
    session.commit()
    session.refresh(product)

    user = User(email="race@test.com", hashed_password=pwd_context.hash("pass123"))
    session.add(user)
    session.commit()
    session.refresh(user)

    product_id = product.id
    user_id = user.id
    session.close()

    yield product_id, user_id

    #чистим за собой
    cleanup_session = SessionLocal()
    cleanup_session.query(Product).filter(Product.id == product_id).delete()
    cleanup_session.query(User).filter(User.id == user_id).delete()
    cleanup_session.commit()
    cleanup_session.close()


def test_concurrent_orders_on_last_item(real_db_setup):
    product_id, user_id = real_db_setup
    results = []

    def try_create_order():
        #каждый поток открывает свою собственную сессию и своего заказ-сервиса
        #это важно, sqlalchemy Session не потокобезопасна сама по себе
        session = SessionLocal()
        service = OrderService(session)
        try:
            items = [OrderItemCreate(product_id=product_id, quantity=1)]
            order = service.create_order(user_id=user_id, items=items)
            results.append(("success", order.id))
        except Exception as e:
            results.append(("failed", str(e)))
        finally:
            session.close()

    #запускаем 5 потоков одновременно на товар с остатком в 1 штуку
    threads = [threading.Thread(target=try_create_order) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    successes = [r for r in results if r[0] == "success"]
    #без SELECT FOR UPDATE тут могло бы пройти несколько заказов разом
    #с блокировкой должен пройти ровно один
    assert len(successes) == 1, f"Ожидали ровно 1 успешный заказ, получили {len(successes)}: {results}"