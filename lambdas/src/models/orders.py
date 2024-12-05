from decimal import Decimal
from typing import List, Optional

from .base import Base


class Dessert(Base):
    dessert_id: str
    dessert_name: str
    size: str
    quantity: int


class Order(Base):
    # every order has these attributes
    order_id: str
    customer_first_name: str
    customer_last_name: str
    customer_email: str
    customer_phone_number: str
    delivery_zip_code: str
    delivery_address_line_1: str
    delivery_address_line_2: str
    delivery_date: str
    delivery_time: int
    order_status: str = "NEW"
    order_date: int
    approved: bool = False
    custom_order: bool = False

    # optional fields if it's a custom order request
    order_total: Optional[Decimal] = None  # calculated in the backend
    description: Optional[str] = None
    desserts: Optional[List[Dessert]] = []


class PostOrderRequest(Base):
    desserts: Optional[List[Dessert]] = []

    # for custom orders
    description: Optional[str] = None
    custom_order: Optional[bool] = False

    # customer info
    customer_first_name: str
    customer_last_name: str
    customer_email: str
    customer_phone_number: str

    # delivery info
    delivery_zip_code: str
    delivery_address_line_1: str
    delivery_address_line_2: str
    delivery_date: str
    delivery_time: int
