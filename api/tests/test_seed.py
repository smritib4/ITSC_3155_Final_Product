"""Tests for the demo seed script (work item 21)."""

from decimal import Decimal

from sqlalchemy.orm import Session

from ..dependencies.database import SessionLocal
from ..models.customer import Customer
from ..models.employee import RestaurantEmployee
from ..models.inventory import Inventory
from ..models.menu_item import MenuItem
from ..models.menu_item_inventory import MenuItemInventory
from ..models.order_details import OrderItem
from ..models.orders import Order
from ..models.payments import Payment
from ..models.promo_codes import PromoCode
from ..models.report import Report
from ..models.restaurant_manager import RestaurantManager
from ..models.review import Review
from ..seed import seed_database


def test_seed_populates_every_table():
    db: Session = SessionLocal()
    try:
        counts = seed_database(db, clear=True)

        assert counts["customers"] >= 1
        assert counts["restaurant_employees"] >= 1
        assert counts["restaurant_managers"] >= 1
        assert counts["inventory"] >= 1
        assert counts["menu_items"] >= 1
        assert counts["menu_item_inventory"] >= 1
        assert counts["promo_codes"] >= 1
        assert counts["orders"] >= 1
        assert counts["order_details"] >= 1
        assert counts["payments"] >= 1
        assert counts["reviews"] >= 1
        assert counts["reports"] >= 1

        assert db.query(Customer).count() == counts["customers"]
        assert db.query(RestaurantEmployee).count() == counts["restaurant_employees"]
        assert db.query(RestaurantManager).count() == counts["restaurant_managers"]
        assert db.query(Inventory).count() == counts["inventory"]
        assert db.query(MenuItem).count() == counts["menu_items"]
        assert db.query(MenuItemInventory).count() == counts["menu_item_inventory"]
        assert db.query(PromoCode).count() == counts["promo_codes"]
        assert db.query(Order).count() == counts["orders"]
        assert db.query(OrderItem).count() == counts["order_details"]
        assert db.query(Payment).count() == counts["payments"]
        assert db.query(Review).count() == counts["reviews"]
        assert db.query(Report).count() == counts["reports"]
    finally:
        db.close()


def test_seed_supports_demo_scenarios():
    db: Session = SessionLocal()
    try:
        seed_database(db, clear=True)

        # Low-stock alerts: tomato and avocado at/below minimum.
        low_stock = (
            db.query(Inventory)
            .filter(Inventory.quantity <= Inventory.minimum_quantity)
            .all()
        )
        low_names = {item.ingredient_name for item in low_stock}
        assert "Tomato" in low_names
        assert "Avocado" in low_names

        # Menu auto-disable demo: avocado toast is unavailable.
        avocado_toast = (
            db.query(MenuItem).filter(MenuItem.item_name == "Avocado Toast").one()
        )
        assert avocado_toast.is_available is False

        # Guest order with no customer account.
        guest_orders = db.query(Order).filter(Order.customerID.is_(None)).all()
        assert len(guest_orders) >= 1
        assert {o.orderType for o in db.query(Order).all()} >= {
            "dine-in",
            "takeout",
            "delivery",
        }

        # Active + expired/inactive promo codes.
        welcome = db.query(PromoCode).filter(PromoCode.promoCode == "WELCOME10").one()
        summer = db.query(PromoCode).filter(PromoCode.promoCode == "SUMMER5").one()
        assert welcome.active is True
        assert summer.active is False

        # Paid revenue + a non-paid payment for report filtering demos.
        statuses = {p.paymentStatus for p in db.query(Payment).all()}
        assert "paid" in statuses
        assert "pending" in statuses or "refunded" in statuses
        paid_total = sum(
            (Decimal(str(p.amount)) for p in db.query(Payment).all() if p.paymentStatus == "paid"),
            Decimal("0"),
        )
        assert paid_total > 0

        # Low-performing soup: low ratings and few orders.
        soup = db.query(MenuItem).filter(MenuItem.item_name == "Soup of the Day").one()
        soup_reviews = db.query(Review).filter(Review.item_id == soup.item_id).all()
        assert any(r.rating <= 2 for r in soup_reviews)
    finally:
        db.close()


def test_seed_is_idempotent_with_clear(client):
    """Clear+seed twice leaves a consistent row count; endpoints still read data."""
    db = SessionLocal()
    try:
        first = seed_database(db, clear=True)
        second = seed_database(db, clear=True)
        assert first == second
    finally:
        db.close()

    response = client.get("/menuitems/")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    alerts = client.get("/inventory/alerts")
    assert alerts.status_code == 200
    assert len(alerts.json()) >= 1
