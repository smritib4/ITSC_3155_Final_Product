from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class OrderBase(BaseModel):
    orderStatus: str
    orderType: str
    totalPrice: Decimal
    estimatedTime: int
    promoCode: Optional[str] = None


class OrderCreate(OrderBase):
    # Nullable to support guest checkout (no customer account).
    customerID: Optional[int] = None
    employeeID: Optional[int] = None


class OrderUpdate(BaseModel):
    orderDate: Optional[datetime] = None
    orderStatus: Optional[str] = None
    orderType: Optional[str] = None
    totalPrice: Optional[Decimal] = None
    estimatedTime: Optional[int] = None
    promoCode: Optional[str] = None
    customerID: Optional[int] = None
    employeeID: Optional[int] = None


class Order(OrderBase):
    orderID: int
    orderDate: Optional[datetime] = None
    customerID: Optional[int] = None
    employeeID: Optional[int] = None

    class Config:
        from_attributes = True
