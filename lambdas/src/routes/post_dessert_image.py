import os
import arrow
import boto3
import uuid
from fastapi import APIRouter, Request
from aws_lambda_powertools import Logger
from src.lib.response import fastapi_gateway_response
from src.models import DessertImage
from src.models.base import Base
from src.lib.dynamodb import DynamoConnection


logger = Logger()
router = APIRouter()

dessert_images_table = DynamoConnection(
    os.environ.get("DYNAMODB_REGION", "us-east-1"),
    os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    os.environ.get("DYNAMODB_DESSERT_IMAGES_TABLE_NAME", "dessert_images"),
).table


class CreateDessertImageRequest(Base):
    name: str
    position: int


class CreateDessertImageResponse(DessertImage):
    upload_url: str


@logger.inject_lambda_context(log_event=True)
@router.post(
    "/desserts/{dessert_id}/images",
    status_code=201,
    response_model=CreateDessertImageResponse,
)
def create_image(request: Request, dessert_id: str, body: CreateDessertImageRequest):
    logger.info(f"Creating new image for dessert: {dessert_id}")

    image_id = uuid.uuid4()
    created_at = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ss")
    last_updated_at = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ss")

    new_image = DessertImage(
        **body.clean(),
        image_id=image_id,
        dessert_id=dessert_id,
        created_at=created_at,
        last_updated_at=last_updated_at,
    )

    dessert_images_table.put_item(Item={**new_image.clean()})

    def generate_presigned_url(img):
        bucket = os.environ.get("DESSERT_IMAGES_BUCKET_NAME")
        s3_client = boto3.client("s3")
        upload_url = s3_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket, "Key": f"{img.dessert_id}/{img.image_id}"},
            ExpiresIn=3600,
        )
        return upload_url

    logger.info(f"Created new image for dessert: {new_image}")
    response = CreateDessertImageResponse(
        **new_image.model_dump(), upload_url=generate_presigned_url(new_image)
    )
    return fastapi_gateway_response(201, {}, response.clean())
