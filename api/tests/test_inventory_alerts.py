"""Integration tests for the Inventory Alerts feature (work item 13 / Story 4).

`GET /inventory/alerts` returns ingredients where quantity <= minimum_quantity.
"""


def _create_ingredient(client, **overrides):
    payload = {
        "ingredient_name": "Sourdough Bread",
        "quantity": "50.00",
        "minimum_quantity": "10.00",
    }
    payload.update(overrides)
    return client.post("/inventory/", json=payload).json()


def test_alerts_returns_low_stock_ingredients(client):
    low = _create_ingredient(
        client,
        ingredient_name="Bacon",
        quantity="3.00",
        minimum_quantity="10.00",
    )
    _create_ingredient(
        client,
        ingredient_name="Lettuce",
        quantity="50.00",
        minimum_quantity="10.00",
    )

    response = client.get("/inventory/alerts")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["ingredient_id"] == low["ingredient_id"]
    assert body[0]["ingredient_name"] == "Bacon"


def test_alerts_includes_quantity_equal_to_minimum(client):
    at_minimum = _create_ingredient(
        client,
        ingredient_name="Tomato",
        quantity="5.00",
        minimum_quantity="5.00",
    )

    response = client.get("/inventory/alerts")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["ingredient_id"] == at_minimum["ingredient_id"]


def test_alerts_empty_when_all_stocked(client):
    _create_ingredient(
        client,
        ingredient_name="Cheese",
        quantity="40.00",
        minimum_quantity="10.00",
    )

    response = client.get("/inventory/alerts")

    assert response.status_code == 200
    assert response.json() == []


def test_alerts_returns_multiple_low_stock_items(client):
    _create_ingredient(client, ingredient_name="Bacon", quantity="1.00", minimum_quantity="5.00")
    _create_ingredient(client, ingredient_name="Mayo", quantity="0.00", minimum_quantity="2.00")
    _create_ingredient(client, ingredient_name="Bread", quantity="20.00", minimum_quantity="5.00")

    response = client.get("/inventory/alerts")

    assert response.status_code == 200
    names = {item["ingredient_name"] for item in response.json()}
    assert names == {"Bacon", "Mayo"}
