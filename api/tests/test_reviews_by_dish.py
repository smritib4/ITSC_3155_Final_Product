"""Integration tests for reading reviews of a specific dish (Story 27)."""


def _customer(client, email="sam@example.com"):
    return client.post(
        "/customers/",
        json={"name": "Sam", "email": email, "phone": "555-0100", "hasAccount": True},
    ).json()


def _menu_item(client, name="BLT"):
    return client.post(
        "/menuitems/",
        json={
            "item_name": name,
            "description": "test dish",
            "price": "6.50",
            "category": "sandwich",
            "dietary_type": None,
            "is_available": True,
        },
    ).json()


def _review(client, customer_id, item_id, rating=5, comment="great"):
    return client.post(
        "/reviews/",
        json={
            "rating": rating,
            "comment": comment,
            "customerID": customer_id,
            "item_id": item_id,
        },
    ).json()


def test_filter_reviews_by_dish(client):
    customer = _customer(client)
    sandwich = _menu_item(client, name="BLT")
    soup = _menu_item(client, name="Soup")
    _review(client, customer["customerID"], sandwich["item_id"], rating=5, comment="loved it")
    _review(client, customer["customerID"], sandwich["item_id"], rating=4, comment="solid")
    _review(client, customer["customerID"], soup["item_id"], rating=1, comment="too salty")

    response = client.get(f"/reviews/?item_id={sandwich['item_id']}")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert {review["item_id"] for review in body} == {sandwich["item_id"]}
    assert {review["comment"] for review in body} == {"loved it", "solid"}


def test_reviews_without_filter_returns_all(client):
    customer = _customer(client)
    sandwich = _menu_item(client, name="BLT")
    soup = _menu_item(client, name="Soup")
    _review(client, customer["customerID"], sandwich["item_id"])
    _review(client, customer["customerID"], soup["item_id"])

    response = client.get("/reviews/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_filter_reviews_for_dish_with_none(client):
    customer = _customer(client)
    sandwich = _menu_item(client, name="BLT")
    soup = _menu_item(client, name="Soup")
    _review(client, customer["customerID"], sandwich["item_id"])

    response = client.get(f"/reviews/?item_id={soup['item_id']}")

    assert response.status_code == 200
    assert response.json() == []
