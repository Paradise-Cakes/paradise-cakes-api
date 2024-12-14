from lib import dessert


def test_post_v1_desserts_returns_201(request_helper, cleanup_desserts):
    response = request_helper.post(
        "/v1/desserts",
        body=dessert.dessert_record(),
    )
    dessert_id = response.json().get("dessert_id")
    cleanup_desserts.append({"dessert_id": dessert_id})

    response.raise_for_status()

    assert response.status_code == 201
    assert response.headers.get("Content-Type") == "application/json"


def test_post_v1_desserts_no_optional_fields_201(request_helper, cleanup_desserts):
    response = request_helper.post(
        "/v1/desserts",
        body=dessert.dessert_record_no_optional_fields(),
    )
    dessert_id = response.json().get("dessert_id")
    cleanup_desserts.append({"dessert_id": dessert_id})
    response.raise_for_status()

    assert response.status_code == 201
    assert response.headers.get("Content-Type") == "application/json"
