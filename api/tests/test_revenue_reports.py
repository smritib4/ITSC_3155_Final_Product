"""Integration tests for revenue reports (work item 17 / Stories 14, 15).

Revenue is summed from paid payments joined to orders by orderDate
(payments have no date column of their own).
"""


def _create_paid_order(client, order_date, amount="10.00", status="paid"):
    order = client.post(
        "/orders/",
        json={
            "orderStatus": "completed",
            "orderType": "dine-in",
            "totalPrice": amount,
            "estimatedTime": 15,
            "customerID": 1,
            "employeeID": 1,
        },
    ).json()
    client.put(f"/orders/{order['orderID']}", json={"orderDate": f"{order_date}T12:00:00"})
    payment = client.post(
        "/payments/",
        json={
            "orderID": order["orderID"],
            "paymentMethod": "card",
            "paymentStatus": status,
            "amount": amount,
        },
    ).json()
    return order, payment


def test_daily_revenue_for_specific_date(client):
    _create_paid_order(client, "2026-07-01", amount="10.00")
    _create_paid_order(client, "2026-07-01", amount="5.50")
    _create_paid_order(client, "2026-07-02", amount="20.00")

    response = client.get("/reports/revenue/daily", params={"date": "2026-07-01"})

    assert response.status_code == 200
    body = response.json()
    assert body["date"] == "2026-07-01"
    assert float(body["total_revenue"]) == 15.50
    assert body["payment_count"] == 2


def test_daily_revenue_excludes_non_paid_payments(client):
    _create_paid_order(client, "2026-07-03", amount="10.00", status="paid")
    _create_paid_order(client, "2026-07-03", amount="9.00", status="refunded")

    response = client.get("/reports/revenue/daily", params={"date": "2026-07-03"})

    assert response.status_code == 200
    body = response.json()
    assert float(body["total_revenue"]) == 10.00
    assert body["payment_count"] == 1


def test_daily_revenue_zero_when_no_payments(client):
    response = client.get("/reports/revenue/daily", params={"date": "2026-01-01"})

    assert response.status_code == 200
    body = response.json()
    assert float(body["total_revenue"]) == 0
    assert body["payment_count"] == 0


def test_revenue_trends_over_range(client):
    _create_paid_order(client, "2026-08-01", amount="10.00")
    _create_paid_order(client, "2026-08-02", amount="7.00")
    _create_paid_order(client, "2026-08-02", amount="3.00")
    _create_paid_order(client, "2026-08-05", amount="4.00")

    response = client.get(
        "/reports/revenue/trends",
        params={"start_date": "2026-08-01", "end_date": "2026-08-03"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["start_date"] == "2026-08-01"
    assert body["end_date"] == "2026-08-03"
    assert float(body["grand_total"]) == 20.00
    days = {day["date"]: day for day in body["days"]}
    assert float(days["2026-08-01"]["total_revenue"]) == 10.00
    assert float(days["2026-08-02"]["total_revenue"]) == 10.00
    assert "2026-08-05" not in days


def test_revenue_trends_rejects_inverted_range(client):
    response = client.get(
        "/reports/revenue/trends",
        params={"start_date": "2026-08-10", "end_date": "2026-08-01"},
    )

    assert response.status_code == 400
