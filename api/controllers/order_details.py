from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response
from ..models import order_details as model
from ..models import inventory as inventory_model
from ..models import menu_item as menu_item_model
from ..models import menu_item_inventory as link_model
from ..models import orders as order_model
from ..models import promo_codes as promo_model
from sqlalchemy.exc import SQLAlchemyError


def _get_order(db: Session, order_id):
    order = db.query(order_model.Order).filter(order_model.Order.orderID == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found!")
    return order


def _get_menu_item(db: Session, item_id):
    item = db.query(menu_item_model.MenuItem).filter(
        menu_item_model.MenuItem.item_id == item_id
    ).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found!")
    return item


def adjust_inventory(db: Session, item_id, quantity_change: int):
    """Consume (positive change) or restore (negative change) a dish's ingredients.

    Story 4/6 support: placing an order draws down the ingredients its dishes are
    made from. Raises 409 listing every short ingredient if stock cannot cover the
    request, so no partial deduction is ever applied.
    """
    if quantity_change == 0:
        return

    links = db.query(link_model.MenuItemInventory).filter(
        link_model.MenuItemInventory.item_id == item_id
    ).all()

    shortages = []
    pending = []
    for link in links:
        ingredient = db.query(inventory_model.Inventory).filter(
            inventory_model.Inventory.ingredient_id == link.ingredient_id
        ).first()
        if ingredient is None:
            continue

        required = Decimal(str(link.quantity_required)) * Decimal(quantity_change)
        new_quantity = Decimal(str(ingredient.quantity)) - required
        if new_quantity < 0:
            shortages.append({
                "ingredient_id": ingredient.ingredient_id,
                "ingredient_name": ingredient.ingredient_name,
                "available": float(ingredient.quantity),
                "required": float(required),
            })
        else:
            pending.append((ingredient, new_quantity))

    if shortages:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Insufficient ingredients", "shortages": shortages},
        )

    for ingredient, new_quantity in pending:
        ingredient.quantity = new_quantity


def recalculate_order_total(db: Session, order_id):
    """Recompute an order's total from its line items, minus any applied promo.

    The server owns the price: the total is always quantity x current menu price
    summed over every line, so a client cannot dictate what an order costs.
    """
    order = db.query(order_model.Order).filter(order_model.Order.orderID == order_id).first()
    if order is None:
        return

    subtotal = Decimal("0.00")
    lines = db.query(model.OrderItem).filter(model.OrderItem.order_id == order_id).all()
    for line in lines:
        menu_item = db.query(menu_item_model.MenuItem).filter(
            menu_item_model.MenuItem.item_id == line.item_id
        ).first()
        if menu_item is None:
            continue
        subtotal += Decimal(str(menu_item.price)) * Decimal(line.quantity)

    if order.promoCode:
        promo = db.query(promo_model.PromoCode).filter(
            promo_model.PromoCode.promoCode == order.promoCode
        ).first()
        if promo is not None:
            subtotal -= Decimal(str(promo.discountAmount))

    order.totalPrice = max(Decimal("0.00"), subtotal)


def create(db: Session, request):
    try:
        _get_order(db, request.order_id)
        _get_menu_item(db, request.item_id)

        adjust_inventory(db, request.item_id, request.quantity)

        new_item = model.OrderItem(
            order_id=request.order_id,
            item_id=request.item_id,
            quantity=request.quantity,
            special_instructions=request.special_instructions,
        )
        db.add(new_item)
        db.flush()
        recalculate_order_total(db, request.order_id)
        db.commit()
        db.refresh(new_item)
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_item


def read_all(db: Session):
    try:
        result = db.query(model.OrderItem).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def read_one(db: Session, item_id):
    try:
        item = db.query(model.OrderItem).filter(model.OrderItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def update(db: Session, item_id, request):
    try:
        detail = db.query(model.OrderItem).filter(model.OrderItem.id == item_id).first()
        if not detail:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")

        update_data = request.model_dump(exclude_unset=True)
        previous_order_id = detail.order_id
        previous_item_id = detail.item_id
        previous_quantity = detail.quantity

        next_item_id = update_data.get("item_id", previous_item_id)
        next_quantity = update_data.get("quantity", previous_quantity)

        if next_item_id != previous_item_id:
            _get_menu_item(db, next_item_id)
            adjust_inventory(db, previous_item_id, -previous_quantity)
            adjust_inventory(db, next_item_id, next_quantity)
        elif next_quantity != previous_quantity:
            adjust_inventory(db, previous_item_id, next_quantity - previous_quantity)

        if "order_id" in update_data:
            _get_order(db, update_data["order_id"])

        for field, value in update_data.items():
            setattr(detail, field, value)

        db.flush()
        recalculate_order_total(db, detail.order_id)
        if detail.order_id != previous_order_id:
            recalculate_order_total(db, previous_order_id)
        db.commit()
        db.refresh(detail)
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return detail


def delete(db: Session, item_id):
    try:
        detail = db.query(model.OrderItem).filter(model.OrderItem.id == item_id).first()
        if not detail:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")

        order_id = detail.order_id
        adjust_inventory(db, detail.item_id, -detail.quantity)
        db.delete(detail)
        db.flush()
        recalculate_order_total(db, order_id)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
