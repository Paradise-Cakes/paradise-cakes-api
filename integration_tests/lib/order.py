import random
import uuid
from datetime import datetime, timedelta, timezone


def order_record(
    delivery_date: str = None,
):
    # Generate a random delivery date within the next 30 days
    random_days = random.randint(1, 30)
    random_delivery_date = (
        datetime.now(tz=timezone.utc) + timedelta(days=random_days)
    ).strftime("%m-%d-%Y")

    return {
        "desserts": [
            {
                "dessert_id": "DESSERT-1",
                "dessert_name": "Lemon Blueberry Cake",
                "size": "slice",
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
        "delivery_date": delivery_date or random_delivery_date,
        "delivery_time": 1734004800,
    }


def order_record_with_too_many_desserts():
    return {
        "desserts": [
            {
                "dessert_id": "DESSERT-1",
                "dessert_name": "Lemon Blueberry Cake",
                "size": "slice",
                "quantity": 3,
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


def order_record_update():
    return {
        "order_status": "APPROVED",
        "approved": True,
        "order_total": 50.00,
    }
