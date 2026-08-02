"""Integration tests for order tracking (Story 22)."""


def _order(client, **overrides):
    payload = {
        "orderStatus": "pending",
        "orderType": "delivery",
        "totalPrice": "12.00",
        "estimatedTime": 25,
    }
    payload.update(overrides)
    return client.post("/orders/", json=payload).json()


def test_track_order_returns_status(client):
    order = _order(client)

    response = client.get(f"/orders/{order['orderID']}/tracking")

    assert response.status_code == 200
    body = response.json()
    assert body["orderID"] == order["orderID"]
    assert body["orderStatus"] == "pending"
    assert body["orderType"] == "delivery"
    assert body["estimatedTime"] == 25


def test_track_order_reflects_status_updates(client):
    order = _order(client)
    client.put(f"/orders/{order['orderID']}", json={"orderStatus": "out for delivery"})

    response = client.get(f"/orders/{order['orderID']}/tracking")

    assert response.status_code == 200
    assert response.json()["orderStatus"] == "out for delivery"


def test_track_order_reflects_estimated_time_updates(client):
    order = _order(client)
    client.put(f"/orders/{order['orderID']}", json={"estimatedTime": 5})

    response = client.get(f"/orders/{order['orderID']}/tracking")

    assert response.json()["estimatedTime"] == 5


def test_track_order_not_found(client):
    response = client.get("/orders/9999/tracking")

    assert response.status_code == 404
