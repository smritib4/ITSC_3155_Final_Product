from sqlalchemy import Column, ForeignKey, Integer, DECIMAL
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class MenuItemInventory(Base):
    __tablename__ = "menu_item_inventory"

    item_id = Column(Integer, ForeignKey("menu_items.item_id", ondelete="CASCADE"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("inventory.ingredient_id", ondelete="CASCADE"), primary_key=True)
    quantity_required = Column(DECIMAL(10, 2), nullable=False, default=0)

    menu_item = relationship("MenuItem", back_populates="ingredient_links")
    ingredient = relationship("Inventory", back_populates="menu_items_links")