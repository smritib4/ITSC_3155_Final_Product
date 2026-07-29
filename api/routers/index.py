from . import orders, order_details, customers, employees, inventory, menu_items, menu_item_inventory, payments


def load_routes(app):
    app.include_router(orders.router)
    app.include_router(order_details.router)
    app.include_router(customers.router)
    app.include_router(employees.router)
    app.include_router(inventory.router)
    app.include_router(menu_items.router)
    app.include_router(menu_item_inventory.router)
    app.include_router(payments.router)
