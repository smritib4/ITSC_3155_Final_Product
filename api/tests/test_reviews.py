"""Integration tests for the Reviews feature (work item 12)."""


def _create_customer(client, **overrides):
    payload = {
        "name": "Reviewer One",
        "email": "reviewer.one@example.com",
        "phone": "704-555-0111",
        "hasAccount": True,
    }
    payload.update(overrides)
    return client.post("/customers/", json=payload).json()


def _create_menu_item(client, **overrides):
    payload = {
        "item_name": "BLT Sandwich",
        "description": "Bacon, lettuce, tomato",
        "price": "7.50",
        "category": "sandwich",
        "dietary_type": None,
        "is_available": True,
    }
    payload.update(overrides)
    return client.post("/menuitems/", json=payload).json()


def _sample_review(customer_id, item_id, **overrides):
    payload = {
        "rating": 4,
        "comment": "Really good sandwich",
        "customerID": customer_id,
        "item_id": item_id,
    }
    payload.update(overrides)
    return payload


def test_create_review(client):
    customer = _create_customer(client)
    menu_item = _create_menu_item(client)

    response = client.post(
        "/reviews/",
        json=_sample_review(customer["customerID"], menu_item["item_id"]),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["reviewID"] is not None
    assert body["rating"] == 4
    assert body["comment"] == "Really good sandwich"
    assert body["customerID"] == customer["customerID"]
    assert body["item_id"] == menu_item["item_id"]
    assert body["reviewDate"] is not None


def test_create_review_invalid_rating_rejected(client):
    customer = _create_customer(client)
    menu_item = _create_menu_item(client)

    response = client.post(
        "/reviews/",
        json=_sample_review(customer["customerID"], menu_item["item_id"], rating=6),
    )

    assert response.status_code == 422


def test_read_all_reviews(client):
    customer = _create_customer(client)
    menu_item = _create_menu_item(client)
    client.post("/reviews/", json=_sample_review(customer["customerID"], menu_item["item_id"]))
    client.post(
        "/reviews/",
        json=_sample_review(
            customer["customerID"],
            menu_item["item_id"],
            rating=2,
            comment="Too salty",
        ),
    )

    response = client.get("/reviews/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_one_review(client):
    customer = _create_customer(client)
    menu_item = _create_menu_item(client)
    created = client.post(
        "/reviews/",
        json=_sample_review(customer["customerID"], menu_item["item_id"]),
    ).json()

    response = client.get(f"/reviews/{created['reviewID']}")

    assert response.status_code == 200
    assert response.json()["reviewID"] == created["reviewID"]


def test_read_one_review_not_found(client):
    response = client.get("/reviews/9999")

    assert response.status_code == 404


def test_update_review(client):
    customer = _create_customer(client)
    menu_item = _create_menu_item(client)
    created = client.post(
        "/reviews/",
        json=_sample_review(customer["customerID"], menu_item["item_id"]),
    ).json()

    response = client.put(
        f"/reviews/{created['reviewID']}",
        json={"rating": 5, "comment": "Even better on a second try"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["rating"] == 5
    assert body["comment"] == "Even better on a second try"


def test_update_review_not_found(client):
    response = client.put("/reviews/9999", json={"rating": 1})

    assert response.status_code == 404


def test_delete_review(client):
    customer = _create_customer(client)
    menu_item = _create_menu_item(client)
    created = client.post(
        "/reviews/",
        json=_sample_review(customer["customerID"], menu_item["item_id"]),
    ).json()

    delete_response = client.delete(f"/reviews/{created['reviewID']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/reviews/{created['reviewID']}")
    assert get_response.status_code == 404


def test_delete_review_not_found(client):
    response = client.delete("/reviews/9999")

    assert response.status_code == 404
