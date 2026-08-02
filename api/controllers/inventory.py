from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response, Depends
from ..models import inventory as model
from ..models import restaurant_manager as manager_model
from sqlalchemy.exc import SQLAlchemyError


def _validate_manager(db: Session, manager_id):
    """Reject an unknown manager rather than silently storing a dangling id."""
    if manager_id is None:
        return
    manager = db.query(manager_model.RestaurantManager).filter(
        manager_model.RestaurantManager.manager_id == manager_id
    ).first()
    if not manager:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manager not found!")


def read_alerts(db: Session):
    """Return ingredients at or below their minimum stock level (Story 4)."""
    try:
        result = db.query(model.Inventory).filter(
            model.Inventory.quantity <= model.Inventory.minimum_quantity
        ).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def create(db: Session, request):
    _validate_manager(db, request.maintained_by_manager_id)

    new_item = model.Inventory(
        ingredient_name=request.ingredient_name,
        quantity=request.quantity,
        minimum_quantity=request.minimum_quantity,
        maintained_by_manager_id=request.maintained_by_manager_id,
    )

    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_item


def read_all(db: Session):
    try:
        result = db.query(model.Inventory).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def read_one(db: Session, item_id):
    try:
        item = db.query(model.Inventory).filter(model.Inventory.ingredient_id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def update(db: Session, item_id, request):
    try:
        item = db.query(model.Inventory).filter(model.Inventory.ingredient_id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        update_data = request.model_dump(exclude_unset=True)
        _validate_manager(db, update_data.get("maintained_by_manager_id"))
        item.update(update_data, synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    # Story 6: after inventory changes, auto-disable menu items that can no longer be made.
    from . import menu_items as menu_items_controller
    menu_items_controller.recompute_availability(db)

    return item.first()


def delete(db: Session, item_id):
    try:
        item = db.query(model.Inventory).filter(model.Inventory.ingredient_id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        item.delete(synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
