from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal


class InventoryBase(BaseModel):
    ingredient_name: str
    quantity: Decimal = Field(..., ge=0)
    minimum_quantity: Decimal = Field(..., ge=0)


class InventoryCreate(InventoryBase):
    maintained_by_manager_id: Optional[int] = None


class InventoryUpdate(BaseModel):
    ingredient_name: Optional[str] = None
    quantity: Optional[Decimal] = Field(None, ge=0)
    minimum_quantity: Optional[Decimal] = Field(None, ge=0)
    maintained_by_manager_id: Optional[int] = None


class Inventory(InventoryBase):
    ingredient_id: int
    maintained_by_manager_id: Optional[int] = None

    class Config:
        from_attributes = True
