from datetime import date, datetime, time
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response, Depends
from ..models import report as model
from ..models import payments as payment_model
from ..models import orders as order_model
from ..schemas import report as schema
from sqlalchemy.exc import SQLAlchemyError


def daily_revenue(db: Session, target_date: date | None = None):
    """Sum paid payment amounts for orders placed on the given day (Story 14)."""
    if target_date is None:
        target_date = date.today()
    start_dt = datetime.combine(target_date, time.min)
    end_dt = datetime.combine(target_date, time.max)

    try:
        total, count = (
            db.query(
                func.coalesce(func.sum(payment_model.Payment.amount), 0),
                func.count(payment_model.Payment.paymentID),
            )
            .join(order_model.Order, payment_model.Payment.orderID == order_model.Order.orderID)
            .filter(
                payment_model.Payment.paymentStatus == "paid",
                order_model.Order.orderDate >= start_dt,
                order_model.Order.orderDate <= end_dt,
            )
            .one()
        )
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return schema.DailyRevenue(
        date=target_date,
        total_revenue=Decimal(str(total)),
        payment_count=int(count),
    )


def revenue_trends(db: Session, start_date: date, end_date: date):
    """Daily paid-revenue totals over a date range (Story 15)."""
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_date must be on or after start_date",
        )

    start_dt = datetime.combine(start_date, time.min)
    end_dt = datetime.combine(end_date, time.max)
    day_col = func.date(order_model.Order.orderDate)

    try:
        rows = (
            db.query(
                day_col.label("day"),
                func.coalesce(func.sum(payment_model.Payment.amount), 0).label("total"),
                func.count(payment_model.Payment.paymentID).label("count"),
            )
            .join(order_model.Order, payment_model.Payment.orderID == order_model.Order.orderID)
            .filter(
                payment_model.Payment.paymentStatus == "paid",
                order_model.Order.orderDate >= start_dt,
                order_model.Order.orderDate <= end_dt,
            )
            .group_by(day_col)
            .order_by(day_col)
            .all()
        )
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    days = []
    grand_total = Decimal("0")
    for row in rows:
        day_value = row.day
        if isinstance(day_value, str):
            day_value = date.fromisoformat(day_value)
        elif isinstance(day_value, datetime):
            day_value = day_value.date()
        total = Decimal(str(row.total))
        grand_total += total
        days.append(
            schema.DailyRevenue(
                date=day_value,
                total_revenue=total,
                payment_count=int(row.count),
            )
        )

    return schema.RevenueTrends(
        start_date=start_date,
        end_date=end_date,
        days=days,
        grand_total=grand_total,
    )


def create(db: Session, request):
    new_item = model.Report(
        report_name=request.report_name,
        date_generated=request.date_generated,
        generated_by_manager_id=request.generated_by_manager_id,
    )

    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_item


def read_all(db: Session):
    try:
        result = db.query(model.Report).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def read_one(db: Session, item_id):
    try:
        item = db.query(model.Report).filter(model.Report.report_id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def update(db: Session, item_id, request):
    try:
        item = db.query(model.Report).filter(model.Report.report_id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        update_data = request.dict(exclude_unset=True)
        item.update(update_data, synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item.first()


def delete(db: Session, item_id):
    try:
        item = db.query(model.Report).filter(model.Report.report_id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        item.delete(synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
