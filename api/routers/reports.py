from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, FastAPI, status, Response, Query
from sqlalchemy.orm import Session
from ..controllers import reports as controller
from ..schemas import report as schema
from ..dependencies.database import engine, get_db

router = APIRouter(
    tags=['Reports'],
    prefix="/reports"
)


@router.post("/", response_model=schema.Report)
def create(request: schema.ReportCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/", response_model=list[schema.Report])
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)


# Declared before /{item_id} so these paths are not captured as integer ids.
@router.get("/revenue/daily", response_model=schema.DailyRevenue)
def daily_revenue(
    report_date: Optional[date] = Query(None, alias="date"),
    db: Session = Depends(get_db),
):
    return controller.daily_revenue(db, target_date=report_date)


@router.get("/revenue/trends", response_model=schema.RevenueTrends)
def revenue_trends(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
):
    return controller.revenue_trends(db, start_date=start_date, end_date=end_date)


@router.get("/low-performing", response_model=list[schema.LowPerformingDish])
def low_performing(
    max_avg_rating: float = Query(2.5),
    max_order_count: int = Query(2),
    db: Session = Depends(get_db),
):
    return controller.low_performing(
        db, max_avg_rating=max_avg_rating, max_order_count=max_order_count
    )


@router.get("/{item_id}", response_model=schema.Report)
def read_one(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=item_id)


@router.put("/{item_id}", response_model=schema.Report)
def update(item_id: int, request: schema.ReportUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, request=request, item_id=item_id)


@router.delete("/{item_id}")
def delete(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)
