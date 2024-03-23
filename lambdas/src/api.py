from mangum import Mangum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import get_desserts, get_dessert, get_orders, post_order

app = FastAPI(title="Paradise Cakes API", version="1.0.0", root_path="/v1")

origins = ["http://localhost:5173", "https://paradisecakesbymegan.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(get_desserts.router)
app.include_router(get_dessert.router)
app.include_router(get_orders.router)
app.include_router(post_order.router)


def lambda_handler(event, context):
    handler = Mangum(app, lifespan="on", api_gateway_base_path="/v1")
    return handler(event, context)
