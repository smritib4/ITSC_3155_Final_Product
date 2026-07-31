"""Integration tests for menu auto-disable (work item 14 / Story 6).

Disables menu items when any linked ingredient has quantity < quantity_required.
Triggered by POST /menuitems/recompute-availability and on inventory PUT.
"""


def _create_menu_item(client, **overrides):
    payload = {
        "item_name": "Club Sandwich",
        "description": "Turkey club",
        "price": "8.50",
        "category": "sandwich",
        "dietary_type": None,
        "is_available": True,
    }
    payload.update(overrides)
    return client.post("/menuitems/", json=payload).json()


def _create_ingredient(client, **overrides):
    payload = {
        "ingredient_name": "Bacon",
        "quantity": "20.00",
        "minimum_quantity": "5.00",
    }
    payload.update(overrides)
    return client.post("/inventory/", json=payload).json()


def _link(client, item_id, ingredient_id, quantity_required="2.00"):
    return client.post(
        "/menuiteminventory/",
        json={
            "item_id": item_id,
            "ingredient_id": ingredient_id,
            "quantity_required": quantity_required,
        },
    ).json()


def test_recompute_disables_menu_item_with_depleted_ingredient(client):
    menu_item = _create_menu_item(client)
    ingredient = _create_ingredient(client, quantity="0.00")
    _link(client, menu_item["item_id"], ingredient["ingredient_id"], "2.00")

    response = client.post("/menuitems/recompute-availability")

    assert response.status_code == 200
    disabled = response.json()
    assert len(disabled) == 1
    assert disabled[0]["item_id"] == menu_item["item_id"]
    assert disabled[0]["is_available"] is False

    fetched = client.get(f"/menuitems/{menu_item['item_id']}").json()
    assert fetched["is_available"] is False


def test_recompute_keeps_available_when_stock_is_sufficient(client):
    menu_item = _create_menu_item(client)
    ingredient = _create_ingredient(client, quantity="10.00")
    _link(client, menu_item["item_id"], ingredient["ingredient_id"], "2.00")

    response = client.post("/menuitems/recompute-availability")

    assert response.status_code == 200
    assert response.json() == []

    fetched = client.get(f"/menuitems/{menu_item['item_id']}").json()
    assert fetched["is_available"] is True


def test_recompute_skips_items_without_ingredient_links(client):
    menu_item = _create_menu_item(client, item_name="Drink")

    response = client.post("/menuitems/recompute-availability")

    assert response.status_code == 200
    assert response.json() == []

    fetched = client.get(f"/menuitems/{menu_item['item_id']}").json()
    assert fetched["is_available"] is True


def test_inventory_update_hooks_auto_disable(client):
    menu_item = _create_menu_item(client)
    ingredient = _create_ingredient(client, quantity="10.00")
    _link(client, menu_item["item_id"], ingredient["ingredient_id"], "2.00")

    client.put(
        f"/inventory/{ingredient['ingredient_id']}",
        json={"quantity": "1.00"},
    )

    fetched = client.get(f"/menuitems/{menu_item['item_id']}").json()
    assert fetched["is_available"] is False
