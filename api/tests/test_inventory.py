"""Integration tests for the Inventory feature (work item 5)."""


def _sample_ingredient(**overrides):
    payload = {
        "ingredient_name": "Sourdough Bread",
        "quantity": "50.00",
        "minimum_quantity": "10.00",
    }
    payload.update(overrides)
    return payload


def test_create_ingredient(client):
    response = client.post("/inventory/", json=_sample_ingredient())

    assert response.status_code == 200
    body = response.json()
    assert body["ingredient_id"] is not None
    assert body["ingredient_name"] == "Sourdough Bread"
    assert float(body["quantity"]) == 50.00
    assert float(body["minimum_quantity"]) == 10.00


def test_read_all_ingredients(client):
    client.post("/inventory/", json=_sample_ingredient())
    client.post("/inventory/", json=_sample_ingredient(ingredient_name="Swiss Cheese"))

    response = client.get("/inventory/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_one_ingredient(client):
    created = client.post("/inventory/", json=_sample_ingredient()).json()

    response = client.get(f"/inventory/{created['ingredient_id']}")

    assert response.status_code == 200
    assert response.json()["ingredient_id"] == created["ingredient_id"]


def test_read_one_ingredient_not_found(client):
    response = client.get("/inventory/9999")

    assert response.status_code == 404


def test_update_ingredient(client):
    created = client.post("/inventory/", json=_sample_ingredient()).json()

    response = client.put(
        f"/inventory/{created['ingredient_id']}", json={"quantity": "5.00"}
    )

    assert response.status_code == 200
    assert float(response.json()["quantity"]) == 5.00


def test_update_ingredient_not_found(client):
    response = client.put("/inventory/9999", json={"quantity": "5.00"})

    assert response.status_code == 404


def test_delete_ingredient(client):
    created = client.post("/inventory/", json=_sample_ingredient()).json()

    delete_response = client.delete(f"/inventory/{created['ingredient_id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/inventory/{created['ingredient_id']}")
    assert get_response.status_code == 404


def test_delete_ingredient_not_found(client):
    response = client.delete("/inventory/9999")

    assert response.status_code == 404
