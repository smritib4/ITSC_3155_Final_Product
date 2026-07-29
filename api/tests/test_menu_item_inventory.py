"""Integration tests for the Menu Item <-> Inventory link feature (work item 7).

This table has a composite primary key (item_id, ingredient_id), so read_one/update/
delete all take both keys as path params: /menuiteminventory/{item_id}/{ingredient_id}.
"""


def _create_menu_item(client, **overrides):
    payload = {
        "item_name": "Club Sandwich",
        "description": "Turkey, bacon, lettuce, tomato",
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


def _sample_link(item_id, ingredient_id, **overrides):
    payload = {
        "item_id": item_id,
        "ingredient_id": ingredient_id,
        "quantity_required": "2.00",
    }
    payload.update(overrides)
    return payload


def test_create_link(client):
    menu_item = _create_menu_item(client)
    ingredient = _create_ingredient(client)

    response = client.post(
        "/menuiteminventory/",
        json=_sample_link(menu_item["item_id"], ingredient["ingredient_id"]),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["item_id"] == menu_item["item_id"]
    assert body["ingredient_id"] == ingredient["ingredient_id"]
    assert float(body["quantity_required"]) == 2.00


def test_read_all_links(client):
    menu_item = _create_menu_item(client)
    ingredient_one = _create_ingredient(client)
    ingredient_two = _create_ingredient(client, ingredient_name="Lettuce")
    client.post("/menuiteminventory/", json=_sample_link(menu_item["item_id"], ingredient_one["ingredient_id"]))
    client.post("/menuiteminventory/", json=_sample_link(menu_item["item_id"], ingredient_two["ingredient_id"]))

    response = client.get("/menuiteminventory/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_one_link(client):
    menu_item = _create_menu_item(client)
    ingredient = _create_ingredient(client)
    client.post("/menuiteminventory/", json=_sample_link(menu_item["item_id"], ingredient["ingredient_id"]))

    response = client.get(f"/menuiteminventory/{menu_item['item_id']}/{ingredient['ingredient_id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["item_id"] == menu_item["item_id"]
    assert body["ingredient_id"] == ingredient["ingredient_id"]


def test_read_one_link_not_found(client):
    response = client.get("/menuiteminventory/9999/9999")

    assert response.status_code == 404


def test_update_link(client):
    menu_item = _create_menu_item(client)
    ingredient = _create_ingredient(client)
    client.post("/menuiteminventory/", json=_sample_link(menu_item["item_id"], ingredient["ingredient_id"]))

    response = client.put(
        f"/menuiteminventory/{menu_item['item_id']}/{ingredient['ingredient_id']}",
        json={"quantity_required": "3.50"},
    )

    assert response.status_code == 200
    assert float(response.json()["quantity_required"]) == 3.50


def test_update_link_not_found(client):
    response = client.put("/menuiteminventory/9999/9999", json={"quantity_required": "3.50"})

    assert response.status_code == 404


def test_delete_link(client):
    menu_item = _create_menu_item(client)
    ingredient = _create_ingredient(client)
    client.post("/menuiteminventory/", json=_sample_link(menu_item["item_id"], ingredient["ingredient_id"]))

    delete_response = client.delete(f"/menuiteminventory/{menu_item['item_id']}/{ingredient['ingredient_id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/menuiteminventory/{menu_item['item_id']}/{ingredient['ingredient_id']}")
    assert get_response.status_code == 404


def test_delete_link_not_found(client):
    response = client.delete("/menuiteminventory/9999/9999")

    assert response.status_code == 404
