"""Integration tests for server-side order totals.

The total is always derived from the line items and any applied promo, so a
client cannot decide what its own order costs.
"""


def _menu_item(client, name="BLT", price="6.50"):
    return client.post(
        "/menuitems/",
        json={
            "item_name": name,
            "description": "test dish",
            "price": price,
            "category": "sandwich",
            "dietary_type": None,
            "is_available": True,
        },
    ).json()


def _order(client, total="0.00"):
    return client.post(
        "/orders/",
        json={
            "orderStatus": "pending",
            "orderType": "takeout",
            "totalPrice": total,
            "estimatedTime": 10,
        },
    ).json()


def _add_line(client, order_id, item_id, quantity=1):
    return client.post(
        "/orderdetails/",
        json={"order_id": order_id, "item_id": item_id, "quantity": quantity},
    ).json()


def _total(client, order_id):
    return float(client.get(f"/orders/{order_id}").json()["totalPrice"])


def test_total_is_computed_from_line_items(client):
    item = _menu_item(client, price="6.50")
    order = _order(client)

    _add_line(client, order["orderID"], item["item_id"], quantity=2)

    assert _total(client, order["orderID"]) == 13.00


def test_total_sums_multiple_dishes(client):
    sandwich = _menu_item(client, name="BLT", price="6.50")
    soup = _menu_item(client, name="Soup", price="3.25")
    order = _order(client)

    _add_line(client, order["orderID"], sandwich["item_id"], quantity=2)
    _add_line(client, order["orderID"], soup["item_id"], quantity=4)

    # (6.50 x 2) + (3.25 x 4) = 26.00
    assert _total(client, order["orderID"]) == 26.00


def test_client_supplied_total_is_overridden_by_line_items(client):
    item = _menu_item(client, price="6.50")
    order = _order(client, total="0.01")

    _add_line(client, order["orderID"], item["item_id"], quantity=2)

    assert _total(client, order["orderID"]) == 13.00


def test_total_follows_quantity_changes(client):
    item = _menu_item(client, price="6.50")
    order = _order(client)
    detail = _add_line(client, order["orderID"], item["item_id"], quantity=2)
    assert _total(client, order["orderID"]) == 13.00

    client.put(f"/orderdetails/{detail['id']}", json={"quantity": 3})

    assert _total(client, order["orderID"]) == 19.50


def test_total_drops_when_a_line_is_removed(client):
    item = _menu_item(client, price="6.50")
    order = _order(client)
    detail = _add_line(client, order["orderID"], item["item_id"], quantity=2)
    assert _total(client, order["orderID"]) == 13.00

    client.delete(f"/orderdetails/{detail['id']}")

    assert _total(client, order["orderID"]) == 0.00


def test_total_keeps_promo_discount_applied(client):
    manager = client.post(
        "/managers/", json={"name": "Alex Rivera", "email": "alex@ros.com"}
    ).json()
    client.post(
        "/promocodes/",
        json={
            "promoCode": "SAVE5",
            "discountAmount": "5.00",
            "expirationDate": "2030-01-01T00:00:00",
            "active": True,
            "managerID": manager["manager_id"],
        },
    )
    item = _menu_item(client, price="6.50")
    order = _order(client)
    client.post("/promocodes/apply", json={"promoCode": "SAVE5", "orderID": order["orderID"]})

    _add_line(client, order["orderID"], item["item_id"], quantity=2)

    # (6.50 x 2) - 5.00 discount = 8.00
    assert _total(client, order["orderID"]) == 8.00


def test_total_never_goes_negative(client):
    manager = client.post(
        "/managers/", json={"name": "Alex Rivera", "email": "alex@ros.com"}
    ).json()
    client.post(
        "/promocodes/",
        json={
            "promoCode": "BIG50",
            "discountAmount": "50.00",
            "expirationDate": "2030-01-01T00:00:00",
            "active": True,
            "managerID": manager["manager_id"],
        },
    )
    item = _menu_item(client, price="6.50")
    order = _order(client)
    client.post("/promocodes/apply", json={"promoCode": "BIG50", "orderID": order["orderID"]})

    _add_line(client, order["orderID"], item["item_id"], quantity=1)

    assert _total(client, order["orderID"]) == 0.00
