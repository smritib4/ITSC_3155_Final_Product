from . import (
    orders,
    order_details,
    customers,
    employees,
    inventory,
    menu_items,
    menu_item_inventory,
    payments,
    promo_codes,
    reports,
    restaurant_managers,
)


def load_routes(app):
    app.include_router(orders.router)
    app.include_router(order_details.router)
    app.include_router(customers.router)
    app.include_router(employees.router)
    app.include_router(inventory.router)
    app.include_router(menu_items.router)
    app.include_router(menu_item_inventory.router)
    app.include_router(payments.router)
    app.include_router(promo_codes.router)
    app.include_router(reports.router)
    app.include_router(restaurant_managers.router)
