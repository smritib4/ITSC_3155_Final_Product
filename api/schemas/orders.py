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
    # Starting total for an order that has no line items yet. Once line items
    # exist the server recomputes this from menu prices, so a client cannot
    # decide what an order costs.
    totalPrice: Decimal = Decimal("0.00")
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


class OrderTracking(BaseModel):
    """Customer-facing order status view (Story 22)."""

    orderID: int
    orderStatus: str
    orderType: str
    estimatedTime: int
    orderDate: Optional[datetime] = None
    totalPrice: Decimal

    class Config:
        from_attributes = True
