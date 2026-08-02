from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME, BOOLEAN
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    item_name = Column(String(150), nullable=True)
    description = Column(String(255))
    price = Column(DECIMAL(10, 2), nullable=False)
    category = Column(String(100))
    dietary_type = Column(String(50))
    is_available = Column(BOOLEAN, nullable=False, default=True)
    created_by_manager_id = Column(Integer, ForeignKey("restaurant_managers.manager_id", ondelete="SET NULL"))
    created_at = Column(DATETIME, nullable=False, default=datetime.now)
    updated_at = Column(DATETIME, nullable=False, default=datetime.now, onupdate=datetime.now)


    created_by = relationship("RestaurantManager", back_populates="menu_items")
    ingredient_links = relationship("MenuItemInventory", back_populates="menu_item", cascade="all, delete-orphan")
    order_links = relationship("OrderItem", back_populates="menu_item")
    reviews = relationship("Review", back_populates="menuItem", cascade="all, delete-orphan")