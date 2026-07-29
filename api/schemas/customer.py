from pydantic import BaseModel, EmailStr
from typing import Optional

class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    hasAccount: bool = False

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    hasAccount: Optional[bool] = None

class CustomerResponse(CustomerBase):
    customerID: int

    class Config:
        from_attributes = True 