from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status, Response, Depends
from ..models import menu_item as model
from ..models import menu_item_inventory as link_model
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


def recompute_availability(db: Session):
    """Set is_available=False when any linked ingredient cannot cover quantity_required.

    Story 6: auto-disable out-of-stock menu items. Only disables; does not re-enable
    items that were manually marked unavailable.
    """
    try:
        menu_items = (
            db.query(model.MenuItem)
            .options(
                joinedload(model.MenuItem.ingredient_links).joinedload(
                    link_model.MenuItemInventory.ingredient
                )
            )
            .all()
        )
        disabled = []
        for item in menu_items:
            if not item.ingredient_links:
                continue
            depleted = any(
                link.ingredient is not None
                and link.ingredient.quantity < link.quantity_required
                for link in item.ingredient_links
            )
            if depleted and item.is_available:
                item.is_available = False
                disabled.append(item)
        db.commit()
        for item in disabled:
            db.refresh(item)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return disabled


def create(db: Session, request):
    _validate_manager(db, request.created_by_manager_id)

    new_item = model.MenuItem(
        item_name=request.item_name,
        description=request.description,
        price=request.price,
        category=request.category,
        dietary_type=request.dietary_type,
        is_available=request.is_available,
        created_by_manager_id=request.created_by_manager_id,
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


def read_all(db: Session, dietary_type: str | None = None, q: str | None = None):
    """Return menu items, optionally filtered by dietary type and/or keyword (Stories 24, 25)."""
    try:
        query = db.query(model.MenuItem)
        if dietary_type is not None:
            query = query.filter(model.MenuItem.dietary_type == dietary_type)
        if q is not None and q.strip():
            pattern = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    model.MenuItem.item_name.ilike(pattern),
                    model.MenuItem.description.ilike(pattern),
                )
            )
        result = query.all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def read_one(db: Session, item_id):
    try:
        item = db.query(model.MenuItem).filter(model.MenuItem.item_id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def update(db: Session, item_id, request):
    try:
        item = db.query(model.MenuItem).filter(model.MenuItem.item_id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        update_data = request.model_dump(exclude_unset=True)
        _validate_manager(db, update_data.get("created_by_manager_id"))
        item.update(update_data, synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item.first()


def delete(db: Session, item_id):
    try:
        item = db.query(model.MenuItem).filter(model.MenuItem.item_id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        item.delete(synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
