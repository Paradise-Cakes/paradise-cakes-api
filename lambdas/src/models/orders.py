from typing import List, Optional
from .base import Base
from decimal import Decimal


class Order(Base):
    order_id: str = None
    dessert_id: str = None
    dessert_name: str = None
    quantity: int = None
    customer_first_name: str = None
    customer_last_name: str = None
    customer_email: str = None
    customer_phone_number: str = None
    delivery_zip_code: str = None
    delivery_address_line_1: str = None
    delivery_address_line_2: str = None
    scheduled_delivery_time: int = None
    order_total: Decimal = None
    order_status: str = None
    order_date: int = None

    description: Optional[str] = None
    custom_order: Optional[bool] = False


class PostOrderRequest(Base):
    # regular orders will have this
    dessert_id: Optional[str] = None
    dessert_name: Optional[str] = None
    quantity: Optional[int] = None
    order_total: Optional[float] = None

    # for custom orders
    description: Optional[str] = None
    custom_order: Optional[bool] = None

    # customer info
    customer_first_name: str
    customer_last_name: str
    customer_email: str
    customer_phone_number: str
    delivery_zip_code: str
    delivery_address_line_1: str
    delivery_address_line_2: str

    # delivery info
    scheduled_delivery_time: int
