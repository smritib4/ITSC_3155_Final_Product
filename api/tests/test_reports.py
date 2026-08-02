"""Integration tests for the Reports feature (work item 10)."""

from datetime import datetime


def _sample_report(**overrides):
    payload = {
        "report_name": "Daily Sales Summary",
        "date_generated": datetime.now().isoformat(),
        "generated_by_manager_id": None,
    }
    payload.update(overrides)
    return payload


def test_create_report(client):
    response = client.post("/reports/", json=_sample_report())

    assert response.status_code == 200
    body = response.json()
    assert body["report_id"] is not None
    assert body["report_name"] == "Daily Sales Summary"
    assert body["date_generated"] is not None
    assert body["generated_by_manager_id"] is None


def test_create_report_without_date_generated(client):
    """date_generated is stamped by the model when the client omits it."""
    response = client.post("/reports/", json={"report_name": "Daily Sales Summary"})

    assert response.status_code == 200
    body = response.json()
    assert body["report_id"] is not None
    assert body["date_generated"] is not None


def test_read_all_reports(client):
    client.post("/reports/", json=_sample_report())
    client.post("/reports/", json=_sample_report(report_name="Weekly Trends"))

    response = client.get("/reports/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_one_report(client):
    created = client.post("/reports/", json=_sample_report()).json()

    response = client.get(f"/reports/{created['report_id']}")

    assert response.status_code == 200
    assert response.json()["report_id"] == created["report_id"]


def test_read_one_report_not_found(client):
    response = client.get("/reports/9999")

    assert response.status_code == 404


def test_update_report(client):
    created = client.post("/reports/", json=_sample_report()).json()

    response = client.put(
        f"/reports/{created['report_id']}",
        json={"report_name": "Updated Sales Summary"},
    )

    assert response.status_code == 200
    assert response.json()["report_name"] == "Updated Sales Summary"


def test_update_report_not_found(client):
    response = client.put("/reports/9999", json={"report_name": "Missing"})

    assert response.status_code == 404


def test_delete_report(client):
    created = client.post("/reports/", json=_sample_report()).json()

    delete_response = client.delete(f"/reports/{created['report_id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/reports/{created['report_id']}")
    assert get_response.status_code == 404


def test_delete_report_not_found(client):
    response = client.delete("/reports/9999")

    assert response.status_code == 404
