from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class PromoCodeBase(BaseModel):
    discountAmount: Decimal
    expirationDate: datetime
    active: bool = True


class PromoCodeCreate(PromoCodeBase):
    promoCode: str
    managerID: int


class PromoCodeUpdate(BaseModel):
    discountAmount: Optional[Decimal] = None
    expirationDate: Optional[datetime] = None
    active: Optional[bool] = None


class PromoCode(PromoCodeBase):
    promoCode: str
    managerID: int

    class Config:
        from_attributes = True


class PromoApplyRequest(BaseModel):
    promoCode: str
    orderID: int


class PromoApplyResponse(BaseModel):
    promoCode: str
    orderID: int
    originalTotal: Decimal
    discountAmount: Decimal
    newTotal: Decimal
