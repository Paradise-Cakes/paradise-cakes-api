def test_get_v1_orders_get_orders_by_delivery_date_returns_200(
    request_helper, function_orders
):
    order_ids = [order_id for order_id in function_orders["order_ids"]]

    response = request_helper.get("/v1/orders?delivery_date=01-01-2022")
    response.raise_for_status()

    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json() == [
        {
            "order_id": order_ids[0],
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
            "order_date": "12-31-2021",
            "order_time": 12,
            "order_status": "NEW",
            "approved": False,
            "custom_order": False,
            "order_total": 0,
            "desserts": [
                {
                    "dessert_id": "DESSERT-1",
                    "dessert_name": "Chocolate Cake",
                    "size": "slice",
                    "quantity": 2,
                }
            ],
            "last_updated_at": 1734036429,
        }
    ]


def test_get_v1_orders_get_orders_by_customer_full_name_returns_200(
    request_helper, function_orders
):
    order_ids = [order_id for order_id in function_orders["order_ids"]]

    response = request_helper.get("/v1/orders?customer_full_name=John Cena")
    response.raise_for_status()

    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json() == [
        {
            "order_id": order_ids[0],
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
            "order_date": "12-31-2021",
            "order_time": 12,
            "order_status": "NEW",
            "approved": False,
            "custom_order": False,
            "order_total": 0,
            "desserts": [
                {
                    "dessert_id": "DESSERT-1",
                    "dessert_name": "Chocolate Cake",
                    "size": "slice",
                    "quantity": 2,
                }
            ],
            "last_updated_at": 1734036429,
        }
    ]


def test_get_v1_orders_get_orders_by_order_date_returns_200(
    request_helper, function_orders
):
    order_ids = [order_id for order_id in function_orders["order_ids"]]

    response = request_helper.get("/v1/orders?order_date=12-31-2021")
    response.raise_for_status()

    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json() == [
        {
            "order_id": order_ids[0],
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
            "order_date": "12-31-2021",
            "order_time": 12,
            "order_status": "NEW",
            "approved": False,
            "custom_order": False,
            "order_total": 0,
            "desserts": [
                {
                    "dessert_id": "DESSERT-1",
                    "dessert_name": "Chocolate Cake",
                    "size": "slice",
                    "quantity": 2,
                }
            ],
            "last_updated_at": 1734036429,
        }
    ]
