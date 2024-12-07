def test_delete_v1_desserts_delete_dessert_returns_200(
    request_helper, function_dessert
):
    dessert_id = function_dessert.get("dessert_id")

    response = request_helper.delete(f"/v1/desserts/{dessert_id}")
    response.raise_for_status()

    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json() == {}

    # Confirm dessert is deleted
    response = request_helper.get(f"/v1/desserts/{dessert_id}")
    assert response.status_code == 404
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json() == {"detail": "Dessert not found"}


def test_delete_v1_desserts_delete_dessert_returns_404(request_helper):
    response = request_helper.delete("/v1/desserts/i-dont-exist")

    assert response.status_code == 404
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json() == {"detail": "Dessert not found"}
