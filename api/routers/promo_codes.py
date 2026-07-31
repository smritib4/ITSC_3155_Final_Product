from fastapi import APIRouter, Depends, FastAPI, status, Response
from sqlalchemy.orm import Session
from ..controllers import promo_codes as controller
from ..schemas import promo_codes as schema
from ..dependencies.database import engine, get_db

router = APIRouter(
    tags=['Promo Codes'],
    prefix="/promocodes"
)


@router.post("/", response_model=schema.PromoCode)
def create(request: schema.PromoCodeCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/", response_model=list[schema.PromoCode])
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/{promo_code}", response_model=schema.PromoCode)
def read_one(promo_code: str, db: Session = Depends(get_db)):
    return controller.read_one(db, promo_code=promo_code)


@router.put("/{promo_code}", response_model=schema.PromoCode)
def update(promo_code: str, request: schema.PromoCodeUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, promo_code=promo_code, request=request)


@router.delete("/{promo_code}")
def delete(promo_code: str, db: Session = Depends(get_db)):
    return controller.delete(db=db, promo_code=promo_code)
