"""Integration tests rejecting nonsensical prices and stock levels."""


def _menu_payload(**overrides):
    payload = {
        "item_name": "BLT",
        "description": "classic",
        "price": "6.50",
        "category": "sandwich",
        "dietary_type": None,
        "is_available": True,
    }
    payload.update(overrides)
    return payload


def _inventory_payload(**overrides):
    payload = {"ingredient_name": "Tomato", "quantity": "10.00", "minimum_quantity": "2.00"}
    payload.update(overrides)
    return payload


def test_negative_price_is_rejected(client):
    response = client.post("/menuitems/", json=_menu_payload(price="-10.00"))

    assert response.status_code == 422


def test_zero_price_is_rejected(client):
    response = client.post("/menuitems/", json=_menu_payload(price="0.00"))

    assert response.status_code == 422


def test_negative_price_on_update_is_rejected(client):
    item = client.post("/menuitems/", json=_menu_payload()).json()

    response = client.put(f"/menuitems/{item['item_id']}", json={"price": "-1.00"})

    assert response.status_code == 422


def test_price_above_ninety_nine_is_accepted(client):
    """The price column is wide enough for catering-sized totals."""
    response = client.post("/menuitems/", json=_menu_payload(price="150.00"))

    assert response.status_code == 200
    assert float(response.json()["price"]) == 150.00


def test_negative_stock_is_rejected(client):
    response = client.post("/inventory/", json=_inventory_payload(quantity="-5.00"))

    assert response.status_code == 422


def test_negative_minimum_stock_is_rejected(client):
    response = client.post("/inventory/", json=_inventory_payload(minimum_quantity="-1.00"))

    assert response.status_code == 422


def test_zero_stock_is_allowed(client):
    """Zero is a legitimate stock level: it is what drives low-stock alerts."""
    response = client.post("/inventory/", json=_inventory_payload(quantity="0.00"))

    assert response.status_code == 200
    assert float(response.json()["quantity"]) == 0.00


def test_negative_stock_on_update_is_rejected(client):
    ingredient = client.post("/inventory/", json=_inventory_payload()).json()

    response = client.put(
        f"/inventory/{ingredient['ingredient_id']}", json={"quantity": "-3.00"}
    )

    assert response.status_code == 422
