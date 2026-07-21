from typing import Optional
from pydantic import BaseModel


class OrderDetailBase(BaseModel):
    order_id: int
    item_id: int
    quantity: int = 1


class OrderDetailCreate(OrderDetailBase):
    pass


class OrderDetailUpdate(BaseModel):
    order_id: Optional[int] = None
    item_id: Optional[int] = None
    quantity: Optional[int] = None


class OrderDetail(OrderDetailBase):
    id: int

    class Config:
        from_attributes = True
