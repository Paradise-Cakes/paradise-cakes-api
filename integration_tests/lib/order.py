from datetime import datetime, timezone, timedelta
import random


def order_record(
    dessert_id: str = "integration_test",
    custom_order: bool = False,
    delivery_date: str = None,
):
    # Generate a random delivery date within the next 30 days
    random_days = random.randint(1, 30)
    random_delivery_date = (
        datetime.now(tz=timezone.utc) + timedelta(days=random_days)
    ).strftime("%Y-%m-%d")

    return {
        "dessert_id": dessert_id,
        "dessert_name": "Chocolate Cake",
        "quantity": 1,
        "customer_first_name": "Anthony",
        "customer_last_name": "Viera",
        "customer_email": "av@gmail.com",
        "customer_phone_number": "2108601043",
        "delivery_zip_code": "76177",
        "delivery_address_line_1": "3239 Winding Shore Ln",
        "delivery_address_line_2": "APT 2",
        "delivery_date": delivery_date if delivery_date else random_delivery_date,
        "delivery_time": int(datetime.now(tz=timezone.utc).timestamp()),
        "order_total": 0.00,
        "description": "integration_test",
        "custom_order": custom_order,
    }
