from lib import order


def test_patch_v1_order_returns_200(request_helper, function_order):
    order_id = function_order().get("order_id")

    response = request_helper.patch(
        f"/v1/orders/{order_id}",
        body=order.order_record_update(),
    )
    response.raise_for_status()

    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json() == {
        "order_id": order_id,
        "customer_first_name": "John",
        "customer_last_name": "Cena",
        "customer_full_name": "John Cena",
        "customer_email": "john.cena@gmail.com",
        "customer_phone_number": "1234567890",
        "delivery_zip_code": "12345",
        "delivery_address_line_1": "123 Main St",
        "delivery_address_line_2": "Apt 1",
        "delivery_date": "01-01-2022",
        "delivery_time": 12,
        "order_status": "APPROVED",
        "order_date": "12-31-2021",
        "order_time": 12,
        "approved": True,
        "custom_order": False,
        "order_total": 50.0,
        "desserts": [
            {
                "dessert_id": "DESSERT-1",
                "dessert_name": "Chocolate Cake",
                "size": "slice",
                "quantity": 2,
            }
        ],
        "last_updated_at": response.json().get("last_updated_at"),
    }
