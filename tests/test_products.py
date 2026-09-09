def test_create_and_get_product(client, admin_headers):
    category_response = client.post("/categories/", json={"name": "Джинсы", "discount_percent": 0}, headers=admin_headers)
    category_id = category_response.json()["id"]

    response = client.post(
        "/products/",
        json={
            "name": "Тестовые джинсы",
            "price": 2000,
            "stock_quantity": 10,
            "category_id": category_id,
        },
        headers=admin_headers,
    )
    assert response.status_code == 200
    product_id = response.json()["id"]
    assert response.json()["likes_count"] == 0

    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Тестовые джинсы"


def test_list_products(client, admin_headers):
    category_response = client.post("/categories/", json={"name": "Кофты"}, headers=admin_headers)
    category_id = category_response.json()["id"]
    client.post(
        "/products/",
        json={"name": "Товар 1", "price": 1000, "stock_quantity": 5, "category_id": category_id},
        headers=admin_headers,
    )
    client.post(
        "/products/",
        json={"name": "Товар 2", "price": 1500, "stock_quantity": 3, "category_id": category_id},
        headers=admin_headers,
    )

    response = client.get("/products/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_toggle_like(client, auth_headers, admin_headers):
    category_response = client.post("/categories/", json={"name": "Куртки"}, headers=admin_headers)
    category_id = category_response.json()["id"]
    product_response = client.post(
        "/products/",
        json={"name": "Куртка", "price": 5000, "stock_quantity": 2, "category_id": category_id},
        headers=admin_headers,
    )
    product_id = product_response.json()["id"]

    like_response = client.post(f"/products/{product_id}/like", headers=auth_headers)
    assert like_response.status_code == 200
    assert like_response.json()["liked"] is True
    assert like_response.json()["likes_count"] == 1

    unlike_response = client.post(f"/products/{product_id}/like", headers=auth_headers)
    assert unlike_response.json()["liked"] is False
    assert unlike_response.json()["likes_count"] == 0


def test_create_product_requires_admin(client, auth_headers):
    #обычный юзер не должен уметь создавать товары
    category_response = client.post("/categories/", json={"name": "Test"}, headers=auth_headers)
    #даже создание категории без прав админа не пройдет, ожидаем 403
    assert category_response.status_code == 403

    response = client.post(
        "/products/",
        json={"name": "Хак товар", "price": 100, "stock_quantity": 1, "category_id": 1},
        headers=auth_headers,
    )
    assert response.status_code == 403