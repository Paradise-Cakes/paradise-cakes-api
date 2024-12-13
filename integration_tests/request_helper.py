import requests


class RequestHelper:
    def __init__(self, url: str, headers: dict):
        self.url = url
        self.headers = headers

    def get(self, path: str, query: dict = None, headers: dict = None):
        response = requests.get(
            f"{self.url}{path}",
            headers=headers if headers else self.headers,
            params=query,
        )

        return response

    def post(
        self, path: str, body: dict = None, headers: dict = None, data: dict = None
    ):
        response = requests.post(
            f"{self.url}{path}",
            headers=headers if headers else self.headers,
            json=body,
            data=data,
        )

        return response

    def patch(self, path: str, body: dict = None, headers: dict = None):
        response = requests.patch(
            f"{self.url}{path}",
            headers=headers if headers else self.headers,
            json=body,
        )

        return response

    def put(self, path: str, body: dict = None, headers: dict = None):
        response = requests.put(
            f"{self.url}{path}",
            headers=headers if headers else self.headers,
            json=body,
        )

        return response

    def delete(self, path: str, headers: dict = None):
        response = requests.delete(
            f"{self.url}{path}",
            headers=headers if headers else self.headers,
        )

        return response
