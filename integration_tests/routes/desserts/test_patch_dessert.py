from lib import dessert


def test_patch_v1_dessert_returns_200(
    request_helper, function_dessert, cleanup_desserts
):
    dessert_id = function_dessert.get("dessert_id")

    response = request_helper.patch(
        f"/v1/desserts/{dessert_id}",
        body=dessert.dessert_record_update(),
    )
    response.raise_for_status()
    cleanup_desserts.append({"dessert_id": dessert_id})

    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json() == {
        "dessert_id": dessert_id,
        "name": "Chocolate Cake",
        "description": "its a chocolate cake",
        "dessert_type": "cake",
        "created_at": response.json().get("created_at"),
        "last_updated_at": response.json().get("last_updated_at"),
        "visible": True,
        "prices": [
            {
                "dessert_id": dessert_id,
                "size": "single",
                "base_price": 25.00,
                "discount": 0.00,
            },
            {
                "dessert_id": dessert_id,
                "size": "dozen",
                "base_price": 45.00,
                "discount": 0.00,
            },
        ],
        "ingredients": ["eggs"],
        "images": [
            {
                "position": 2,
                "file_name": "image1.jpg",
                "file_type": "jpg",
            },
            {
                "position": 1,
                "file_name": "image2.jpg",
                "file_type": "jpg",
            },
        ],
    }
