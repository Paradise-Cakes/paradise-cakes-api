from mangum import Mangum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import (
    get_desserts,
    get_dessert,
    get_orders,
    post_order,
    post_signup,
    post_signin,
    post_confirm_signup,
    post_resend_confirmation_code,
    post_forgot_password,
    post_logout,
    post_dessert,
    post_dessert_image,
    patch_dessert,
    delete_dessert,
    get_display_images,
)

app = FastAPI(title="Paradise Cakes API", version="1.0.0", root_path="/v1")

origins = [
    "http://localhost:5173",
    "https://megsparadisecakes.com",
    "https://www.megsparadisecakes.com",
    "https://dev.megsparadisecakes.com",
    "https://www.dev.megsparadisecakes.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(get_desserts.router)
app.include_router(get_dessert.router)
app.include_router(get_orders.router)
app.include_router(post_order.router)
app.include_router(post_signup.router)
app.include_router(post_signin.router)
app.include_router(post_confirm_signup.router)
app.include_router(post_resend_confirmation_code.router)
app.include_router(post_forgot_password.router)
app.include_router(post_logout.router)
app.include_router(post_dessert.router)
app.include_router(post_dessert_image.router)
app.include_router(patch_dessert.router)
app.include_router(delete_dessert.router)
app.include_router(get_display_images.router)


def lambda_handler(event, context):
    handler = Mangum(app, lifespan="on", api_gateway_base_path="/v1")
    return handler(event, context)
