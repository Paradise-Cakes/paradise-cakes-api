from datetime import datetime, timezone, timedelta
import random
import uuid


def order_record(
    delivery_date: str = None,
):
    # Generate a random delivery date within the next 30 days
    random_days = random.randint(1, 30)
    random_delivery_date = (
        datetime.now(tz=timezone.utc) + timedelta(days=random_days)
    ).strftime("%Y-%m-%d")

    return {
        "desserts": [
            {
                "dessert_id": f"INTEGRATION_TEST-{uuid.uuid4()}",
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
        "delivery_date": delivery_date or random_delivery_date,
        "delivery_time": 1711108800,
    }
