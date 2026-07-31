from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response, Depends
from ..models import promo_codes as model
from ..models import orders as order_model
from ..schemas import promo_codes as schema
from sqlalchemy.exc import SQLAlchemyError


def apply(db: Session, request):
    """Validate an active, non-expired promo and apply its discount to an order (Story 28)."""
    try:
        promo = db.query(model.PromoCode).filter(
            model.PromoCode.promoCode == request.promoCode
        ).first()
        if not promo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promo code not found!")

        if not promo.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Promo code is not active",
            )

        if promo.expirationDate < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Promo code has expired",
            )

        order = db.query(order_model.Order).filter(
            order_model.Order.orderID == request.orderID
        ).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found!")

        if order.promoCode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A promo code has already been applied to this order",
            )

        original_total = Decimal(str(order.totalPrice))
        discount = Decimal(str(promo.discountAmount))
        new_total = max(Decimal("0.00"), original_total - discount)

        order.totalPrice = new_total
        order.promoCode = promo.promoCode
        db.commit()
        db.refresh(order)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return schema.PromoApplyResponse(
        promoCode=promo.promoCode,
        orderID=order.orderID,
        originalTotal=original_total,
        discountAmount=discount,
        newTotal=new_total,
    )


def create(db: Session, request):
    new_item = model.PromoCode(
        promoCode=request.promoCode,
        discountAmount=request.discountAmount,
        expirationDate=request.expirationDate,
        active=request.active,
        managerID=request.managerID,
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
        result = db.query(model.PromoCode).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def read_one(db: Session, promo_code):
    try:
        item = db.query(model.PromoCode).filter(model.PromoCode.promoCode == promo_code).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def update(db: Session, promo_code, request):
    try:
        item = db.query(model.PromoCode).filter(model.PromoCode.promoCode == promo_code)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        update_data = request.dict(exclude_unset=True)
        item.update(update_data, synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item.first()


def delete(db: Session, promo_code):
    try:
        item = db.query(model.PromoCode).filter(model.PromoCode.promoCode == promo_code)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        item.delete(synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
