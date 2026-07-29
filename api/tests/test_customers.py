"""Integration tests for the Customers feature (work item 3)."""


def _sample_customer(**overrides):
    payload = {
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "phone": "704-555-0100",
        "hasAccount": True,
    }
    payload.update(overrides)
    return payload


def test_create_customer(client):
    response = client.post("/customers/", json=_sample_customer())

    assert response.status_code == 200
    body = response.json()
    assert body["customerID"] is not None
    assert body["name"] == "Jane Smith"
    assert body["email"] == "jane.smith@example.com"
    assert body["hasAccount"] is True


def test_create_customer_invalid_email_rejected(client):
    response = client.post("/customers/", json=_sample_customer(email="not-an-email"))

    assert response.status_code == 422


def test_read_all_customers(client):
    client.post("/customers/", json=_sample_customer())
    client.post("/customers/", json=_sample_customer(email="second@example.com"))

    response = client.get("/customers/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_one_customer(client):
    created = client.post("/customers/", json=_sample_customer()).json()

    response = client.get(f"/customers/{created['customerID']}")

    assert response.status_code == 200
    assert response.json()["customerID"] == created["customerID"]


def test_read_one_customer_not_found(client):
    response = client.get("/customers/9999")

    assert response.status_code == 404


def test_update_customer(client):
    created = client.post("/customers/", json=_sample_customer()).json()

    response = client.put(
        f"/customers/{created['customerID']}", json={"phone": "704-555-0199"}
    )

    assert response.status_code == 200
    assert response.json()["phone"] == "704-555-0199"


def test_update_customer_not_found(client):
    response = client.put("/customers/9999", json={"phone": "704-555-0199"})

    assert response.status_code == 404


def test_delete_customer(client):
    created = client.post("/customers/", json=_sample_customer()).json()

    delete_response = client.delete(f"/customers/{created['customerID']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/customers/{created['customerID']}")
    assert get_response.status_code == 404


def test_delete_customer_not_found(client):
    response = client.delete("/customers/9999")

    assert response.status_code == 404
