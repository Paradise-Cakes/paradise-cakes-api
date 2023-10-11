from mangum import Mangum
from fastapi import FastAPI
from src.routes import hello

app = FastAPI(title="Paradise Cakes API", version="1.0.0", root_path="/v1")


app.include_router(hello.router)


def lambda_handler(event, context):
    handler = Mangum(app, lifespan="on", api_gateway_base_path="/v1")
    return handler(event, context)
