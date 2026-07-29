from . import orders, order_details, customers, employees, inventory, menu_items


def load_routes(app):
    app.include_router(orders.router)
    app.include_router(order_details.router)
    app.include_router(customers.router)
    app.include_router(employees.router)
    app.include_router(inventory.router)
    app.include_router(menu_items.router)
