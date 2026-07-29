"""Integration tests for the Menu Items feature (work item 6)."""


def _sample_menu_item(**overrides):
    payload = {
        "item_name": "Veggie Wrap",
        "description": "Grilled veggies in a spinach wrap",
        "price": "7.25",
        "category": "wrap",
        "dietary_type": "vegetarian",
        "is_available": True,
    }
    payload.update(overrides)
    return payload


def test_create_menu_item(client):
    response = client.post("/menuitems/", json=_sample_menu_item())

    assert response.status_code == 200
    body = response.json()
    assert body["item_id"] is not None
    assert body["item_name"] == "Veggie Wrap"
    assert float(body["price"]) == 7.25
    assert body["is_available"] is True


def test_read_all_menu_items(client):
    client.post("/menuitems/", json=_sample_menu_item())
    client.post("/menuitems/", json=_sample_menu_item(item_name="Turkey Club"))

    response = client.get("/menuitems/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_one_menu_item(client):
    created = client.post("/menuitems/", json=_sample_menu_item()).json()

    response = client.get(f"/menuitems/{created['item_id']}")

    assert response.status_code == 200
    assert response.json()["item_id"] == created["item_id"]


def test_read_one_menu_item_not_found(client):
    response = client.get("/menuitems/9999")

    assert response.status_code == 404


def test_update_menu_item(client):
    created = client.post("/menuitems/", json=_sample_menu_item()).json()

    response = client.put(
        f"/menuitems/{created['item_id']}", json={"is_available": False}
    )

    assert response.status_code == 200
    assert response.json()["is_available"] is False


def test_update_menu_item_not_found(client):
    response = client.put("/menuitems/9999", json={"is_available": False})

    assert response.status_code == 404


def test_delete_menu_item(client):
    created = client.post("/menuitems/", json=_sample_menu_item()).json()

    delete_response = client.delete(f"/menuitems/{created['item_id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/menuitems/{created['item_id']}")
    assert get_response.status_code == 404


def test_delete_menu_item_not_found(client):
    response = client.delete("/menuitems/9999")

    assert response.status_code == 404
