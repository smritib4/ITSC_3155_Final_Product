from fastapi import APIRouter, Depends, FastAPI, status, Response
from sqlalchemy.orm import Session
from ..controllers import menu_item_inventory as controller
from ..schemas import menu_item_inventory as schema
from ..dependencies.database import engine, get_db

router = APIRouter(
    tags=['Menu Item Inventory'],
    prefix="/menuiteminventory"
)


@router.post("/", response_model=schema.MenuItemInventoryOut)
def create(request: schema.MenuItemInventoryCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/", response_model=list[schema.MenuItemInventoryOut])
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/{item_id}/{ingredient_id}", response_model=schema.MenuItemInventoryOut)
def read_one(item_id: int, ingredient_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=item_id, ingredient_id=ingredient_id)


@router.put("/{item_id}/{ingredient_id}", response_model=schema.MenuItemInventoryOut)
def update(item_id: int, ingredient_id: int, request: schema.MenuItemInventoryUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, item_id=item_id, ingredient_id=ingredient_id, request=request)


@router.delete("/{item_id}/{ingredient_id}")
def delete(item_id: int, ingredient_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id, ingredient_id=ingredient_id)
