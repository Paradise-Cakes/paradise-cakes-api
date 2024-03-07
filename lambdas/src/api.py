from mangum import Mangum
from fastapi import FastAPI
from src.routes import hello, get_desserts

app = FastAPI(title="Paradise Cakes API", version="1.0.0", root_path="/v1")

origins = [
    "http://localhost*
    "https://paradisecakesbymegan.com/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(hello.router)
app.include_router(get_desserts.router)

def lambda_handler(event, context):
    handler = Mangum(app, lifespan="on", api_gateway_base_path="/v1")
    return handler(event, context)
