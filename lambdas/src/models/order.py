from typing import List, Optional
from .base import Base


class Order(Base):
    order_id: str = None
    dessert_id: str = None
    quantity: int = None
    customer_first_name: str = None
    customer_last_name: str = None
    customer_email: str = None
    customer_phone: str = None
    delivery_address: str = None
    delivery_date: str = None
    delivery_time: str = None
    order_total: float = None
    order_status: str = None
    order_date: str = None
