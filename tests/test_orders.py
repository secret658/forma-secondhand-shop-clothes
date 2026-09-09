def test_create_order_success(client, auth_headers, admin_headers):
    category_response = client.post("/categories/", json={"name": "Обувь"}, headers=admin_headers)
    category_id = category_response.json()["id"]
    product_response = client.post(
        "/products/",
        json={"name": "Кроссовки", "price": 3000, "stock_quantity": 5, "category_id": category_id},
        headers=admin_headers,
    )
    product_id = product_response.json()["id"]

    order_response = client.post(
        "/orders/",
        json={"items": [{"product_id": product_id, "quantity": 2}]},
        headers=auth_headers,
    )
    assert order_response.status_code == 200

    product_after = client.get(f"/products/{product_id}")
    assert product_after.json()["stock_quantity"] == 3


def test_create_order_insufficient_stock(client, auth_headers, admin_headers):
    category_response = client.post("/categories/", json={"name": "Шапки"}, headers=admin_headers)
    category_id = category_response.json()["id"]
    product_response = client.post(
        "/products/",
        json={"name": "Шапка", "price": 500, "stock_quantity": 1, "category_id": category_id},
        headers=admin_headers,
    )
    product_id = product_response.json()["id"]

    order_response = client.post(
        "/orders/",
        json={"items": [{"product_id": product_id, "quantity": 5}]},
        headers=auth_headers,
    )
    assert order_response.status_code == 400
    product_after = client.get(f"/products/{product_id}")
    assert product_after.json()["stock_quantity"] == 1