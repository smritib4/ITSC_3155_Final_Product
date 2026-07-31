"""Integration tests for low-performing dishes (work item 19 / Story 10).

`GET /reports/low-performing` returns dishes with low average ratings and/or
low order counts, including complaint comments from ratings <= 2.
"""


def _create_customer(client, email="lp.customer@example.com"):
    return client.post(
        "/customers/",
        json={
            "name": "Low Perf Customer",
            "email": email,
            "phone": "704-555-0100",
            "hasAccount": True,
        },
    ).json()


def _create_menu_item(client, name="Dish", **overrides):
    payload = {
        "item_name": name,
        "description": f"{name} description",
        "price": "8.00",
        "category": "sandwich",
        "dietary_type": None,
        "is_available": True,
    }
    payload.update(overrides)
    return client.post("/menuitems/", json=payload).json()


def _create_review(client, customer_id, item_id, rating, comment=None):
    return client.post(
        "/reviews/",
        json={
            "customerID": customer_id,
            "item_id": item_id,
            "rating": rating,
            "comment": comment,
        },
    ).json()


def _create_order_with_item(client, item_id, quantity=1):
    order = client.post(
        "/orders/",
        json={
            "orderStatus": "completed",
            "orderType": "dine-in",
            "totalPrice": "8.00",
            "estimatedTime": 15,
            "customerID": 1,
            "employeeID": 1,
        },
    ).json()
    client.post(
        "/orderdetails/",
        json={"order_id": order["orderID"], "item_id": item_id, "quantity": quantity},
    )
    return order


def test_low_performing_includes_low_rated_dish_with_complaints(client):
    customer = _create_customer(client)
    bad = _create_menu_item(client, name="Soggy Sandwich")
    good = _create_menu_item(client, name="Perfect Club")

    _create_review(client, customer["customerID"], bad["item_id"], 1, "Too soggy")
    _create_review(client, customer["customerID"], bad["item_id"], 2, "Bland")
    # Give the good dish enough orders so it is not flagged for low order count.
    for _ in range(3):
        _create_order_with_item(client, good["item_id"])
    _create_review(client, customer["customerID"], good["item_id"], 5, "Amazing")

    response = client.get(
        "/reports/low-performing",
        params={"max_avg_rating": 2.5, "max_order_count": 0},
    )

    assert response.status_code == 200
    body = response.json()
    ids = {dish["item_id"] for dish in body}
    assert bad["item_id"] in ids
    assert good["item_id"] not in ids

    bad_row = next(d for d in body if d["item_id"] == bad["item_id"])
    assert bad_row["average_rating"] <= 2.5
    assert "Too soggy" in bad_row["complaint_comments"]
    assert "Bland" in bad_row["complaint_comments"]


def test_low_performing_includes_low_order_count_dish(client):
    unpopular = _create_menu_item(client, name="Rare Special")
    popular = _create_menu_item(client, name="House Favorite")

    _create_order_with_item(client, unpopular["item_id"], quantity=1)
    for _ in range(5):
        _create_order_with_item(client, popular["item_id"], quantity=2)

    response = client.get(
        "/reports/low-performing",
        params={"max_avg_rating": 1.0, "max_order_count": 2},
    )

    assert response.status_code == 200
    ids = {dish["item_id"] for dish in response.json()}
    assert unpopular["item_id"] in ids
    assert popular["item_id"] not in ids


def test_low_performing_thresholds_are_configurable(client):
    customer = _create_customer(client, email="lp2@example.com")
    mid = _create_menu_item(client, name="Average Dish")
    _create_review(client, customer["customerID"], mid["item_id"], 3, "Okay")
    _create_order_with_item(client, mid["item_id"], quantity=5)

    loose = client.get(
        "/reports/low-performing",
        params={"max_avg_rating": 3.5, "max_order_count": 0},
    )
    strict = client.get(
        "/reports/low-performing",
        params={"max_avg_rating": 2.0, "max_order_count": 0},
    )

    assert mid["item_id"] in {d["item_id"] for d in loose.json()}
    assert mid["item_id"] not in {d["item_id"] for d in strict.json()}


def test_low_performing_empty_when_nothing_qualifies(client):
    customer = _create_customer(client, email="lp3@example.com")
    item = _create_menu_item(client, name="Top Seller")
    for _ in range(3):
        _create_order_with_item(client, item["item_id"], quantity=2)
    _create_review(client, customer["customerID"], item["item_id"], 5, "Best ever")

    response = client.get(
        "/reports/low-performing",
        params={"max_avg_rating": 2.0, "max_order_count": 1},
    )

    assert response.status_code == 200
    assert response.json() == []
