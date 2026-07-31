"""Integration tests for applying a promo code at checkout (work item 18 / Story 28)."""

from datetime import datetime, timedelta


def _create_manager(client):
    return client.post(
        "/managers/",
        json={"name": "Promo Apply Manager", "email": "promo.apply@example.com"},
    ).json()


def _create_promo(client, manager_id, **overrides):
    payload = {
        "promoCode": "SAVE10",
        "discountAmount": "10.00",
        "expirationDate": (datetime.now() + timedelta(days=30)).isoformat(),
        "active": True,
        "managerID": manager_id,
    }
    payload.update(overrides)
    return client.post("/promocodes/", json=payload).json()


def _create_order(client, total="25.00"):
    return client.post(
        "/orders/",
        json={
            "orderStatus": "pending",
            "orderType": "takeout",
            "totalPrice": total,
            "estimatedTime": 20,
            "customerID": 1,
            "employeeID": 1,
        },
    ).json()


def test_apply_promo_updates_order_total(client):
    manager = _create_manager(client)
    _create_promo(client, manager["manager_id"])
    order = _create_order(client, total="25.00")

    response = client.post(
        "/promocodes/apply",
        json={"promoCode": "SAVE10", "orderID": order["orderID"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["promoCode"] == "SAVE10"
    assert body["orderID"] == order["orderID"]
    assert float(body["originalTotal"]) == 25.00
    assert float(body["discountAmount"]) == 10.00
    assert float(body["newTotal"]) == 15.00

    updated = client.get(f"/orders/{order['orderID']}").json()
    assert float(updated["totalPrice"]) == 15.00
    assert updated["promoCode"] == "SAVE10"


def test_apply_promo_caps_new_total_at_zero(client):
    manager = _create_manager(client)
    _create_promo(client, manager["manager_id"], discountAmount="50.00")
    order = _create_order(client, total="20.00")

    response = client.post(
        "/promocodes/apply",
        json={"promoCode": "SAVE10", "orderID": order["orderID"]},
    )

    assert response.status_code == 200
    assert float(response.json()["newTotal"]) == 0.00


def test_apply_inactive_promo_rejected(client):
    manager = _create_manager(client)
    _create_promo(client, manager["manager_id"], active=False)
    order = _create_order(client)

    response = client.post(
        "/promocodes/apply",
        json={"promoCode": "SAVE10", "orderID": order["orderID"]},
    )

    assert response.status_code == 400
    assert "not active" in response.json()["detail"]


def test_apply_expired_promo_rejected(client):
    manager = _create_manager(client)
    _create_promo(
        client,
        manager["manager_id"],
        expirationDate=(datetime.now() - timedelta(days=1)).isoformat(),
    )
    order = _create_order(client)

    response = client.post(
        "/promocodes/apply",
        json={"promoCode": "SAVE10", "orderID": order["orderID"]},
    )

    assert response.status_code == 400
    assert "expired" in response.json()["detail"]


def test_apply_missing_promo_not_found(client):
    order = _create_order(client)

    response = client.post(
        "/promocodes/apply",
        json={"promoCode": "MISSING", "orderID": order["orderID"]},
    )

    assert response.status_code == 404


def test_apply_missing_order_not_found(client):
    manager = _create_manager(client)
    _create_promo(client, manager["manager_id"])

    response = client.post(
        "/promocodes/apply",
        json={"promoCode": "SAVE10", "orderID": 9999},
    )

    assert response.status_code == 404


def test_apply_rejects_second_promo_on_same_order(client):
    manager = _create_manager(client)
    _create_promo(client, manager["manager_id"])
    _create_promo(
        client,
        manager["manager_id"],
        promoCode="SAVE5",
        discountAmount="5.00",
    )
    order = _create_order(client, total="30.00")

    first = client.post(
        "/promocodes/apply",
        json={"promoCode": "SAVE10", "orderID": order["orderID"]},
    )
    assert first.status_code == 200

    second = client.post(
        "/promocodes/apply",
        json={"promoCode": "SAVE5", "orderID": order["orderID"]},
    )
    assert second.status_code == 400
    assert "already been applied" in second.json()["detail"]
