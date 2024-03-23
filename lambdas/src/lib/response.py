from fastapi.responses import JSONResponse
from decimal import Decimal


def fastapi_gateway_response(
    httpStatusCode: int = 200, headers: dict = {}, body: dict = {}
):
    headers.setdefault("content-type", "application/json")
    headers.setdefault("access-control-allow-headers", "Content-Type")
    headers.setdefault("access-control-allow-origin", "*")
    headers.setdefault(
        "access-control-allow-methods", "OPTIONS,POST,PUT,PATCH,GET,DELETE"
    )

    if type(body) is list:
        for item in body:
            if "order_total" in item:
                item["order_total"] = float(item["order_total"])

    if "order_total" in body:
        body["order_total"] = float(body["order_total"])

    return JSONResponse(
        status_code=httpStatusCode,
        content=body,
        headers=headers,
    )
