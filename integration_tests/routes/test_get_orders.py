def test_get_v1_desserts_get_desserts_returns_200(
    request_helper, function_orders, cleanup_orders
):
  order_ids = [order.get("order_id") for order in function_orders]

  response = request_helper.get("/v1/orders?delivery_date=2022-01-01")
  response.raise_for_status()
  cleanup_orders.extend([{"order_id": order_id} for order_id in order_ids])

  assert response.status_code == 200
  assert response.headers.get("Content-Type") == "application/json"
  assert response.json() == [
    {
      "order_id": order_ids[0],
      "customer_first_name": "John",
      "customer_last_name": "Cena",
      "customer_full_name": "John Cena",
      "customer_email": "john.cena@gmail.com",
      "customer_phone": "123-456-7890",
      "delivery_zip_code": "12345",
      "delivery_address_line_1": "123 Main St",
      "delivery_address_line_2": "Apt 1",
      "delivery_date": "2022-01-01",
      "delivery_time": 12,
      "order_date": "2021-12-01",
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
          "quantity": 2
        }
      ]
    }
  ]
