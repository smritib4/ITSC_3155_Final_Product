from . import orders, order_details, menu_item, inventory, menu_item_inventory, report, restaurant_manager, \
    customer, employee, payments, promo_codes, review
from ..dependencies.database import engine


def index():
    customer.Base.metadata.create_all(engine)
    employee.Base.metadata.create_all(engine)
    restaurant_manager.Base.metadata.create_all(engine)
    payments.Base.metadata.create_all(engine)
    promo_codes.Base.metadata.create_all(engine)
    inventory.Base.metadata.create_all(engine)
    menu_item.Base.metadata.create_all(engine)
    menu_item_inventory.Base.metadata.create_all(engine)
    orders.Base.metadata.create_all(engine)
    order_details.Base.metadata.create_all(engine)
    review.Base.metadata.create_all(engine)
    report.Base.metadata.create_all(engine)