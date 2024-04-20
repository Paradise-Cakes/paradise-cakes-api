import os
import arrow
import boto3
import uuid
from fastapi import APIRouter, Request, File, UploadFile, Form, HTTPException
from aws_lambda_powertools import Logger
from src.lib.response import fastapi_gateway_response
from src.models import DessertImage
from src.models.base import Base
from src.lib.dynamodb import DynamoConnection


logger = Logger()
router = APIRouter()
s3_client = boto3.client("s3")


dessert_images_table = DynamoConnection(
    os.environ.get("DYNAMODB_REGION", "us-east-1"),
    os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    os.environ.get("DYNAMODB_DESSERT_IMAGES_TABLE_NAME", "dessert_images"),
).table


class postDessertImageRequest(Base):
    position: int
    file_extension: str


class PostDessertImageResponse(DessertImage):
    upload_url: str


@logger.inject_lambda_context(log_event=True)
@router.post(
    "/desserts/{dessert_id}/images",
    status_code=201,
    response_model=PostDessertImageResponse,
)
def post_dessert_image(
    request: Request,
    body: postDessertImageRequest,
    dessert_id: str,
):
    logger.info(f"Creating new image for dessert: {dessert_id}")

    def upload_url(dessert_image):
        bucket_name = os.environ.get("DESSERT_IMAGES_BUCKET_NAME")
        upload_url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": bucket_name,
                "Key": "/".join([dessert_image.dessert_id, dessert_image.image_id]),
                "ContentType": f"{dessert_image.file_extension}",
            },
            ExpiresIn=60 * 60 * 24,
        )
        return upload_url

    image_id = str(uuid.uuid4())

    # calculate the object url
    object_url = f"https://{os.environ.get('DESSERT_IMAGES_BUCKET_NAME')}.s3.amazonaws.com/{dessert_id}/{image_id}"

    new_dessert_image = DessertImage(
        image_id=image_id,
        dessert_id=dessert_id,
        position=body.position,
        created_at=int(arrow.utcnow().timestamp()),
        last_updated_at=int(arrow.utcnow().timestamp()),
        file_extension=body.file_extension,
        url=object_url,
    )

    # storing the image metadata
    dessert_images_table.put_item(Item=new_dessert_image.clean())

    logger.info(f"Created new dessert image: {new_dessert_image.image_id}")
    response = PostDessertImageResponse(
        **new_dessert_image.model_dump(), upload_url=upload_url(new_dessert_image)
    )
    return fastapi_gateway_response(200, {}, response.clean())
