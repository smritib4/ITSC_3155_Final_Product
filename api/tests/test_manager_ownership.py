"""Integration tests for manager ownership of menu items and inventory.

The UML models "restaurant_manager Creates/Manages menu_item" and
"restaurant_manager Updates inventory", so those owner ids have to be settable
through the API rather than only by writing to the database directly.
"""


def _manager(client, name="Alex Rivera", email="alex@ros.com"):
    return client.post("/managers/", json={"name": name, "email": email}).json()


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


def test_menu_item_records_creating_manager(client):
    manager = _manager(client)

    response = client.post(
        "/menuitems/", json=_menu_payload(created_by_manager_id=manager["manager_id"])
    )

    assert response.status_code == 200
    assert response.json()["created_by_manager_id"] == manager["manager_id"]


def test_menu_item_manager_is_optional(client):
    response = client.post("/menuitems/", json=_menu_payload())

    assert response.status_code == 200
    assert response.json()["created_by_manager_id"] is None


def test_menu_item_rejects_unknown_manager(client):
    response = client.post("/menuitems/", json=_menu_payload(created_by_manager_id=9999))

    assert response.status_code == 404


def test_menu_item_manager_can_be_reassigned(client):
    first = _manager(client)
    second = _manager(client, name="Jordan Lee", email="jordan@ros.com")
    item = client.post(
        "/menuitems/", json=_menu_payload(created_by_manager_id=first["manager_id"])
    ).json()

    response = client.put(
        f"/menuitems/{item['item_id']}",
        json={"created_by_manager_id": second["manager_id"]},
    )

    assert response.status_code == 200
    assert response.json()["created_by_manager_id"] == second["manager_id"]


def test_inventory_records_maintaining_manager(client):
    manager = _manager(client)

    response = client.post(
        "/inventory/", json=_inventory_payload(maintained_by_manager_id=manager["manager_id"])
    )

    assert response.status_code == 200
    assert response.json()["maintained_by_manager_id"] == manager["manager_id"]


def test_inventory_manager_is_optional(client):
    response = client.post("/inventory/", json=_inventory_payload())

    assert response.status_code == 200
    assert response.json()["maintained_by_manager_id"] is None


def test_inventory_rejects_unknown_manager(client):
    response = client.post(
        "/inventory/", json=_inventory_payload(maintained_by_manager_id=9999)
    )

    assert response.status_code == 404
