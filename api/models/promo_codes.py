from sqlalchemy import Boolean, Column, DECIMAL, String, DATETIME, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class PromoCode(Base):
    __tablename__ = "promo_codes"

    promoCode = Column(String(50), primary_key=True, index=True)
    discountAmount = Column(DECIMAL(10, 2), nullable=False)
    expirationDate = Column(DATETIME, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    managerID = Column(Integer, ForeignKey("restaurant_managers.manager_id"), nullable=False)

    orders = relationship("Order", back_populates="promo_code")
    manager = relationship("RestaurantManager", back_populates="promoCodes")