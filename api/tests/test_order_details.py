"""Integration tests for the Order Details feature (work item 2)."""


def _create_order(client):
    order = {
        "orderStatus": "pending",
        "orderType": "dine-in",
        "totalPrice": "9.99",
        "estimatedTime": 10,
        "customerID": 1,
        "employeeID": 1,
    }
    return client.post("/orders/", json=order).json()


def _create_menu_item(client, **overrides):
    payload = {
        "item_name": "Turkey Sandwich",
        "description": "Classic turkey on wheat",
        "price": "6.50",
        "category": "sandwich",
        "dietary_type": None,
        "is_available": True,
    }
    payload.update(overrides)
    return client.post("/menuitems/", json=payload).json()


def _sample_detail(order_id, item_id, **overrides):
    payload = {"order_id": order_id, "item_id": item_id, "quantity": 2}
    payload.update(overrides)
    return payload


def test_create_order_detail(client):
    order = _create_order(client)
    menu_item = _create_menu_item(client)

    response = client.post(
        "/orderdetails/", json=_sample_detail(order["orderID"], menu_item["item_id"])
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] is not None
    assert body["order_id"] == order["orderID"]
    assert body["item_id"] == menu_item["item_id"]
    assert body["quantity"] == 2


def test_read_all_order_details(client):
    order = _create_order(client)
    menu_item = _create_menu_item(client)
    client.post("/orderdetails/", json=_sample_detail(order["orderID"], menu_item["item_id"]))
    client.post("/orderdetails/", json=_sample_detail(order["orderID"], menu_item["item_id"], quantity=1))

    response = client.get("/orderdetails/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_one_order_detail(client):
    order = _create_order(client)
    menu_item = _create_menu_item(client)
    created = client.post(
        "/orderdetails/", json=_sample_detail(order["orderID"], menu_item["item_id"])
    ).json()

    response = client.get(f"/orderdetails/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_read_one_order_detail_not_found(client):
    response = client.get("/orderdetails/9999")

    assert response.status_code == 404


def test_update_order_detail(client):
    order = _create_order(client)
    menu_item = _create_menu_item(client)
    created = client.post(
        "/orderdetails/", json=_sample_detail(order["orderID"], menu_item["item_id"])
    ).json()

    response = client.put(f"/orderdetails/{created['id']}", json={"quantity": 5})

    assert response.status_code == 200
    assert response.json()["quantity"] == 5


def test_update_order_detail_not_found(client):
    response = client.put("/orderdetails/9999", json={"quantity": 5})

    assert response.status_code == 404


def test_delete_order_detail(client):
    order = _create_order(client)
    menu_item = _create_menu_item(client)
    created = client.post(
        "/orderdetails/", json=_sample_detail(order["orderID"], menu_item["item_id"])
    ).json()

    delete_response = client.delete(f"/orderdetails/{created['id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/orderdetails/{created['id']}")
    assert get_response.status_code == 404


def test_delete_order_detail_not_found(client):
    response = client.delete("/orderdetails/9999")

    assert response.status_code == 404


def test_create_order_detail_with_special_instructions(client):
    """Story 8: staff need to see itemized special instructions."""
    order = _create_order(client)
    menu_item = _create_menu_item(client)

    response = client.post(
        "/orderdetails/",
        json=_sample_detail(
            order["orderID"], menu_item["item_id"], special_instructions="no mayo, extra pickles"
        ),
    )

    assert response.status_code == 200
    assert response.json()["special_instructions"] == "no mayo, extra pickles"


def test_special_instructions_default_to_none(client):
    order = _create_order(client)
    menu_item = _create_menu_item(client)

    response = client.post(
        "/orderdetails/", json=_sample_detail(order["orderID"], menu_item["item_id"])
    )

    assert response.status_code == 200
    assert response.json()["special_instructions"] is None


def test_update_special_instructions(client):
    order = _create_order(client)
    menu_item = _create_menu_item(client)
    created = client.post(
        "/orderdetails/",
        json=_sample_detail(order["orderID"], menu_item["item_id"], special_instructions="no mayo"),
    ).json()

    response = client.put(
        f"/orderdetails/{created['id']}", json={"special_instructions": "gluten free bread"}
    )

    assert response.status_code == 200
    assert response.json()["special_instructions"] == "gluten free bread"


def test_special_instructions_visible_in_order_detail_list(client):
    order = _create_order(client)
    menu_item = _create_menu_item(client)
    client.post(
        "/orderdetails/",
        json=_sample_detail(order["orderID"], menu_item["item_id"], special_instructions="on the side"),
    )

    response = client.get("/orderdetails/")

    assert response.status_code == 200
    assert response.json()[0]["special_instructions"] == "on the side"


def test_zero_quantity_line_item_is_rejected(client):
    order = _create_order(client)
    menu_item = _create_menu_item(client)

    response = client.post(
        "/orderdetails/", json=_sample_detail(order["orderID"], menu_item["item_id"], quantity=0)
    )

    assert response.status_code == 422
