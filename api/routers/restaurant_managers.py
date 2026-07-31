from fastapi import APIRouter, Depends, FastAPI, status, Response
from sqlalchemy.orm import Session
from ..controllers import restaurant_managers as controller
from ..schemas import restaurant_manager as schema
from ..dependencies.database import engine, get_db

router = APIRouter(
    tags=['Restaurant Managers'],
    prefix="/managers"
)


@router.post("/", response_model=schema.RestaurantManager)
def create(request: schema.RestaurantManagerCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/", response_model=list[schema.RestaurantManager])
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/{item_id}", response_model=schema.RestaurantManager)
def read_one(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=item_id)


@router.put("/{item_id}", response_model=schema.RestaurantManager)
def update(item_id: int, request: schema.RestaurantManagerUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, request=request, item_id=item_id)


@router.delete("/{item_id}")
def delete(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)
