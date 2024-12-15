import pytest

from lib import order


def test_post_v1_orders_returns_201(request_helper, function_prices, cleanup_orders):
    for dessert in order.order_record()["desserts"]:
        function_prices(dessert["dessert_id"])

    response = request_helper.post(
        "/v1/orders",
        body=order.order_record(),
    )
    cleanup_orders.append(response.json().get("order_id"))
    response.raise_for_status()

    assert response.status_code == 201
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json().get("order_total") == 10.0


def test_post_v1_orders_exceeds_order_limit_returns_400(request_helper, function_order):
    delivery_date = "12-12-2024"

    function_order(delivery_date)
    function_order(delivery_date)

    response = request_helper.post(
        "/v1/orders",
        body=order.order_record(delivery_date=delivery_date),
    )
    assert response.status_code == 400
    assert (
        response.json().get("error")
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
