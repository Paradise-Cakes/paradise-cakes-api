from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/hello",
    status_code=200,
)
def hello_message():
    return {"Greeting": "hello there"}
