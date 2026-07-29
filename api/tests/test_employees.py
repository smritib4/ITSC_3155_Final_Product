"""Integration tests for the Employees feature (work item 4)."""


def _sample_employee(**overrides):
    payload = {
        "employee_id": "EMP-100",
        "name": "Alex Rivera",
        "role": "cashier",
    }
    payload.update(overrides)
    return payload


def test_create_employee(client):
    response = client.post("/employees/", json=_sample_employee())

    assert response.status_code == 200
    body = response.json()
    assert body["id"] is not None
    assert body["employee_id"] == "EMP-100"
    assert body["name"] == "Alex Rivera"
    assert body["role"] == "cashier"


def test_read_all_employees(client):
    client.post("/employees/", json=_sample_employee())
    client.post("/employees/", json=_sample_employee(employee_id="EMP-101"))

    response = client.get("/employees/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_one_employee(client):
    created = client.post("/employees/", json=_sample_employee()).json()

    response = client.get(f"/employees/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_read_one_employee_not_found(client):
    response = client.get("/employees/9999")

    assert response.status_code == 404


def test_update_employee(client):
    created = client.post("/employees/", json=_sample_employee()).json()

    response = client.put(f"/employees/{created['id']}", json={"role": "manager"})

    assert response.status_code == 200
    assert response.json()["role"] == "manager"


def test_update_employee_not_found(client):
    response = client.put("/employees/9999", json={"role": "manager"})

    assert response.status_code == 404


def test_delete_employee(client):
    created = client.post("/employees/", json=_sample_employee()).json()

    delete_response = client.delete(f"/employees/{created['id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/employees/{created['id']}")
    assert get_response.status_code == 404


def test_delete_employee_not_found(client):
    response = client.delete("/employees/9999")

    assert response.status_code == 404
