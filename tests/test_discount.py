from datetime import datetime, timedelta, timezone


def _create_category_and_product(client, admin_headers, price=1000, stock=10):
    category_response = client.post("/categories/", json={"name": "Тест категория"}, headers=admin_headers)
    category_id = category_response.json()["id"]
    product_response = client.post(
        "/products/",
        json={"name": "Тест товар", "price": price, "stock_quantity": stock, "category_id": category_id},
        headers=admin_headers,
    )
    return category_id, product_response.json()["id"]


def _create_discount(client, admin_headers, **overrides):
    now = datetime.now(timezone.utc)
    payload = {
        "code": "SALE10",
        "discount_type": "percentage",
        "value": 10,
        "scope": "order",
        "start_date": (now - timedelta(days=1)).isoformat(),
        "end_date": (now + timedelta(days=1)).isoformat(),
        "usage_limit": None,
    }
    payload.update(overrides)
    return client.post("/admin/discounts", json=payload, headers=admin_headers)


def test_cart_preview_without_promo(client, admin_headers):
    _, product_id = _create_category_and_product(client, admin_headers, price=1000)

    response = client.post(
        "/cart/preview", json={"items": [{"product_id": product_id, "quantity": 2}]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["subtotal"] == 2000
    assert data["discount_amount"] == 0
    assert data["total"] == 2000
    assert data["promo_valid"] is None


def test_cart_preview_with_valid_promo(client, admin_headers):
    _, product_id = _create_category_and_product(client, admin_headers, price=1000)
    _create_discount(client, admin_headers)

    response = client.post(
        "/cart/preview",
        json={"items": [{"product_id": product_id, "quantity": 2}], "promo_code": "SALE10"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["subtotal"] == 2000
    assert data["discount_amount"] == 200
    #10% с 2000 это 200
    assert data["total"] == 1800
    assert data["promo_valid"] is True


def test_cart_preview_with_invalid_code(client, admin_headers):
    _, product_id = _create_category_and_product(client, admin_headers, price=1000)

    response = client.post(
        "/cart/preview",
        json={"items": [{"product_id": product_id, "quantity": 1}], "promo_code": "NOPE"},
    )
    assert response.status_code == 200
    data = response.json()
    #корзина не падает, просто без скидки
    assert data["promo_valid"] is False
    assert data["discount_amount"] == 0
    assert data["total"] == data["subtotal"]


def test_cart_preview_with_expired_promo(client, admin_headers):
    _, product_id = _create_category_and_product(client, admin_headers, price=1000)
    now = datetime.now(timezone.utc)
    _create_discount(
        client,
        admin_headers,
        code="EXPIRED",
        start_date=(now - timedelta(days=10)).isoformat(),
        end_date=(now - timedelta(days=1)).isoformat(),
        #срок действия уже прошел
    )

    response = client.post(
        "/cart/preview",
        json={"items": [{"product_id": product_id, "quantity": 1}], "promo_code": "EXPIRED"},
    )
    data = response.json()
    assert data["promo_valid"] is False


def test_cart_preview_with_zero_limit(client, admin_headers):
    #usage_limit=0 значит лимит уже исчерпан с самого начала
    #заказ пока не списывает used_count у промокода (это отдельная фича, cart/preview
    #только читает состояние скидки, не изменяет его), так что тестируем через usage_limit=0 напрямую
    _, product_id = _create_category_and_product(client, admin_headers, price=1000)
    _create_discount(client, admin_headers, code="ZEROLIMIT", usage_limit=0)

    response = client.post(
        "/cart/preview",
        json={"items": [{"product_id": product_id, "quantity": 1}], "promo_code": "ZEROLIMIT"},
    )
    data = response.json()
    assert data["promo_valid"] is False