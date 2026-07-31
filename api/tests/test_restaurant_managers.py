"""Integration tests for the Restaurant Managers feature (work item 11)."""


def _sample_manager(**overrides):
    payload = {
        "name": "Sam Manager",
        "email": "sam.manager@example.com",
    }
    payload.update(overrides)
    return payload


def test_create_manager(client):
    response = client.post("/managers/", json=_sample_manager())

    assert response.status_code == 200
    body = response.json()
    assert body["manager_id"] is not None
    assert body["name"] == "Sam Manager"
    assert body["email"] == "sam.manager@example.com"


def test_create_manager_invalid_email_rejected(client):
    response = client.post("/managers/", json=_sample_manager(email="not-an-email"))

    assert response.status_code == 422


def test_read_all_managers(client):
    client.post("/managers/", json=_sample_manager())
    client.post(
        "/managers/",
        json=_sample_manager(name="Alex Manager", email="alex.manager@example.com"),
    )

    response = client.get("/managers/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_one_manager(client):
    created = client.post("/managers/", json=_sample_manager()).json()

    response = client.get(f"/managers/{created['manager_id']}")

    assert response.status_code == 200
    assert response.json()["manager_id"] == created["manager_id"]


def test_read_one_manager_not_found(client):
    response = client.get("/managers/9999")

    assert response.status_code == 404


def test_update_manager(client):
    created = client.post("/managers/", json=_sample_manager()).json()

    response = client.put(
        f"/managers/{created['manager_id']}",
        json={"email": "sam.updated@example.com"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "sam.updated@example.com"


def test_update_manager_not_found(client):
    response = client.put("/managers/9999", json={"email": "missing@example.com"})

    assert response.status_code == 404


def test_delete_manager(client):
    created = client.post("/managers/", json=_sample_manager()).json()

    delete_response = client.delete(f"/managers/{created['manager_id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/managers/{created['manager_id']}")
    assert get_response.status_code == 404


def test_delete_manager_not_found(client):
    response = client.delete("/managers/9999")

    assert response.status_code == 404
