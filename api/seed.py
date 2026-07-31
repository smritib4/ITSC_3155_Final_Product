"""Populate every ROS table with realistic demo sample data.

Run from the project root (uses the same SQLite/MySQL config as the app):

    python -m api.seed
    python -m api.seed --force   # wipe existing rows first (default when empty)

The seed is ordered to satisfy foreign keys and is designed so demos can exercise
inventory alerts, menu availability, date-filtered orders, promo apply, revenue
reports, and low-performing dishes without hand-entering data.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from .dependencies.database import Base, SessionLocal, engine
from .models import model_loader
from .models.customer import Customer
from .models.employee import RestaurantEmployee
from .models.inventory import Inventory
from .models.menu_item import MenuItem
from .models.menu_item_inventory import MenuItemInventory
from .models.order_details import OrderItem
from .models.orders import Order
from .models.payments import Payment
from .models.promo_codes import PromoCode
from .models.report import Report
from .models.restaurant_manager import RestaurantManager
from .models.review import Review


def _clear_all(db: Session) -> None:
    """Delete all rows in reverse dependency order so FKs stay happy."""
    for model in (
        Review,
        Payment,
        OrderItem,
        Order,
        PromoCode,
        MenuItemInventory,
        MenuItem,
        Inventory,
        Report,
        RestaurantManager,
        RestaurantEmployee,
        Customer,
    ):
        db.query(model).delete()
    db.commit()


def seed_database(db: Session, *, clear: bool = True) -> dict[str, int]:
    """Insert demo rows into every table. Returns a count per table name."""
    if clear:
        _clear_all(db)

    today = date.today()
    now = datetime.now().replace(microsecond=0)
    day = lambda n: now - timedelta(days=n)

    managers = [
        RestaurantManager(name="Alex Rivera", email="alex.rivera@ros.demo"),
        RestaurantManager(name="Jordan Lee", email="jordan.lee@ros.demo"),
    ]
    db.add_all(managers)
    db.flush()

    employees = [
        RestaurantEmployee(employee_id="E001", name="Sam Patel", role="cashier"),
        RestaurantEmployee(employee_id="E002", name="Casey Nguyen", role="cook"),
        RestaurantEmployee(employee_id="E003", name="Riley Brooks", role="delivery"),
    ]
    db.add_all(employees)
    db.flush()

    customers = [
        Customer(
            name="Taylor Morgan",
            email="taylor.morgan@example.com",
            phone="704-555-0101",
            hasAccount=True,
        ),
        Customer(
            name="Jamie Chen",
            email="jamie.chen@example.com",
            phone="704-555-0102",
            hasAccount=True,
        ),
        Customer(
            name="Guest Walker",
            email="guest.walker@example.com",
            phone="704-555-0199",
            hasAccount=False,
        ),
        Customer(
            name="Morgan Ellis",
            email="morgan.ellis@example.com",
            phone=None,
            hasAccount=True,
        ),
    ]
    db.add_all(customers)
    db.flush()

    # Low tomato/avocado stock triggers /inventory/alerts and menu auto-disable demos.
    inventory = [
        Inventory(
            ingredient_name="Sourdough Bread",
            quantity=Decimal("40.00"),
            minimum_quantity=Decimal("10.00"),
            maintained_by_manager_id=managers[0].manager_id,
        ),
        Inventory(
            ingredient_name="Turkey Breast",
            quantity=Decimal("25.00"),
            minimum_quantity=Decimal("8.00"),
            maintained_by_manager_id=managers[0].manager_id,
        ),
        Inventory(
            ingredient_name="Cheddar Cheese",
            quantity=Decimal("18.00"),
            minimum_quantity=Decimal("5.00"),
            maintained_by_manager_id=managers[0].manager_id,
        ),
        Inventory(
            ingredient_name="Tomato",
            quantity=Decimal("3.00"),
            minimum_quantity=Decimal("5.00"),
            maintained_by_manager_id=managers[1].manager_id,
        ),
        Inventory(
            ingredient_name="Lettuce",
            quantity=Decimal("12.00"),
            minimum_quantity=Decimal("4.00"),
            maintained_by_manager_id=managers[1].manager_id,
        ),
        Inventory(
            ingredient_name="Avocado",
            quantity=Decimal("0.00"),
            minimum_quantity=Decimal("2.00"),
            maintained_by_manager_id=managers[1].manager_id,
        ),
        Inventory(
            ingredient_name="Vegetable Broth",
            quantity=Decimal("30.00"),
            minimum_quantity=Decimal("6.00"),
            maintained_by_manager_id=managers[0].manager_id,
        ),
    ]
    db.add_all(inventory)
    db.flush()

    menu_items = [
        MenuItem(
            item_name="Club Sandwich",
            description="Turkey, cheddar, lettuce, tomato on sourdough",
            price=Decimal("9.50"),
            category="Sandwiches",
            dietary_type="none",
            is_available=True,
            created_by_manager_id=managers[0].manager_id,
        ),
        MenuItem(
            item_name="Turkey Melt",
            description="Warm turkey and cheddar on toasted sourdough",
            price=Decimal("8.75"),
            category="Sandwiches",
            dietary_type="none",
            is_available=True,
            created_by_manager_id=managers[0].manager_id,
        ),
        MenuItem(
            item_name="Garden Wrap",
            description="Lettuce, tomato, and cheddar in a wrap",
            price=Decimal("7.25"),
            category="Wraps",
            dietary_type="vegetarian",
            is_available=True,
            created_by_manager_id=managers[1].manager_id,
        ),
        MenuItem(
            item_name="Avocado Toast",
            description="Sourdough topped with avocado — currently out of stock",
            price=Decimal("6.50"),
            category="Sides",
            dietary_type="vegan",
            is_available=False,
            created_by_manager_id=managers[1].manager_id,
        ),
        MenuItem(
            item_name="Soup of the Day",
            description="House vegetable broth — rarely ordered",
            price=Decimal("4.25"),
            category="Soups",
            dietary_type="vegan",
            is_available=True,
            created_by_manager_id=managers[0].manager_id,
        ),
    ]
    db.add_all(menu_items)
    db.flush()

    club, melt, wrap, avocado_toast, soup = menu_items
    bread, turkey, cheese, tomato, lettuce, avocado, broth = inventory

    links = [
        MenuItemInventory(item_id=club.item_id, ingredient_id=bread.ingredient_id, quantity_required=Decimal("2.00")),
        MenuItemInventory(item_id=club.item_id, ingredient_id=turkey.ingredient_id, quantity_required=Decimal("1.00")),
        MenuItemInventory(item_id=club.item_id, ingredient_id=cheese.ingredient_id, quantity_required=Decimal("1.00")),
        MenuItemInventory(item_id=club.item_id, ingredient_id=tomato.ingredient_id, quantity_required=Decimal("1.00")),
        MenuItemInventory(item_id=club.item_id, ingredient_id=lettuce.ingredient_id, quantity_required=Decimal("1.00")),
        MenuItemInventory(item_id=melt.item_id, ingredient_id=bread.ingredient_id, quantity_required=Decimal("2.00")),
        MenuItemInventory(item_id=melt.item_id, ingredient_id=turkey.ingredient_id, quantity_required=Decimal("1.00")),
        MenuItemInventory(item_id=melt.item_id, ingredient_id=cheese.ingredient_id, quantity_required=Decimal("1.00")),
        MenuItemInventory(item_id=wrap.item_id, ingredient_id=lettuce.ingredient_id, quantity_required=Decimal("2.00")),
        MenuItemInventory(item_id=wrap.item_id, ingredient_id=tomato.ingredient_id, quantity_required=Decimal("1.00")),
        MenuItemInventory(item_id=wrap.item_id, ingredient_id=cheese.ingredient_id, quantity_required=Decimal("1.00")),
        MenuItemInventory(
            item_id=avocado_toast.item_id,
            ingredient_id=bread.ingredient_id,
            quantity_required=Decimal("1.00"),
        ),
        MenuItemInventory(
            item_id=avocado_toast.item_id,
            ingredient_id=avocado.ingredient_id,
            quantity_required=Decimal("1.00"),
        ),
        MenuItemInventory(item_id=soup.item_id, ingredient_id=broth.ingredient_id, quantity_required=Decimal("1.00")),
    ]
    db.add_all(links)

    promos = [
        PromoCode(
            promoCode="WELCOME10",
            discountAmount=Decimal("10.00"),
            expirationDate=now + timedelta(days=60),
            active=True,
            managerID=managers[0].manager_id,
        ),
        PromoCode(
            promoCode="SUMMER5",
            discountAmount=Decimal("5.00"),
            expirationDate=now - timedelta(days=10),
            active=False,
            managerID=managers[0].manager_id,
        ),
        PromoCode(
            promoCode="STAFF20",
            discountAmount=Decimal("20.00"),
            expirationDate=now + timedelta(days=30),
            active=True,
            managerID=managers[1].manager_id,
        ),
    ]
    db.add_all(promos)
    db.flush()

    orders = [
        Order(
            orderDate=day(5),
            orderStatus="completed",
            orderType="dine-in",
            totalPrice=Decimal("19.00"),
            estimatedTime=15,
            promoCode=None,
            customerID=customers[0].customerID,
            employeeID=employees[0].id,
        ),
        Order(
            orderDate=day(3),
            orderStatus="completed",
            orderType="takeout",
            totalPrice=Decimal("8.75"),
            estimatedTime=12,
            promoCode="WELCOME10",
            customerID=customers[1].customerID,
            employeeID=employees[0].id,
        ),
        Order(
            orderDate=day(2),
            orderStatus="completed",
            orderType="delivery",
            totalPrice=Decimal("16.75"),
            estimatedTime=35,
            promoCode=None,
            customerID=customers[3].customerID,
            employeeID=employees[2].id,
        ),
        # Guest order (no customer account)
        Order(
            orderDate=day(1),
            orderStatus="pending",
            orderType="takeout",
            totalPrice=Decimal("7.25"),
            estimatedTime=10,
            promoCode=None,
            customerID=None,
            employeeID=employees[1].id,
        ),
        Order(
            orderDate=day(0),
            orderStatus="completed",
            orderType="dine-in",
            totalPrice=Decimal("4.25"),
            estimatedTime=8,
            promoCode=None,
            customerID=customers[2].customerID,
            employeeID=employees[0].id,
        ),
        Order(
            orderDate=day(4),
            orderStatus="completed",
            orderType="dine-in",
            totalPrice=Decimal("9.50"),
            estimatedTime=14,
            promoCode="STAFF20",
            customerID=customers[0].customerID,
            employeeID=employees[1].id,
        ),
    ]
    db.add_all(orders)
    db.flush()

    order_items = [
        OrderItem(order_id=orders[0].orderID, item_id=club.item_id, quantity=2),
        OrderItem(order_id=orders[1].orderID, item_id=melt.item_id, quantity=1),
        OrderItem(order_id=orders[2].orderID, item_id=club.item_id, quantity=1),
        OrderItem(order_id=orders[2].orderID, item_id=wrap.item_id, quantity=1),
        OrderItem(order_id=orders[3].orderID, item_id=wrap.item_id, quantity=1),
        OrderItem(order_id=orders[4].orderID, item_id=soup.item_id, quantity=1),
        OrderItem(order_id=orders[5].orderID, item_id=club.item_id, quantity=1),
    ]
    db.add_all(order_items)

    payments = [
        Payment(
            orderID=orders[0].orderID,
            paymentMethod="card",
            paymentStatus="paid",
            amount=Decimal("19.00"),
        ),
        Payment(
            orderID=orders[1].orderID,
            paymentMethod="card",
            paymentStatus="paid",
            amount=Decimal("8.75"),
        ),
        Payment(
            orderID=orders[2].orderID,
            paymentMethod="cash",
            paymentStatus="paid",
            amount=Decimal("16.75"),
        ),
        Payment(
            orderID=orders[3].orderID,
            paymentMethod="card",
            paymentStatus="pending",
            amount=Decimal("7.25"),
        ),
        Payment(
            orderID=orders[4].orderID,
            paymentMethod="card",
            paymentStatus="paid",
            amount=Decimal("4.25"),
        ),
        Payment(
            orderID=orders[5].orderID,
            paymentMethod="card",
            paymentStatus="refunded",
            amount=Decimal("9.50"),
        ),
    ]
    db.add_all(payments)

    reviews = [
        Review(
            comment="Perfect club sandwich — will order again.",
            rating=5,
            reviewDate=today - timedelta(days=4),
            customerID=customers[0].customerID,
            item_id=club.item_id,
        ),
        Review(
            comment="Melt was tasty but a bit soggy.",
            rating=3,
            reviewDate=today - timedelta(days=2),
            customerID=customers[1].customerID,
            item_id=melt.item_id,
        ),
        Review(
            comment="Soup was bland and lukewarm.",
            rating=1,
            reviewDate=today - timedelta(days=1),
            customerID=customers[2].customerID,
            item_id=soup.item_id,
        ),
        Review(
            comment="Still disappointed with the soup.",
            rating=2,
            reviewDate=today,
            customerID=customers[3].customerID,
            item_id=soup.item_id,
        ),
        Review(
            comment="Fresh wrap, great for lunch.",
            rating=4,
            reviewDate=today - timedelta(days=2),
            customerID=customers[1].customerID,
            item_id=wrap.item_id,
        ),
    ]
    db.add_all(reviews)

    reports = [
        Report(
            report_name="Weekly Sales Summary",
            date_generated=day(1),
            generated_by_manager_id=managers[0].manager_id,
        ),
        Report(
            report_name="Low Stock Snapshot",
            date_generated=day(0),
            generated_by_manager_id=managers[1].manager_id,
        ),
    ]
    db.add_all(reports)

    db.commit()

    return {
        "customers": len(customers),
        "restaurant_employees": len(employees),
        "restaurant_managers": len(managers),
        "inventory": len(inventory),
        "menu_items": len(menu_items),
        "menu_item_inventory": len(links),
        "promo_codes": len(promos),
        "orders": len(orders),
        "order_details": len(order_items),
        "payments": len(payments),
        "reviews": len(reviews),
        "reports": len(reports),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed the ROS database with demo data.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Clear existing rows before seeding (also the default when the DB is empty).",
    )
    args = parser.parse_args(argv)

    model_loader.index()
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        already_seeded = db.query(Customer).count() > 0
        if already_seeded and not args.force:
            print(
                "Database already has data. Re-run with --force to wipe and reseed:\n"
                "  python -m api.seed --force"
            )
            return 1

        counts = seed_database(db, clear=already_seeded or args.force)
        print("Seeded demo data:")
        for table, count in counts.items():
            print(f"  {table}: {count}")
        print("Done.")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
