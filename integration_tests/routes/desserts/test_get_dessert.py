def test_get_v1_desserts_get_dessert_returns_200(
    request_helper, function_dessert, cleanup_desserts
):
    dessert_id = function_dessert.get("dessert_id")

    response = request_helper.get(f"/v1/desserts/{dessert_id}")
    cleanup_desserts.append({"dessert_id": dessert_id})
    response.raise_for_status()

    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json() == {
        "dessert_id": dessert_id,
        "name": "Chocolate Cake",
        "description": "its a chocolate cake",
        "dessert_type": "cake",
        "created_at": response.json().get("created_at"),
        "last_updated_at": response.json().get("last_updated_at"),
        "visible": False,
        "prices": [
            {
                "dessert_id": dessert_id,
                "size": "slice",
                "base_price": 5.00,
                "discount": 0.00,
            },
            {
                "dessert_id": dessert_id,
                "size": "whole",
                "base_price": 40.00,
                "discount": 0.00,
            },
        ],
        "ingredients": ["flour", "sugar", "cocoa", "butter", "eggs"],
        "images": [
            {
                "image_id": "IMAGE-1",
                "url": "https://example.com/image1.jpg",
                "upload_url": "https://example.com/upload-url",
                "position": 1,
                "file_name": "image1.jpg",
                "file_type": "jpg",
            },
            {
                "image_id": "IMAGE-2",
                "url": "https://example.com/image2.jpg",
                "upload_url": "https://example.com/upload-url",
                "position": 2,
                "file_name": "image2.jpg",
                "file_type": "jpg",
            },
        ],
    }


def test_get_v1_desserts_get_dessert_returns_404(request_helper):
    response = request_helper.get("/v1/desserts/i-dont-exist")

    assert response.status_code == 404
    assert response.headers.get("Content-Type") == "application/json"
    assert response.json() == {"detail": "Dessert not found"}
