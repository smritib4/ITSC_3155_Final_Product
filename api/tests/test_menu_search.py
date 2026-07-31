"""Integration tests for menu search/filter (work item 16 / Stories 24, 25).

`GET /menuitems?dietary_type=` filters by dietary type.
`GET /menuitems?q=` keyword-searches item_name and description (case-insensitive).
"""


def _create_item(client, **overrides):
    payload = {
        "item_name": "Veggie Wrap",
        "description": "Grilled veggies in a spinach wrap",
        "price": "7.25",
        "category": "wrap",
        "dietary_type": "vegetarian",
        "is_available": True,
    }
    payload.update(overrides)
    return client.post("/menuitems/", json=payload).json()


def test_filter_by_dietary_type(client):
    veg = _create_item(client, item_name="Veggie Wrap", dietary_type="vegetarian")
    _create_item(
        client,
        item_name="Turkey Club",
        description="Turkey sandwich",
        dietary_type=None,
        category="sandwich",
    )

    response = client.get("/menuitems/", params={"dietary_type": "vegetarian"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["item_id"] == veg["item_id"]


def test_keyword_search_matches_item_name(client):
    match = _create_item(client, item_name="Spicy Chili Bowl", description="Hot chili")
    _create_item(client, item_name="Veggie Wrap", description="Spinach wrap")

    response = client.get("/menuitems/", params={"q": "chili"})

    assert response.status_code == 200
    ids = {item["item_id"] for item in response.json()}
    assert match["item_id"] in ids
    assert len(ids) == 1


def test_keyword_search_matches_description(client):
    match = _create_item(
        client,
        item_name="House Special",
        description="Served with avocado spread",
    )
    _create_item(client, item_name="Veggie Wrap", description="Spinach wrap")

    response = client.get("/menuitems/", params={"q": "avocado"})

    assert response.status_code == 200
    ids = {item["item_id"] for item in response.json()}
    assert match["item_id"] in ids
    assert len(ids) == 1


def test_combined_dietary_type_and_keyword(client):
    match = _create_item(
        client,
        item_name="Tofu Stir Fry",
        description="Crispy tofu with veggies",
        dietary_type="vegan",
    )
    _create_item(
        client,
        item_name="Tofu Scramble",
        description="Breakfast tofu",
        dietary_type="vegetarian",
    )
    _create_item(
        client,
        item_name="Steak Plate",
        description="Grilled steak",
        dietary_type=None,
    )

    response = client.get("/menuitems/", params={"dietary_type": "vegan", "q": "tofu"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["item_id"] == match["item_id"]


def test_search_empty_when_no_matches(client):
    _create_item(client)

    response = client.get("/menuitems/", params={"q": "nonexistent-dish"})

    assert response.status_code == 200
    assert response.json() == []


def test_search_without_params_returns_all(client):
    _create_item(client, item_name="Item A")
    _create_item(client, item_name="Item B", dietary_type="vegan")

    response = client.get("/menuitems/")

    assert response.status_code == 200
    assert len(response.json()) == 2
