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
    customer_full_name: str
    customer_email: str
    customer_phone_number: str
    delivery_zip_code: str
    delivery_address_line_1: str
    delivery_address_line_2: str
    delivery_date: str
    delivery_time: int
    order_status: str = "NEW"
    order_date: str
    order_time: int
    approved: bool = False
    custom_order: bool = False
    last_updated_at: int

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

    class Config:
        json_schema_extra = {
            "example": {
                "desserts": [
                    {
                        "dessert_id": "SCHEMA-TEST-DESSERT-ID",
                        "dessert_name": "Lemon Blueberry Cake",
                        "size": "6 inch",
                        "quantity": 2,
                    }
                ],
                "customer_first_name": "Anthony",
                "customer_last_name": "Soprano",
                "customer_email": "anthony.soprano@gmail.com",
                "customer_phone_number": "555-555-5555",
                "delivery_zip_code": "07001",
                "delivery_address_line_1": "123 Main St",
                "delivery_address_line_2": "Apt 1",
                "delivery_date": "12-12-2024",
                "delivery_time": 1734004800,
            }
        }


class PatchOrderRequest(Base):
    order_status: Optional[str] = None
    approved: Optional[bool] = None
    order_total: Optional[Decimal] = None
