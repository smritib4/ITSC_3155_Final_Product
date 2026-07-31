from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal


class ReportBase(BaseModel):
    report_name: str
    date_generated: datetime


class ReportCreate(ReportBase):
    generated_by_manager_id: Optional[int] = None


class ReportUpdate(BaseModel):
    report_name: Optional[str] = None
    date_generated: Optional[datetime] = None


class Report(ReportBase):
    report_id: int
    generated_by_manager_id: Optional[int] = None

    class Config:
        from_attributes = True


class DailyRevenue(BaseModel):
    date: date
    total_revenue: Decimal
    payment_count: int


class RevenueTrends(BaseModel):
    start_date: date
    end_date: date
    days: List[DailyRevenue]
    grand_total: Decimal


class LowPerformingDish(BaseModel):
    item_id: int
    item_name: Optional[str] = None
    average_rating: Optional[float] = None
    review_count: int
    order_count: int
    complaint_comments: List[str]