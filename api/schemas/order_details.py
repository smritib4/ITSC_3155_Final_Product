from typing import Optional
from pydantic import BaseModel, Field


class OrderDetailBase(BaseModel):
    order_id: int
    item_id: int
    quantity: int = Field(1, ge=1)
    special_instructions: Optional[str] = None


class OrderDetailCreate(OrderDetailBase):
    pass


class OrderDetailUpdate(BaseModel):
    order_id: Optional[int] = None
    item_id: Optional[int] = None
    quantity: Optional[int] = Field(None, ge=1)
    special_instructions: Optional[str] = None


class OrderDetail(OrderDetailBase):
    id: int

    class Config:
        from_attributes = True
