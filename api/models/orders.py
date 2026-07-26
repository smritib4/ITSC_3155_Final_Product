from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME, func
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base


class Order(Base):
    __tablename__ = "orders"

    orderID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    orderDate = Column(DATETIME, nullable=False, server_default=func.now())
    orderStatus = Column(String(50), nullable=False)
    orderType = Column(String(50), nullable=False)
    totalPrice = Column(DECIMAL(10, 2), nullable=False)
    estimatedTime = Column(Integer, nullable=False)

    promoCode = Column(String(50), ForeignKey("promo_codes.promoCode"), nullable=True)
    customerID = Column(Integer, ForeignKey("customers.customerID"), nullable=True)
    employeeID = Column(Integer, ForeignKey("restaurant_employees.id"), nullable=True)

    payment = relationship("Payment", back_populates="order", uselist=False)
    promo_code = relationship("PromoCode", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")
    employee = relationship("RestaurantEmployee", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    