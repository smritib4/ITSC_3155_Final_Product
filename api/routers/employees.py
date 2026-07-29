from fastapi import APIRouter, Depends, FastAPI, status, Response
from sqlalchemy.orm import Session
from ..controllers import employees as controller
from ..schemas import employee as schema
from ..dependencies.database import engine, get_db

router = APIRouter(
    tags=['Employees'],
    prefix="/employees"
)


@router.post("/", response_model=schema.RestaurantEmployeeSchema)
def create(request: schema.EmployeeCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/", response_model=list[schema.RestaurantEmployeeSchema])
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/{item_id}", response_model=schema.RestaurantEmployeeSchema)
def read_one(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=item_id)


@router.put("/{item_id}", response_model=schema.RestaurantEmployeeSchema)
def update(item_id: int, request: schema.EmployeeUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, request=request, item_id=item_id)


@router.delete("/{item_id}")
def delete(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)
