from fastapi.responses import JSONResponse
import simplejson


def fastapi_gateway_response(
    httpStatusCode: int = 200, headers: dict = {}, body: dict = {}
):
    headers.setdefault("content-type", "application/json")
    headers.setdefault("access-control-allow-headers", "Content-Type")
    headers.setdefault("access-control-allow-origin", "*")
    headers.setdefault(
        "access-control-allow-methods", "OPTIONS,POST,PUT,PATCH,GET,DELETE"
    )

    return JSONResponse(
        status_code=httpStatusCode,
        content=simplejson.dumps(body),
        headers=headers,
    )
