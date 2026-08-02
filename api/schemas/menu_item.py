from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal


class MenuItemBase(BaseModel):
    item_name: str
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    category: Optional[str] = None
    dietary_type: Optional[str] = None
    is_available: bool = True


class MenuItemCreate(MenuItemBase):
    created_by_manager_id: Optional[int] = None


class MenuItemUpdate(BaseModel):
    item_name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = None
    dietary_type: Optional[str] = None
    is_available: Optional[bool] = None
    created_by_manager_id: Optional[int] = None


class MenuItem(MenuItemBase):
    item_id: int
    created_by_manager_id: Optional[int] = None

    class Config:
        from_attributes = True
