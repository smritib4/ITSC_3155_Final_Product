"""Integration tests for the Payments feature (work item 8)."""


def _create_order(client, **overrides):
    payload = {
        "orderStatus": "pending",
        "orderType": "dine-in",
        "totalPrice": "24.99",
        "estimatedTime": 20,
        "customerID": 1,
        "employeeID": 1,
    }
    payload.update(overrides)
    return client.post("/orders/", json=payload).json()


def _sample_payment(order_id, **overrides):
    payload = {
        "orderID": order_id,
        "paymentMethod": "card",
        "paymentStatus": "paid",
        "amount": "24.99",
    }
    payload.update(overrides)
    return payload


def test_create_payment(client):
    order = _create_order(client)

    response = client.post("/payments/", json=_sample_payment(order["orderID"]))

    assert response.status_code == 200
    body = response.json()
    assert body["paymentID"] is not None
    assert body["orderID"] == order["orderID"]
    assert body["paymentMethod"] == "card"
    assert body["paymentStatus"] == "paid"
    assert float(body["amount"]) == 24.99


def test_read_all_payments(client):
    order_one = _create_order(client)
    order_two = _create_order(client)
    client.post("/payments/", json=_sample_payment(order_one["orderID"]))
    client.post("/payments/", json=_sample_payment(order_two["orderID"], paymentMethod="cash"))

    response = client.get("/payments/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_one_payment(client):
    order = _create_order(client)
    created = client.post("/payments/", json=_sample_payment(order["orderID"])).json()

    response = client.get(f"/payments/{created['paymentID']}")

    assert response.status_code == 200
    assert response.json()["paymentID"] == created["paymentID"]


def test_read_one_payment_not_found(client):
    response = client.get("/payments/9999")

    assert response.status_code == 404


def test_update_payment(client):
    order = _create_order(client)
    created = client.post("/payments/", json=_sample_payment(order["orderID"])).json()

    response = client.put(
        f"/payments/{created['paymentID']}", json={"paymentStatus": "refunded"}
    )

    assert response.status_code == 200
    assert response.json()["paymentStatus"] == "refunded"


def test_update_payment_not_found(client):
    response = client.put("/payments/9999", json={"paymentStatus": "refunded"})

    assert response.status_code == 404


def test_delete_payment(client):
    order = _create_order(client)
    created = client.post("/payments/", json=_sample_payment(order["orderID"])).json()

    delete_response = client.delete(f"/payments/{created['paymentID']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/payments/{created['paymentID']}")
    assert get_response.status_code == 404


def test_delete_payment_not_found(client):
    response = client.delete("/payments/9999")

    assert response.status_code == 404
