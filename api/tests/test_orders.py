"""Integration tests for the Orders feature (work item 1).

Exercises the real /orders endpoints end-to-end (router -> controller ->
model) against an isolated in-memory database, per test_orders.py fixture
`client` defined in conftest.py.
"""


def _sample_order(**overrides):
    payload = {
        "orderStatus": "pending",
        "orderType": "dine-in",
        "totalPrice": "19.99",
        "estimatedTime": 15,
        "promoCode": None,
        "customerID": 1,
        "employeeID": 1,
    }
    payload.update(overrides)
    return payload


def test_create_order(client):
    response = client.post("/orders/", json=_sample_order())

    assert response.status_code == 200
    body = response.json()
    assert body["orderID"] is not None
    assert body["orderStatus"] == "pending"
    assert body["orderType"] == "dine-in"
    assert float(body["totalPrice"]) == 19.99
    assert body["customerID"] == 1
    assert body["employeeID"] == 1


def test_read_all_orders(client):
    client.post("/orders/", json=_sample_order())
    client.post("/orders/", json=_sample_order(orderType="takeout"))

    response = client.get("/orders/")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2


def test_read_one_order(client):
    created = client.post("/orders/", json=_sample_order()).json()

    response = client.get(f"/orders/{created['orderID']}")

    assert response.status_code == 200
    assert response.json()["orderID"] == created["orderID"]


def test_read_one_order_not_found(client):
    response = client.get("/orders/9999")

    assert response.status_code == 404


def test_update_order(client):
    created = client.post("/orders/", json=_sample_order()).json()

    response = client.put(
        f"/orders/{created['orderID']}",
        json={"orderStatus": "completed"},
    )

    assert response.status_code == 200
    assert response.json()["orderStatus"] == "completed"


def test_update_order_not_found(client):
    response = client.put("/orders/9999", json={"orderStatus": "completed"})

    assert response.status_code == 404


def test_delete_order(client):
    created = client.post("/orders/", json=_sample_order()).json()

    delete_response = client.delete(f"/orders/{created['orderID']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/orders/{created['orderID']}")
    assert get_response.status_code == 404


def test_delete_order_not_found(client):
    response = client.delete("/orders/9999")

    assert response.status_code == 404
