import uuid


def dessert_record():
    return {
        "name": "Chocolate Cupcakes",
        "description": "A delicious chocolate cupcake",
        "dessert_type": "cupcake",
        "prices": [
            {"size": "single", "base_price": 2.00, "discount": 0.00},
            {"size": "dozen", "base_price": 20.00, "discount": 0.00},
        ],
        "ingredients": ["flour", "sugar", "cocoa", "butter", "eggs"],
        "images": [
            {
                "position": 1,
                "file_name": "image1.jpg",
                "file_type": "jpg",
            },
            {
                "position": 2,
                "file_name": "image2.jpg",
                "file_type": "jpg",
            },
        ],
    }


def dessert_record_no_optional_fields():
    return {
        "name": "Chocolate Cupcakes",
        "description": "A delicious chocolate cupcake",
        "dessert_type": "cupcake",
    }


def dessert_record_update():
    return {
        "prices": [
            {"size": "single", "base_price": 25.00, "discount": 0.00},
            {"size": "dozen", "base_price": 45.00, "discount": 0.00},
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
        "visible": True,
    }
