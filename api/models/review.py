from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from ..dependencies.database import Base

class Review(Base):
    __tablename__ = 'reviews'

    reviewID = Column(Integer, primary_key = True, autoincrement = True)
    comment = Column(String(250), nullable = True)
    rating = Column(Integer, nullable = False)
    reviewDate = Column(Date, default = date.today)

    customerID = Column(Integer, ForeignKey('customers.customerID', ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey('menu_items.item_id', ondelete="CASCADE"), nullable=False)

    customer = relationship("Customer", back_populates="reviews")
    menuItem = relationship("MenuItem", back_populates="reviews")