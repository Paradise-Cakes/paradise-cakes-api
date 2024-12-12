from lib import order


def test_post_v1_orders_returns_201(
    request_helper, cleanup_orders, function_prices, cleanup_prices
):
    price_records = function_prices("DESSERT-1")["records"]

    response = request_helper.post(
        "/v1/orders",
        body=order.order_record(),
    )
    response.raise_for_status()

    order_id = response.json().get("order_id")
    delivery_date = response.json().get("delivery_date")
    cleanup_orders.append({"order_id": order_id, "delivery_date": delivery_date})
    cleanup_prices.extend(price_records)

    assert response.status_code == 201
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json().get("order_total") == 10.0


def test_post_v1_orders_exceeds_order_limit_returns_400(request_helper, cleanup_orders):
    delivery_date = "12-12-2024"

    response_1 = request_helper.post(
        "/v1/orders",
        body=order.order_record(delivery_date=delivery_date),
    )
    response_1.raise_for_status()
    assert response_1.status_code == 201
    cleanup_orders.append(
        {
            "order_id": response_1.json().get("order_id"),
        }
    )

    response_2 = request_helper.post(
        "/v1/orders",
        body=order.order_record(delivery_date=delivery_date),
    )
    response_2.raise_for_status()
    assert response_2.status_code == 201
    cleanup_orders.append(
        {
            "order_id": response_2.json().get("order_id"),
        }
    )

    response_3 = request_helper.post(
        "/v1/orders",
        body=order.order_record(delivery_date=delivery_date),
    )
    assert response_3.status_code == 400
    assert (
        response_3.json().get("error")
        == f"Order limit exceeded for date: {delivery_date}. Max orders: 2"
    )


def test_post_v1_orders_exceeds_dessert_quantity_limit_returns_400(request_helper):
    response = request_helper.post(
        "/v1/orders",
        body=order.order_record_with_too_many_desserts(),
    )

    assert response.status_code == 400
    assert (
        response.json().get("error")
        == "Dessert quantity limit exceeded for dessert: DESSERT-1. Max quantity: 2"
    )
