"""Integration tests for ingredient deduction when dishes are ordered.

Placing a line item draws its recipe's ingredients down from inventory, and
removing or shrinking that line puts them back.
"""


def _ingredient(client, name="Tomato", quantity="10", minimum="2"):
    return client.post(
        "/inventory/",
        json={"ingredient_name": name, "quantity": quantity, "minimum_quantity": minimum},
    ).json()


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


def _link(client, item_id, ingredient_id, quantity_required):
    return client.post(
        "/menuiteminventory/",
        json={
            "item_id": item_id,
            "ingredient_id": ingredient_id,
            "quantity_required": quantity_required,
        },
    ).json()


def _order(client):
    return client.post(
        "/orders/",
        json={
            "orderStatus": "pending",
            "orderType": "takeout",
            "totalPrice": "0.00",
            "estimatedTime": 10,
        },
    ).json()


def _stock(client, ingredient_id):
    return float(client.get(f"/inventory/{ingredient_id}").json()["quantity"])


def test_ordering_deducts_ingredients(client):
    ingredient = _ingredient(client, quantity="10")
    item = _menu_item(client)
    _link(client, item["item_id"], ingredient["ingredient_id"], "2")
    order = _order(client)

    response = client.post(
        "/orderdetails/",
        json={"order_id": order["orderID"], "item_id": item["item_id"], "quantity": 3},
    )

    assert response.status_code == 200
    # 10 in stock - (2 required x 3 ordered) = 4
    assert _stock(client, ingredient["ingredient_id"]) == 4.0


def test_insufficient_stock_is_rejected(client):
    ingredient = _ingredient(client, quantity="3")
    item = _menu_item(client)
    _link(client, item["item_id"], ingredient["ingredient_id"], "2")
    order = _order(client)

    response = client.post(
        "/orderdetails/",
        json={"order_id": order["orderID"], "item_id": item["item_id"], "quantity": 5},
    )

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["message"] == "Insufficient ingredients"
    assert detail["shortages"][0]["ingredient_name"] == "Tomato"
    # Nothing was deducted, so the order can still be fulfilled at a smaller size.
    assert _stock(client, ingredient["ingredient_id"]) == 3.0


def test_no_partial_deduction_when_one_ingredient_is_short(client):
    plenty = _ingredient(client, name="Bread", quantity="100")
    scarce = _ingredient(client, name="Avocado", quantity="1")
    item = _menu_item(client)
    _link(client, item["item_id"], plenty["ingredient_id"], "1")
    _link(client, item["item_id"], scarce["ingredient_id"], "1")
    order = _order(client)

    response = client.post(
        "/orderdetails/",
        json={"order_id": order["orderID"], "item_id": item["item_id"], "quantity": 5},
    )

    assert response.status_code == 409
    assert _stock(client, plenty["ingredient_id"]) == 100.0
    assert _stock(client, scarce["ingredient_id"]) == 1.0


def test_deleting_a_line_restores_ingredients(client):
    ingredient = _ingredient(client, quantity="10")
    item = _menu_item(client)
    _link(client, item["item_id"], ingredient["ingredient_id"], "2")
    order = _order(client)
    detail = client.post(
        "/orderdetails/",
        json={"order_id": order["orderID"], "item_id": item["item_id"], "quantity": 3},
    ).json()
    assert _stock(client, ingredient["ingredient_id"]) == 4.0

    client.delete(f"/orderdetails/{detail['id']}")

    assert _stock(client, ingredient["ingredient_id"]) == 10.0


def test_increasing_quantity_deducts_only_the_difference(client):
    ingredient = _ingredient(client, quantity="10")
    item = _menu_item(client)
    _link(client, item["item_id"], ingredient["ingredient_id"], "2")
    order = _order(client)
    detail = client.post(
        "/orderdetails/",
        json={"order_id": order["orderID"], "item_id": item["item_id"], "quantity": 2},
    ).json()
    assert _stock(client, ingredient["ingredient_id"]) == 6.0

    client.put(f"/orderdetails/{detail['id']}", json={"quantity": 4})

    # Two more units consumed, not four.
    assert _stock(client, ingredient["ingredient_id"]) == 2.0


def test_reducing_quantity_returns_ingredients(client):
    ingredient = _ingredient(client, quantity="10")
    item = _menu_item(client)
    _link(client, item["item_id"], ingredient["ingredient_id"], "2")
    order = _order(client)
    detail = client.post(
        "/orderdetails/",
        json={"order_id": order["orderID"], "item_id": item["item_id"], "quantity": 4},
    ).json()
    assert _stock(client, ingredient["ingredient_id"]) == 2.0

    client.put(f"/orderdetails/{detail['id']}", json={"quantity": 1})

    assert _stock(client, ingredient["ingredient_id"]) == 8.0


def test_dish_without_a_recipe_does_not_touch_inventory(client):
    ingredient = _ingredient(client, quantity="10")
    item = _menu_item(client)
    order = _order(client)

    response = client.post(
        "/orderdetails/",
        json={"order_id": order["orderID"], "item_id": item["item_id"], "quantity": 3},
    )

    assert response.status_code == 200
    assert _stock(client, ingredient["ingredient_id"]) == 10.0


def test_line_item_for_unknown_menu_item_is_rejected(client):
    order = _order(client)

    response = client.post(
        "/orderdetails/",
        json={"order_id": order["orderID"], "item_id": 9999, "quantity": 1},
    )

    assert response.status_code == 404


def test_line_item_for_unknown_order_is_rejected(client):
    item = _menu_item(client)

    response = client.post(
        "/orderdetails/",
        json={"order_id": 9999, "item_id": item["item_id"], "quantity": 1},
    )

    assert response.status_code == 404
