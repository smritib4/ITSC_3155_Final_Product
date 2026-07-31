"""Integration tests for filtering orders by date range (work item 15 / Story 9).

`GET /orders?start_date=&end_date=` filters on `orderDate`. Dates are inclusive
(start at 00:00:00, end at 23:59:59.999999).
"""


def _create_order(client, order_date=None, **overrides):
    payload = {
        "orderStatus": "pending",
        "orderType": "dine-in",
        "totalPrice": "12.50",
        "estimatedTime": 15,
        "customerID": 1,
        "employeeID": 1,
    }
    payload.update(overrides)
    created = client.post("/orders/", json=payload).json()
    if order_date is not None:
        updated = client.put(
            f"/orders/{created['orderID']}",
            json={"orderDate": f"{order_date}T12:00:00"},
        ).json()
        return updated
    return created


def test_filter_orders_by_start_and_end_date(client):
    early = _create_order(client, order_date="2026-01-10")
    mid = _create_order(client, order_date="2026-01-15")
    late = _create_order(client, order_date="2026-01-20")

    response = client.get("/orders/", params={"start_date": "2026-01-12", "end_date": "2026-01-18"})

    assert response.status_code == 200
    ids = {order["orderID"] for order in response.json()}
    assert mid["orderID"] in ids
    assert early["orderID"] not in ids
    assert late["orderID"] not in ids


def test_filter_orders_by_start_date_only(client):
    early = _create_order(client, order_date="2026-02-01")
    late = _create_order(client, order_date="2026-02-20")

    response = client.get("/orders/", params={"start_date": "2026-02-10"})

    assert response.status_code == 200
    ids = {order["orderID"] for order in response.json()}
    assert late["orderID"] in ids
    assert early["orderID"] not in ids


def test_filter_orders_by_end_date_only(client):
    early = _create_order(client, order_date="2026-03-01")
    late = _create_order(client, order_date="2026-03-20")

    response = client.get("/orders/", params={"end_date": "2026-03-10"})

    assert response.status_code == 200
    ids = {order["orderID"] for order in response.json()}
    assert early["orderID"] in ids
    assert late["orderID"] not in ids


def test_filter_orders_empty_when_none_in_range(client):
    _create_order(client, order_date="2026-04-01")

    response = client.get(
        "/orders/",
        params={"start_date": "2026-05-01", "end_date": "2026-05-31"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_filter_orders_without_params_returns_all(client):
    _create_order(client, order_date="2026-06-01")
    _create_order(client, order_date="2026-06-15")

    response = client.get("/orders/")

    assert response.status_code == 200
    assert len(response.json()) == 2
