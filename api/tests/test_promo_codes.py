"""Integration tests for the Promo Codes feature (work item 9).

Promo codes use a string primary key (`promoCode`) and require a `managerID` FK.
Restaurant-managers CRUD is not built yet, so tests seed a manager directly into
the shared in-memory test DB before creating promo codes.
"""

from datetime import datetime, timedelta

from ..dependencies.database import SessionLocal
from ..models.restaurant_manager import RestaurantManager


def _create_manager(name="Promo Manager", email="promo.manager@example.com"):
    db = SessionLocal()
    try:
        manager = RestaurantManager(name=name, email=email)
        db.add(manager)
        db.commit()
        db.refresh(manager)
        return manager.manager_id
    finally:
        db.close()


def _sample_promo(manager_id, **overrides):
    payload = {
        "promoCode": "SAVE10",
        "discountAmount": "10.00",
        "expirationDate": (datetime.now() + timedelta(days=30)).isoformat(),
        "active": True,
        "managerID": manager_id,
    }
    payload.update(overrides)
    return payload


def test_create_promo_code(client):
    manager_id = _create_manager()

    response = client.post("/promocodes/", json=_sample_promo(manager_id))

    assert response.status_code == 200
    body = response.json()
    assert body["promoCode"] == "SAVE10"
    assert float(body["discountAmount"]) == 10.00
    assert body["active"] is True
    assert body["managerID"] == manager_id
    assert body["expirationDate"] is not None


def test_read_all_promo_codes(client):
    manager_id = _create_manager()
    client.post("/promocodes/", json=_sample_promo(manager_id))
    client.post(
        "/promocodes/",
        json=_sample_promo(manager_id, promoCode="SAVE20", discountAmount="20.00"),
    )

    response = client.get("/promocodes/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_one_promo_code(client):
    manager_id = _create_manager()
    client.post("/promocodes/", json=_sample_promo(manager_id))

    response = client.get("/promocodes/SAVE10")

    assert response.status_code == 200
    assert response.json()["promoCode"] == "SAVE10"


def test_read_one_promo_code_not_found(client):
    response = client.get("/promocodes/MISSING")

    assert response.status_code == 404


def test_update_promo_code(client):
    manager_id = _create_manager()
    client.post("/promocodes/", json=_sample_promo(manager_id))

    response = client.put(
        "/promocodes/SAVE10",
        json={"active": False, "discountAmount": "5.00"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["active"] is False
    assert float(body["discountAmount"]) == 5.00


def test_update_promo_code_not_found(client):
    response = client.put("/promocodes/MISSING", json={"active": False})

    assert response.status_code == 404


def test_delete_promo_code(client):
    manager_id = _create_manager()
    client.post("/promocodes/", json=_sample_promo(manager_id))

    delete_response = client.delete("/promocodes/SAVE10")
    assert delete_response.status_code == 204

    get_response = client.get("/promocodes/SAVE10")
    assert get_response.status_code == 404


def test_delete_promo_code_not_found(client):
    response = client.delete("/promocodes/MISSING")

    assert response.status_code == 404
