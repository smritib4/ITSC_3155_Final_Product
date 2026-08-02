from datetime import date, datetime, time
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response, Depends
from ..models import report as model
from ..models import payments as payment_model
from ..models import orders as order_model
from ..models import menu_item as menu_model
from ..models import review as review_model
from ..models import order_details as order_details_model
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


def low_performing(
    db: Session,
    max_avg_rating: float = 2.5,
    max_order_count: int = 2,
):
    """Return dishes with low average ratings and/or low order counts (Story 10).

    A dish is included when:
    - it has reviews and average_rating <= max_avg_rating, or
    - its total ordered quantity <= max_order_count.

    Complaint comments are review comments with rating <= 2.
    """
    try:
        rating_subq = (
            db.query(
                review_model.Review.item_id.label("item_id"),
                func.avg(review_model.Review.rating).label("avg_rating"),
                func.count(review_model.Review.reviewID).label("review_count"),
            )
            .group_by(review_model.Review.item_id)
            .subquery()
        )
        orders_subq = (
            db.query(
                order_details_model.OrderItem.item_id.label("item_id"),
                func.coalesce(func.sum(order_details_model.OrderItem.quantity), 0).label(
                    "order_count"
                ),
            )
            .group_by(order_details_model.OrderItem.item_id)
            .subquery()
        )

        rows = (
            db.query(
                menu_model.MenuItem,
                rating_subq.c.avg_rating,
                rating_subq.c.review_count,
                orders_subq.c.order_count,
            )
            .outerjoin(rating_subq, menu_model.MenuItem.item_id == rating_subq.c.item_id)
            .outerjoin(orders_subq, menu_model.MenuItem.item_id == orders_subq.c.item_id)
            .all()
        )

        results = []
        for item, avg_rating, review_count, order_count in rows:
            avg = float(avg_rating) if avg_rating is not None else None
            rc = int(review_count or 0)
            oc = int(order_count or 0)
            low_rating = avg is not None and avg <= max_avg_rating
            low_orders = oc <= max_order_count
            if not (low_rating or low_orders):
                continue

            complaint_rows = (
                db.query(review_model.Review.comment)
                .filter(
                    review_model.Review.item_id == item.item_id,
                    review_model.Review.rating <= 2,
                    review_model.Review.comment.isnot(None),
                    review_model.Review.comment != "",
                )
                .all()
            )
            results.append(
                schema.LowPerformingDish(
                    item_id=item.item_id,
                    item_name=item.item_name,
                    average_rating=avg,
                    review_count=rc,
                    order_count=oc,
                    complaint_comments=[c[0] for c in complaint_rows],
                )
            )

        results.sort(
            key=lambda d: (
                d.average_rating if d.average_rating is not None else 999,
                d.order_count,
            )
        )
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return results


def create(db: Session, request):
    fields = {
        "report_name": request.report_name,
        "generated_by_manager_id": request.generated_by_manager_id,
    }
    # Leave the column unset when the client omits it so the model default applies.
    if request.date_generated is not None:
        fields["date_generated"] = request.date_generated

    new_item = model.Report(**fields)

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
