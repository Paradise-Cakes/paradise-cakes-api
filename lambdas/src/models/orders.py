from typing import List, Optional
from .base import Base


class Order(Base):
    order_id: str = None
    dessert_id: str = None
    dessert_name: Optional[str] = None
    quantity: int = None
    customer_first_name: str = None
    customer_last_name: str = None
    customer_email: str = None
    customer_phone_number: str = None
    customer_zip_code: str = None
    delivery_address: str = None
    scheduled_delivery_time: int = None
    order_total: float = None
    order_status: str = None
    order_date: int = None


class PostOrderRequest(Base):
    dessert_id: Optional[str] = None
    dessert_name: Optional[str] = None
    quantity: Optional[int] = None
    customer_first_name: str
    customer_last_name: str
    customer_email: str
    customer_phone_number: str
    customer_zip_code: str
    delivery_address: str
    scheduled_delivery_time: int
    order_total: float
